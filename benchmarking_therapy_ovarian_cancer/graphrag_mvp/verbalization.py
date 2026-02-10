from typing import List, Dict, Any
from .knowledge_graph import KG

def verbalize_subgraph_from_anchor(kg: KG, pid: str, anchor) -> str:
    if not anchor:
        return "Kein Anchor gefunden."
    a_name, a_kind, a_depth, a_phase = anchor["name"], anchor["kind"], anchor["depth"], anchor["phase"]

    # Anchor
    q_anchor_facts = """
    MATCH (a:Step {name:$anchor})-[:PROVIDES_FACT]->(fk:FactKey)
    OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
    RETURN fk.key AS key, head([v IN collect(pf.value) WHERE v IS NOT NULL]) AS patient_value
    """
    af_rows = kg.run_list(q_anchor_facts, pid=pid, anchor=a_name)
    anchor_fact_vals = {r["key"]: r["patient_value"] for r in af_rows if r["key"]}

    # NEXT-Schritte ab Anchor (REQUIRES, not completed)
    q_next = """
    MATCH (p:Patient {pid:$pid})
    MATCH (a:Step {name:$anchor})-[:NEXT]->(n:Step)
    OPTIONAL MATCH (n)-[rq:REQUIRES_FACT]->(fkReq:FactKey)
    WITH p, n,
         [r IN collect(CASE WHEN fkReq IS NULL THEN NULL ELSE {k: fkReq.key, v: rq.value} END)
          WHERE r IS NOT NULL] AS reqs
    WITH p, n,
         (CASE WHEN size(reqs)=0 THEN true ELSE ALL (r IN reqs WHERE EXISTS {
            MATCH (p)-[:HAS_FACT]->(pf)-[:OF_KEY]->(:FactKey {key:r.k})
            WHERE pf.value = r.v
         }) END) AS requires_ok
    WHERE requires_ok AND NOT (p)-[:COMPLETED]->(n)
    RETURN n.name AS name, n.kind AS kind
    ORDER BY kind DESC, name ASC
    """
    next_rows = kg.run_list(q_next, pid=pid, anchor=a_name)

    def get_requires(step: str) -> List[Dict[str, Any]]:
        q = """
        MATCH (n:Step {name:$name})
        OPTIONAL MATCH (n)-[rq:REQUIRES_FACT]->(fk:FactKey)
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
        RETURN fk.key AS key, rq.value AS needed, pf.value AS have
        """
        rows = kg.run_list(q, pid=pid, name=step)
        return [dict(key=r["key"], needed=r["needed"], have=r["have"]) for r in rows if r["key"]]

    def get_needs_with_providers(step: str) -> List[Dict[str, Any]]:
        q = """
        MATCH (n:Step {name:$name})-[:NEEDS_FACT]->(fk:FactKey)
        OPTIONAL MATCH (prov:Step)-[:PROVIDES_FACT]->(fk)
        WITH fk, collect(DISTINCT prov) AS provs
        UNWIND (CASE WHEN size(provs)=0 THEN [NULL] ELSE provs END) AS prov
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:COMPLETED]->(prov)
        WITH fk, prov, CASE WHEN prov IS NULL THEN 0 ELSE count(*) END AS c_done
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:PERFORMED]->(prov)
        WITH fk, prov, c_done, CASE WHEN prov IS NULL THEN 0 ELSE count(*) END AS c_perf
        WITH fk, prov,
             CASE
               WHEN prov IS NULL THEN 'none'
               WHEN c_done > 0 THEN 'completed'
               WHEN c_perf > 0 THEN 'performed'
               ELSE 'none'
             END AS status
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
        WITH fk, collect(DISTINCT {provider: coalesce(prov.name,'<kein Provider modelliert>'), status: status}) AS providers,
             head([v IN collect(pf.value) WHERE v IS NOT NULL]) AS patient_value
        RETURN fk.key AS key, providers, patient_value
        ORDER BY key
        """
        rows = kg.run_list(q, pid=pid, name=step)
        cleaned = []
        for r in rows:
            seen, provs = set(), []
            for pinfo in r["providers"]:
                tup = (pinfo["provider"], pinfo["status"])
                if tup not in seen:
                    provs.append(pinfo)
                    seen.add(tup)
            cleaned.append(dict(key=r["key"], providers=provs, patient_value=r["patient_value"]))
        return cleaned

    q_anchor_prov = """
    MATCH (a:Step {name:$anchor})-[:PROVIDES_FACT]->(fk:FactKey)
    OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
    OPTIONAL MATCH (needStep:Step)-[:NEEDS_FACT]->(fk)
    OPTIONAL MATCH (reqStep:Step)-[rq:REQUIRES_FACT]->(fk)
    WITH fk,
         head([v IN collect(pf.value) WHERE v IS NOT NULL]) AS patient_value,
         collect(DISTINCT needStep.name) AS needs_cons,
         collect(DISTINCT reqStep.name) AS req_cons
    RETURN fk.key AS key, patient_value, needs_cons, req_cons
    ORDER BY key
    """
    ap_rows = kg.run_list(q_anchor_prov, pid=pid, anchor=a_name)

    out: List[str] = []
    out.append(f"Anchor: {a_name}  (Typ: {a_kind}, Phase: {a_phase}, Tiefe: {a_depth})")
    out.append("→ Repräsentiert den aktuell fachlich weitesten abgeschlossenen Knoten im Pfad.\n")

    if not next_rows:
        out.append("Keine direkten nächsten Schritte (NEXT-Schritte) (entweder REQUIRES nicht erfüllt oder bereits abgeschlossen).\n")
    else:
        out.append("Direkten nächste Schritte (NEXT-Schritte) (REQUIRES erfüllt, noch nicht abgeschlossen):")
        for nr in next_rows:
            n_name, n_kind = nr["name"], nr["kind"]
            out.append(f"• {n_name} [{n_kind}] — ausführbar: alle Gate-Bedingungen erfüllt.")

            # REQUIRES
            reqs = get_requires(n_name)
            if reqs:
                out.append("Spezifischer Wert von Fakt benötigt (REQUIRES_FACT, benötigte Zielwerte, bereits erfüllt):")
                for r in reqs:
                    have = r["have"]
                    have_str = "nicht vorhanden" if have is None else f"{have}"
                    suffix = "erfüllt" if have is not None and str(have) == str(
                        r["needed"]) else "(Istwert abweichend/nicht gesetzt)"
                    out.append(f"    – {r['key']} muss '{r['needed']}' sein (Patient: {have_str}) {suffix}")
            else:
                out.append("  Kein spezifischer Wert von Fakt benötigt (keine Gate-Bedingungen definiert)")

            # NEEDS
            needs = get_needs_with_providers(n_name)
            if needs:
                out.append("  Benötigte Fakten (NEEDS_FACT) und mögliche Lieferanten:")
                for n in needs:
                    pval = n["patient_value"]
                    pval_str = "" if pval in (None, "unknown") else f" | "
                    provs = ", ".join([f"{p['provider']} [{p['status']}]" for p in n["providers"]]) or "—"
                    out.append(f"    – {n['key']}: Provider → {provs}{pval_str}")
                    if pval in (None, "unknown"):
                        out.append(f"       ⤷ Hinweis: Wert fehlt/unklar. Provider step {provs} muss zunächst durchgeführt werden um {pval} zu ermitteln.")
                    else:
                        out.append(f"       ⤷ Hinweis: Wert vorhanden; der Schritt kann diesen Bedarf bereits decken/prüfen, ermittelter Patientenwert ist {pval}.")
            else:
                out.append("  Benötigte Fakten (NEEDS_FACT): — (keine zusätzlichen Datenanforderungen)")
            out.append("")

    if not ap_rows:
        out.append("Vom Anchor gelieferte Fakten: —")
    else:
        out.append("Vom Anchor gelieferte Fakten (Patientenwert & Konsumenten):")
        for r in ap_rows:
            pval = r["patient_value"]
            pval_str = "unbekannt" if pval is None else f"{pval}"
            needs_cons = ", ".join([c for c in r["needs_cons"] if c]) or "—"
            req_cons   = ", ".join([c for c in r["req_cons"] if c]) or "—"
            out.append(f"• {r['key']}: Patient = {pval_str} → genutzt von NEEDS: {needs_cons} | REQUIRES: {req_cons}")

    return "\n".join(out)
