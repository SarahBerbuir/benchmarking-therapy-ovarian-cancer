from typing import List, Dict, Any, Optional, Tuple
from .knowledge_graph import KG
from graph_cypher.cypher_graph.definitions import definitions

ROUTE_PREFIX = "route_"
PARALLEL_JOIN_NAME = "Parallel Join"  # ggf. anpassen


def verbalize_subgraph_from_anchor(kg: KG, pid: str, anchor) -> str:
    if not anchor:
        return "Kein Anchor gefunden."
    a_name, a_kind, a_depth, a_phase = anchor["name"], anchor["kind"], anchor["depth"], anchor["phase"]

    # ---------- kleine Helfer ----------

    def _step_def(name: str) -> Optional[str]:
        return (definitions.get("steps") or {}).get(name) or None

    def _fact_def(key: str) -> Optional[str]:
        return (definitions.get("facts") or {}).get(key) or None

    def _fmt_step(name: str, with_defs: bool = True) -> str:
        d = _step_def(name) if with_defs else None
        return f"{name} — {d}" if d else name

    def _fmt_fact(key: str, with_defs: bool = True) -> str:
        d = _fact_def(key) if with_defs else None
        # kurze, schlanke Darstellung
        return f"{key} ({d})" if d else key

    def _fmt_have(v: Any) -> str:
        return "fehlt" if v is None else f"'{v}'"

    def is_routing_step(name: str) -> bool:
        row = kg._run_one("MATCH (s:Step {name:$n}) RETURN 'Routing' IN labels(s) AS is_routing", n=name)
        return bool(row and row["is_routing"])

    def routing_child(name: str) -> Optional[str]:
        rows = kg.run_list("MATCH (:Step {name:$n})-[:NEXT]->(c:Step) RETURN c.name AS child", n=name)
        if not rows:
            return None
        return sorted(r["child"] for r in rows)[0]

    def routing_children(name: str) -> List[str]:
        rows = kg.run_list("MATCH (:Step {name:$n})-[:NEXT]->(c:Step) RETURN c.name AS child", n=name)
        return sorted(r["child"] for r in rows)

    def routing_parent(name: str) -> Optional[str]:
        rows = kg.run_list("MATCH (p:Step)-[:NEXT]->(:Step {name:$n}) RETURN p.name AS parent", n=name)
        if not rows:
            return None
        # deterministisch
        return rows[0]["parent"] if len(rows) == 1 else sorted(r["parent"] for r in rows)[0]

    def get_requires(pid_: str, step: str, include_route: bool = False) -> List[Dict[str, Any]]:
        q = """
        MATCH (n:Step {name:$name})-[rq:REQUIRES_FACT]->(fk:FactKey)
        WHERE $includeRoute OR NOT fk.key STARTS WITH $routePrefix
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
        RETURN fk.key AS key, rq.value AS needed, pf.value AS have
        ORDER BY key
        """
        return kg.run_list(q, pid=pid_, name=step, includeRoute=include_route, routePrefix=ROUTE_PREFIX)

    def anchor_conflicts_with_requires(reqs_nonroute: List[Dict[str, Any]], anchor_vals: Dict[str, Any]) -> bool:
        # TRUE, wenn ein benötigter (nicht-route) Fakt bereits am Anchor auf einen ABWEICHENDEN Wert gesetzt ist
        for r in reqs_nonroute:
            k, need = r["key"], r["needed"]
            if k in anchor_vals and anchor_vals[k] is not None and str(anchor_vals[k]) != str(need):
                return True
        return False

    def resolve_effective_display_for_router(router_name: str, anchor_vals: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
        """
        Rückgabe:
          - display_name: anzuzeigender Downstream-Schritt (nicht der Router selbst)
          - route_ok:   erfüllte route_* Gates (rein informativ)
          - route_missing: offene route_* Gates (rein informativ)

        Spezialfall Parallel Join:
          - wählt den kompatiblen Downstream-Router anhand der Anchor-Werte (z. B. next_step_system_therapy)
          - zeigt dessen Kind als display_name
        """
        # 1) Router-Gates (route_*) bewerten
        rqs_route = [r for r in get_requires(pid, router_name, include_route=True)
                     if str(r["key"]).startswith(ROUTE_PREFIX)]
        route_ok, route_missing = [], []
        for r in rqs_route:
            have = r["have"]
            if have is not None and str(have) == str(r["needed"]):
                route_ok.append(f"{r['key']}='{r['needed']}'")
            else:
                route_missing.append(f"{r['key']} benötigt '{r['needed']}' (aktuell {_fmt_have(have)})")

        # 2) Normale Router: direkt ihr einziges Kind
        if router_name != PARALLEL_JOIN_NAME:
            child = routing_child(router_name)
            return (child or router_name), route_ok, route_missing

        # 3) Parallel Join: Kind-Router prüfen, die mit Anchor kompatibel sind
        candidates = routing_children(router_name)
        compatible_targets: List[str] = []
        for cand in candidates:
            reqs_nonroute = get_requires(pid, cand, include_route=False)
            if not anchor_conflicts_with_requires(reqs_nonroute, anchor_vals):
                tgt_child = routing_child(cand) or cand
                compatible_targets.append(tgt_child)

        display = compatible_targets[0] if compatible_targets else (routing_child(router_name) or router_name)
        return display, route_ok, route_missing

    def next_steps_respecting_requires(pid_: str, anchor_name: str) -> List[Dict[str, Any]]:
        # Direkte NEXT ab Anchor; nur Steps, deren REQUIRES (alle) bereits beim Patienten erfüllt sind; noch nicht completed
        q = """
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
        RETURN n.name AS name, n.kind AS kind, labels(n) AS labels
        ORDER BY kind DESC, name ASC
        """
        return kg.run_list(q, pid=pid_, anchor=anchor_name)

    def anchor_fact_values(pid_: str, anchor_name: str) -> Dict[str, Any]:
        q = """
        MATCH (a:Step {name:$anchor})-[:PROVIDES_FACT]->(fk:FactKey)
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
        RETURN fk.key AS key, head([v IN collect(pf.value) WHERE v IS NOT NULL]) AS patient_value
        """
        rows_ = kg.run_list(q, pid=pid_, anchor=anchor_name)
        return {r["key"]: r["patient_value"] for r in rows_ if r["key"]}

    def anchor_provides_nonroute(pid_: str, anchor_name: str) -> List[Dict[str, Any]]:
        q = """
        MATCH (a:Step {name:$anchor})-[:PROVIDES_FACT]->(fk:FactKey)
        WHERE NOT fk.key STARTS WITH $routePrefix
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
        return kg.run_list(q, pid=pid_, anchor=anchor_name, routePrefix=ROUTE_PREFIX)

    def get_needs_with_providers(pid_: str, step: str) -> List[Dict[str, Any]]:
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
        WITH fk, collect(DISTINCT {provider: coalesce(prov.name,'<kein Provider modelliert>'),
                                   status: status}) AS providers,
             head([v IN collect(pf.value) WHERE v IS NOT NULL]) AS patient_value
        RETURN fk.key AS key, providers, patient_value
        ORDER BY key
        """
        rows_ = kg.run_list(q, pid=pid_, name=step)
        cleaned_: List[Dict[str, Any]] = []
        for r in rows_:
            seen, provs = set(), []
            for pinfo in r["providers"]:
                tup = (pinfo["provider"], pinfo["status"])
                if tup not in seen:
                    provs.append(pinfo)
                    seen.add(tup)
            cleaned_.append(dict(key=r["key"], providers=provs, patient_value=r["patient_value"]))
        return cleaned_

    def get_provides_nonroute(pid_: str, step: str) -> List[Dict[str, Any]]:
        q = """
        MATCH (s:Step {name:$name})-[:PROVIDES_FACT]->(fk:FactKey)
        WHERE NOT fk.key STARTS WITH $routePrefix
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
        RETURN fk.key AS key, head([v IN collect(pf.value) WHERE v IS NOT NULL]) AS patient_value
        ORDER BY key
        """
        return kg.run_list(q, pid=pid_, name=step, routePrefix=ROUTE_PREFIX)

    def _summarize_parallel_join_requirements(pid_: str, anchor_vals_: Dict[str, Any]) -> List[str]:
        """
        Erklärt:
          – Welche Parallel-Gates (route_*) am Parallel Join erfüllt/offen sind
          – Welche **Fakten** der Parallel Join selbst (NEEDS_FACT) benötigt, inkl. Provider + Status,
            und welche davon fehlen bzw. schon vorhanden sind
          – Welche Zielspur mit den Anchor-Werten kompatibel ist
          – Für diese Zielspur: welche NEEDS-Fakten fehlen / welche Provider sie liefern
        """
        lines: List[str] = []

        # 1) Router-Gates direkt am Parallel Join (z. B. route_system_therapy_done, parallel_done ...)
        pj_route_ok: List[str] = []
        pj_route_missing: List[str] = []
        rqs_pj = [r for r in get_requires(pid_, PARALLEL_JOIN_NAME, include_route=True)
                  if str(r["key"]).startswith(ROUTE_PREFIX)]
        for r in rqs_pj:
            have = r["have"]
            if have is not None and str(have) == str(r["needed"]):
                pj_route_ok.append(f"{r['key']}='{r['needed']}'")
            else:
                have_str = "fehlt" if have is None else f"'{have}'"
                pj_route_missing.append(f"{r['key']} benötigt '{r['needed']}' (aktuell {have_str})")

        gates_info = []
        if pj_route_ok:
            gates_info.append("erfüllt: " + ", ".join(pj_route_ok))
        if pj_route_missing:
            gates_info.append("offen: " + "; ".join(pj_route_missing))
        gates_txt = " | ".join(gates_info) if gates_info else "—"
        lines.append(f"Parallelfluss: Erforderliche Parallel-Gates → {gates_txt}")

        # 2) Faktenanforderungen AM PARALLEL JOIN selbst (NEEDS_FACT)
        needs_pj = get_needs_with_providers(pid_, PARALLEL_JOIN_NAME)
        if needs_pj:
            lines.append("Faktenanforderungen am Parallel Join (NEEDS_FACT) & Provider:")
            missing_provider_names: List[str] = []
            for n in needs_pj:
                key = n["key"]
                pval = n["patient_value"]
                provs = n["providers"]  # [{provider, status}, ...]
                provs_txt = ", ".join([f"{p['provider']} [{p['status']}]" for p in provs]) or "—"
                if pval in (None, "unknown"):
                    lines.append(f"  · {key}: Wert fehlt/unklar → mögliche Provider: {provs_txt}")
                    for pinfo in provs:
                        if pinfo["status"] != "completed" and pinfo["provider"] and pinfo["provider"] != "<kein Provider modelliert>":
                            missing_provider_names.append(pinfo["provider"])
                else:
                    lines.append(f"  · {key}: vorhandener Patientenwert = '{pval}' → Provider: {provs_txt}")
            # Handlungsfokus am Parallel Join
            missing_provider_names = sorted(set(missing_provider_names))
            if missing_provider_names:
                lines.append("Handlungsfokus (Parallel Join): führe offene Provider-Schritte aus, z. B.: " +
                             ", ".join(missing_provider_names))
            else:
                lines.append("Alle am Parallel Join benötigten Provider sind bereits abgeschlossen oder haben Werte geliefert.")
        else:
            lines.append("Der Parallel Join hat keine eigenen NEEDS_FACT.")

        # 3) Kompatible Downstream-Zielspur bestimmen (anhand Anchor-Werte)
        children = routing_children(PARALLEL_JOIN_NAME)
        compatible: List[str] = []
        for cand_router in children:
            reqs_nonroute = get_requires(pid_, cand_router, include_route=False)
            if not anchor_conflicts_with_requires(reqs_nonroute, anchor_vals_):
                tgt = routing_child(cand_router) or cand_router
                compatible.append(tgt)

        if compatible:
            primary_target = compatible[0]
            lines.append(
                f"Kompatible Zielspur nach Parallelabschluss: {_fmt_step(primary_target)}")

            needs_target = get_needs_with_providers(pid_, primary_target)
            if needs_target:
                lines.append("Benötigte Fakten und Provider für den Zielschritt nach Parallelabschluss:")
                missing_providers_target: List[str] = []
                for n in needs_target:
                    key = n["key"]
                    pval = n["patient_value"]
                    provs = n["providers"]
                    provs_txt = ", ".join([f"{p['provider']} [{p['status']}]" for p in provs]) or "—"
                    if pval in (None, "unknown"):
                        lines.append(
                            f"  · {_fmt_fact(key)}: Wert fehlt/unklar → mögliche Provider: {provs_txt}")
                        for pinfo in provs:
                            if pinfo["status"] != "completed" and pinfo["provider"] and pinfo["provider"] != "<kein Provider modelliert>":
                                missing_providers_target.append(pinfo["provider"])
                    else:
                        lines.append(
                            f"  · {_fmt_fact(key)}: vorhandener Patientenwert = '{pval}' → Provider: {provs_txt}")
                missing_providers_target = sorted(set(missing_providers_target))
                if missing_providers_target:
                    lines.append("Handlungsfokus (Zielschritt): fehlende Provider-Schritte priorisieren, z. B.: " +
                                 ", ".join(missing_providers_target))
                else:
                    lines.append("Für den Zielschritt sind alle benötigten Provider bereits abgeschlossen oder es liegen Werte vor.")
            else:
                lines.append("Der Zielschritt meldet keine zusätzlichen NEEDS_FACT.")
        else:
            lines.append("Hinweis: Aktuell keine mit den Anchor-Werten kompatible Zielspur vom Parallel Join gefunden.")

        return lines

    # ---------- Anchor & Kontext ----------
    anchor_vals = anchor_fact_values(pid, a_name)
    ap_rows = anchor_provides_nonroute(pid, a_name)

    out: List[str] = []
    out.append(
        f"Anchor: {_fmt_step(a_name)}  (Typ: {a_kind}, Phase: {a_phase}, Tiefe: {a_depth})")
    out.append("→ Fachlich aktuell weitester abgeschlossener Schritt im Pfad.\n")

    # Routing-Hinweis am Anchor
    if is_routing_step(a_name):
        par = routing_parent(a_name)
        if par:
            out.append(f"Anchor ist ein Routing-Knoten. Zulieferer (direkter Vorgänger): {_fmt_step(par)}.")
        ch = routing_child(a_name)
        if ch:
            out.append(f"Geroutetes Ziel (Downstream-Schritt): {_fmt_step(ch)}.\n")

    # ---------- NEXT-Schritte (Routing-aware) ----------
    next_rows = next_steps_respecting_requires(pid, a_name)
    if not next_rows:
        out.append("Keine direkten nächsten Schritte (NEXT) mit erfüllten REQUIRES (oder bereits abgeschlossen).\n")
    else:
        out.append("Direkte nächste Schritte (REQUIRES erfüllt, noch nicht abgeschlossen):")
        for nr in next_rows:
            n_name, n_kind, n_labels = nr["name"], nr["kind"], nr["labels"] or []
            is_router = "Routing" in n_labels

            # Effektives Ziel + Router-Gates
            if is_router:
                display_name, route_ok, route_missing = resolve_effective_display_for_router(n_name, anchor_vals)
                effective = display_name
                router_note = " (über Routing)"
            else:
                reqs_nonroute = get_requires(pid, n_name, include_route=False)
                if anchor_conflicts_with_requires(reqs_nonroute, anchor_vals):
                    # z. B. Maintenance-Mapping rausfiltern, wenn Anchor already 'Nachsorge'
                    continue
                display_name = n_name
                effective = n_name
                route_ok, route_missing = [], []
                router_note = ""

            display_txt = _fmt_step(display_name)
            out.append(f"• {display_txt}{router_note} [{n_kind}] — ausführbar: REQUIRES erfüllt.")

            # Router-Gates (Info)
            if route_ok:
                pretty = []
                for r in route_ok:
                    k = r.split("=")[0].strip()
                    pretty.append(r.replace(k, _fmt_fact(k)))
                out.append("   – Routing-Gates erfüllt: " + ", ".join(pretty))

            if route_missing:
                pretty_miss = []
                for r in route_missing:
                    parts = r.split(" benötigt ")
                    k = parts[0].strip()
                    pretty_miss.append(r.replace(k, _fmt_fact(k)))
                out.append("   – Routing-Gates fehlen: " + "; ".join(pretty_miss))

            # REQUIRES des effektiven Zielschritts (ohne route_*)
            reqs_nonroute_eff = get_requires(pid, effective, include_route=False)
            if reqs_nonroute_eff:
                out.append("   – Wert-Gates (REQUIRES_FACT) des Zielschritts:")
                for r in reqs_nonroute_eff:
                    key_txt = _fmt_fact(r['key'])
                    have = r["have"]
                    status = "✓ erfüllt" if have is not None and str(have) == str(
                        r["needed"]) else "✗ abweichend/fehlt"
                    out.append(f"      · {key_txt} muss '{r['needed']}' sein (Patient: {_fmt_have(have)}) {status}")

            else:
                out.append("   – Keine Wert-Gates (REQUIRES_FACT) beim Zielschritt.")

            # NEEDS + Provider
            needs = get_needs_with_providers(pid, effective)
            if needs:
                out.append("   – Benötigte Fakten (NEEDS_FACT) & mögliche Provider:")
                for n in needs:
                    key_txt = _fmt_fact(n['key'])
                    pval = n["patient_value"]
                    provs_txt = ", ".join([f"{p['provider']} [{p['status']}]" for p in n["providers"]]) or "—"
                    if pval in (None, "unknown"):
                        out.append(f"      · {key_txt}: Wert fehlt/unklar → Provider: {provs_txt}")
                        out.append(
                            f"         ⇒ Aktion: Einen Provider-Schritt durchführen, um '{key_txt}' zu bestimmen.")
                    else:
                        out.append(f"      · {key_txt}: vorhandener Patientenwert = '{pval}' → Provider: {provs_txt}")
            else:
                out.append("   – Keine zusätzlichen Datenanforderungen (NEEDS_FACT).")

            # PROV des Zielschritts (ohne route_*)
            provs = get_provides_nonroute(pid, effective)
            if provs:
                out.append("   – Liefert bei Durchführung (PROVIDES_FACT, ohne Routing-Flags):")
                for pr in provs:
                    key_txt = _fmt_fact(pr['key'])
                    current = _fmt_have(pr["patient_value"]).replace("fehlt", "—")
                    out.append(f"      · {key_txt} (Patient aktuell: {current})")

            out.append("")

        # Zusatztext speziell für Parallel Join: Gates + NEEDS + fehlende Provider + erwartetes Ziel
        pj_in_next = any(
            nr["name"] == PARALLEL_JOIN_NAME or ("Routing" in (nr["labels"] or []) and nr["name"] == PARALLEL_JOIN_NAME)
            for nr in next_rows
        )
        if pj_in_next:
            out.extend(_summarize_parallel_join_requirements(pid, anchor_vals))
            out.append("")  # optische Trennung

    # ---------- Anchor liefert (ohne route_*) ----------
    if not ap_rows:
        out.append("Vom Anchor gelieferte Fakten: —")
    else:
        out.append("Vom Anchor gelieferte Fakten (Patientenwert & Konsumenten):")
        for r in ap_rows:
            key_txt = _fmt_fact(r['key'])
            pval = r["patient_value"]
            pval_str = "unbekannt" if pval is None else f"'{pval}'"
            needs_cons = ", ".join([_fmt_step(c) for c in r["needs_cons"] if c]) or "—"
            req_cons = ", ".join([_fmt_step(c) for c in r["req_cons"] if c]) or "—"
            out.append(f"• {key_txt}: Patient = {pval_str} → genutzt von NEEDS: {needs_cons} | REQUIRES: {req_cons}")
    return "\n".join(out)
