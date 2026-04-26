from typing import List, Dict, Any, Optional, Tuple

from .graph_cypher.cypher_graph.definitions import definitions
from .graph_cypher.cypher_graph.names_nodes import names
from .knowledge_graph import KG

ROUTE_PREFIX = "route_"
PARALLEL_JOIN_NAME = "Parallel Join"
SHOW_KEYS = False

# ── Labeling ──

def _step_def(name: str) -> Optional[str]:
    return (definitions.get("steps") or {}).get(name) or None

def _fact_def(key: str) -> Optional[str]:
    return (definitions.get("facts") or {}).get(key) or None

def _label_step(name: str) -> str:
    d = _step_def(name)
    return f"{name} ({d})" if d else name

def _label_fact(key: str) -> str:
    d = _fact_def(key)
    if d and SHOW_KEYS:
        return f"{d} [{key}]"
    return d or key

def _fmt_have(v: Any) -> str:
    return "nicht dokumentiert" if v is None else f"'{v}'"

def _is_actionable(kind: Optional[str]) -> bool:
    return (kind or "").lower() in {"diagnostic", "therapy", "info"}

def _is_evaluator(kind: Optional[str]) -> bool:
    return (kind or "").lower() == "evaluator"

def _is_unknown(v: Any) -> bool:
    return v is None or v == "unknown"

def _is_conflict(have: Any, need: Any) -> bool:
    return (not _is_unknown(have)) and (str(have) != str(need))

# ── Formatting helpers ──

def _section_header(title: str) -> str:
    return f"\n{'─' * 60}\n{title}\n{'─' * 60}"

def _step_type_label(kind: Optional[str]) -> str:
    k = (kind or "").lower()
    if k == "evaluator":
        return "Entscheidungspunkt"
    elif k == "diagnostic":
        return "Diagnostik"
    elif k == "therapy":
        return "Therapie"
    elif k == "info":
        return "Information"
    return "Schritt"

# ── Verbalization ──

def verbalize_subgraph_from_anchor(kg: KG, pid: str, anchor) -> str:
    if not anchor:
        return "Kein abgeschlossener Schritt dokumentiert.\nEmpfohlener erster Schritt: Gynäkologische Untersuchung und Sonografie."

    a_name = anchor["name"]
    a_kind = anchor["kind"]
    a_depth = anchor["depth"]
    a_phase = anchor["phase"]

    # ── Inner helper functions (queries) ── unchanged logic ──

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
        return rows[0]["parent"] if len(rows) == 1 else sorted(r["parent"] for r in rows)[0]

    def routing_parents(name: str) -> List[str]:
        rows = kg.run_list(
            "MATCH (p:Step)-[:NEXT]->(:Step {name:$n}) RETURN p.name AS parent, labels(p) AS labels",
            n=name
        )
        return sorted([r["parent"] for r in rows if "Routing" in (r.get("labels") or [])])

    def get_requires(pid_: str, step: str, include_route: bool = False) -> List[Dict[str, Any]]:
        q = """
        MATCH (n:Step {name:$name})-[rq:REQUIRES_FACT]->(fk:FactKey)
        WHERE $includeRoute OR NOT fk.key STARTS WITH $routePrefix
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
        RETURN fk.key AS key, rq.value AS needed, pf.value AS have
        ORDER BY key
        """
        return kg.run_list(q, pid=pid_, name=step, includeRoute=include_route, routePrefix=ROUTE_PREFIX)

    def eval_route_requires(pid_: str, step: str) -> Tuple[List[str], List[str]]:
        rqs_route = [r for r in get_requires(pid_, step, include_route=True) if str(r["key"]).startswith(ROUTE_PREFIX)]
        ok, missing = [], []
        for r in rqs_route:
            have = r["have"]
            if have is not None and str(have) == str(r["needed"]):
                ok.append(f"{r['key']}='{r['needed']}'")
            else:
                missing.append(f"{r['key']} benötigt '{r['needed']}' (aktuell {_fmt_have(have)})")
        return ok, missing

    def patient_fact_values(pid_: str) -> Dict[str, Any]:
        q = """
        MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk:FactKey)
        RETURN fk.key AS key, pf.value AS value
        """
        rows = kg.run_list(q, pid=pid_)
        return {r["key"]: r["value"] for r in rows if r.get("key")}

    def has_only_route_requires(pid_: str, step: str) -> bool:
        rqs_all = get_requires(pid_, step, include_route=True)
        if not rqs_all:
            return False
        return all(str(r["key"]).startswith(ROUTE_PREFIX) for r in rqs_all)

    def active_routing_parent(pid_: str, child: str, anchor_name: str) -> Optional[str]:
        if is_routing_step(anchor_name):
            hit = kg._run_one(
                "MATCH (:Step {name:$a})-[:NEXT]->(:Step {name:$c}) RETURN 1 AS ok",
                a=anchor_name, c=child
            )
            if hit:
                return anchor_name

        q = """
        MATCH (p:Patient {pid:$pid})
        MATCH (par:Step)-[:NEXT]->(c:Step {name:$child})
        WHERE 'Routing' IN labels(par)
        WITH par,
             CASE
               WHEN EXISTS { MATCH (p)-[:COMPLETED]->(par) } THEN 2
               WHEN EXISTS { MATCH (p)-[:PERFORMED]->(par) } THEN 1
               ELSE 0
             END AS score
        RETURN par.name AS parent, score
        ORDER BY score DESC, parent ASC
        """
        rows = kg.run_list(q, pid=pid_, child=child)
        if not rows:
            return None
        best = rows[0]["score"]
        if best == 0 and len(rows) > 1:
            return None
        return rows[0]["parent"]

    def conflicts_with_requires(reqs_nonroute: List[Dict[str, Any]], fact_vals: Dict[str, Any]) -> bool:
        for r in reqs_nonroute:
            k, need = r["key"], r["needed"]
            if k in fact_vals and fact_vals[k] is not None and str(fact_vals[k]) != str(need):
                return True
        return False

    def resolve_effective_display_for_router(router_name: str, fact_vals: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
        rqs_route = [r for r in get_requires(pid, router_name, include_route=True)
                     if str(r["key"]).startswith(ROUTE_PREFIX)]
        route_ok, route_missing = [], []
        for r in rqs_route:
            have = r["have"]
            if have is not None and str(have) == str(r["needed"]):
                route_ok.append(f"{r['key']}='{r['needed']}'")
            else:
                route_missing.append(f"{r['key']} benötigt '{r['needed']}' (aktuell {_fmt_have(have)})")

        if router_name != PARALLEL_JOIN_NAME:
            child = routing_child(router_name)
            return (child or router_name), route_ok, route_missing

        candidates = routing_children(router_name)
        compatible_targets: List[str] = []
        for cand in candidates:
            reqs_nonroute = get_requires(pid, cand, include_route=False)
            if not conflicts_with_requires(reqs_nonroute, fact_vals):
                tgt_child = routing_child(cand) or cand
                compatible_targets.append(tgt_child)

        display = compatible_targets[0] if compatible_targets else (routing_child(router_name) or router_name)
        return display, route_ok, route_missing

    def next_steps_respecting_requires(pid_: str, anchor_name: str) -> List[Dict[str, Any]]:
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
        WHERE NOT (p)-[:COMPLETED]->(n)
        RETURN n.name AS name, n.kind AS kind, labels(n) AS labels, requires_ok
        ORDER BY kind DESC, name ASC
        """
        return kg.run_list(q, pid=pid_, anchor=anchor_name)

    def _steps_for_evidence_key(fk_key: str) -> List[str]:
        q = """
        MATCH (s:Step)-[:EVIDENCE_HINTS]->(:FactKey {key:$k})
        RETURN s.name AS name ORDER BY name
        """
        return [r["name"] for r in kg.run_list(q, k=fk_key) if r.get("name")]

    def _is_done_or_in_progress(pid_: str, step_name: Optional[str]) -> bool:
        if not step_name:
            return False
        q = """
        MATCH (p:Patient {pid:$pid})
        RETURN EXISTS { MATCH (p)-[:COMPLETED]->(:Step {name:$s}) } AS done
        """
        row = kg._run_one(q, pid=pid_, s=step_name)
        return bool(row and row.get("done"))

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
        UNWIND (CASE WHEN size(provs) = 0 THEN [NULL] ELSE provs END) AS prov
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
        WITH fk, collect(DISTINCT {provider: coalesce(prov.name,'<kein Provider>'),
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

    def _router_requirements(pid_: str, router_name: str) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        rqs_route = [r for r in get_requires(pid_, router_name, include_route=True)
                     if str(r["key"]).startswith(ROUTE_PREFIX)]
        route_ok, route_missing = [], []
        for r in rqs_route:
            have = r["have"]
            if have is not None and str(have) == str(r["needed"]):
                route_ok.append(f"{r['key']}='{r['needed']}'")
            else:
                route_missing.append(f"{r['key']} benötigt '{r['needed']}' (aktuell {_fmt_have(have)})")
        rqs_nonroute = get_requires(pid_, router_name, include_route=False)
        unmet_nonroute = [r for r in rqs_nonroute if not (r["have"] is not None and str(r["have"]) == str(r["needed"]))]
        return route_ok, route_missing, unmet_nonroute

    def _get_provides_route_keys(step_name: str) -> List[str]:
        q = """
        MATCH (:Step {name:$name})-[:PROVIDES_FACT]->(fk:FactKey)
        WHERE fk.key STARTS WITH $routePrefix
        RETURN DISTINCT fk.key AS key ORDER BY key
        """
        return [r["key"] for r in kg.run_list(q, name=step_name, routePrefix=ROUTE_PREFIX) if r.get("key")]

    def _unlocked_steps_from_route_keys(pid_: str, src_step: str, route_keys: List[str]) -> List[str]:
        unlocked: List[str] = []
        seen = set()
        for k in route_keys:
            q = """
            MATCH (p:Patient {pid:$pid})
            MATCH (src:Step {name:$src})
            MATCH (cand:Step)-[:REQUIRES_FACT]->(:FactKey {key:$k})
            WHERE EXISTS { MATCH (src)-[:NEXT*0..]->(cand) }
              AND NOT EXISTS { MATCH (p)-[:COMPLETED]->(cand) }
            OPTIONAL MATCH (cand)-[:NEXT]->(child:Step)
            RETURN cand.name AS cand, labels(cand) AS labels, child.name AS child
            ORDER BY cand, child
            """
            rows = kg.run_list(q, pid=pid_, src=src_step, k=k)
            for r in rows:
                cand = r.get("cand")
                if not cand:
                    continue
                labels_ = r.get("labels") or []
                child = r.get("child")
                target = child if ("Routing" in labels_ and child) else cand
                if target and target not in seen:
                    seen.add(target)
                    unlocked.append(target)
        return sorted(unlocked)

    def get_provides_nonroute(pid_: str, step: str) -> List[Dict[str, Any]]:
        q = """
        MATCH (s:Step {name:$name})-[:PROVIDES_FACT]->(fk:FactKey)
        WHERE NOT fk.key STARTS WITH $routePrefix
        OPTIONAL MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
        RETURN fk.key AS key, head([v IN collect(pf.value) WHERE v IS NOT NULL]) AS patient_value
        ORDER BY key
        """
        return kg.run_list(q, pid=pid_, name=step, routePrefix=ROUTE_PREFIX)

    def get_outcome_branches(pid_: str, provider_step: str) -> List[Dict[str, Any]]:
        q = """
        MATCH (src:Step {name:$name})-[:PROVIDES_FACT]->(fk:FactKey)
        MATCH (src)-[:NEXT]->(r:Step)-[rq:REQUIRES_FACT]->(fk)
        WITH fk, rq.value AS needed, r
        OPTIONAL MATCH (r)-[:NEXT]->(child:Step)
        RETURN fk.key AS key, needed AS needed_value,
               r.name AS router_name, labels(r) AS router_labels, child.name AS child_name
        ORDER BY key, needed_value, router_name, child_name
        """
        rows = kg.run_list(q, name=provider_step)
        branches: List[Dict[str, Any]] = []
        for r in rows:
            is_router = "Routing" in (r.get("router_labels") or [])
            target = r.get("child_name") if is_router and r.get("child_name") else r.get("router_name")
            if not target:
                continue
            branches.append({"key": r["key"], "value": r["needed_value"], "target": target})
        uniq, out = set(), []
        for b in branches:
            t = (b["key"], str(b["value"]), b["target"])
            if t not in uniq:
                uniq.add(t)
                out.append(b)
        return out

    def _single_next_child(step_name: str) -> Optional[str]:
        rows = kg.run_list(
            "MATCH (:Step {name:$n})-[:NEXT]->(c:Step) RETURN DISTINCT c.name AS child ORDER BY child",
            n=step_name
        )
        children = [r["child"] for r in rows if r.get("child")]
        return children[0] if len(children) == 1 else None

    # ── Formatting functions (improved) ──

    def _fmt_providers(providers: List[Dict[str, Any]]) -> str:
        items = []
        for p in providers:
            name = p.get("provider")
            if not name or name == "<kein Provider>":
                continue
            status = p.get("status", "none")
            marker = "✓" if status == "completed" else ("~" if status == "performed" else "✗")
            items.append(f"{_label_step(name)} [{marker}]")
        return ", ".join(items) or "—"

    def _fmt_requires(reqs: List[Dict[str, Any]]) -> List[str]:
        if not reqs:
            return []
        lines = []
        for r in reqs:
            have = r["have"]
            need = r["needed"]
            if have is not None and str(have) == str(need):
                lines.append(f"    ✓ {_label_fact(r['key'])} = '{need}'")
            else:
                lines.append(f"    ✗ {_label_fact(r['key'])}: benötigt '{need}', aktuell {_fmt_have(have)}")
        return lines

    def _fmt_needs(needs: List[Dict[str, Any]]) -> List[str]:
        if not needs:
            return []
        lines = []
        for n in needs:
            pval = n["patient_value"]
            status = "vorhanden" if pval not in (None, "unknown") else "fehlt"
            provs = _fmt_providers(n["providers"])
            if pval in (None, "unknown"):
                lines.append(f"    ✗ {_label_fact(n['key'])}: {status} → Lieferant: {provs}")
            else:
                lines.append(f"    ✓ {_label_fact(n['key'])}: '{pval}'")
        return lines

    def _fmt_provides(provs: List[Dict[str, Any]]) -> List[str]:
        if not provs:
            return []
        lines = []
        for pr in provs:
            have = pr["patient_value"]
            if have not in (None, "unknown"):
                lines.append(f"    • {_label_fact(pr['key'])}: '{have}'")
            else:
                lines.append(f"    • {_label_fact(pr['key'])}: ausstehend")
        return lines

    def _fmt_outcome_preview(step_name: str, kind: Optional[str]) -> List[str]:
        if not _is_actionable(kind):
            return []
        branches = get_outcome_branches(pid, step_name)
        if not branches:
            return []
        grouped: Dict[str, List[Tuple[str, str]]] = {}
        for b in branches:
            grouped.setdefault(b["key"], []).append((str(b["value"]), b["target"]))
        lines = ["  Mögliche Weichen (abhängig vom Ergebnis):"]
        for fk, pairs in grouped.items():
            seen, ordered = set(), []
            for v, t in sorted(pairs, key=lambda x: (x[0], x[1])):
                if (v, t) not in seen:
                    ordered.append((v, t))
                    seen.add((v, t))
            for v, t in ordered:
                lines.append(f"    → {_label_fact(fk)} = '{v}': {_label_step(t)}")
        return lines

    def _fmt_next_preview(current_step: str) -> List[str]:
        nxt = _single_next_child(current_step)
        if not nxt:
            return []
        if _is_done_or_in_progress(pid, nxt):
            return []
        lines = [f"  Danach: {_label_step(nxt)}"]
        needs = get_needs_with_providers(pid, nxt) or []
        pending = [_label_fact(n["key"]) for n in needs if n.get("patient_value") in (None, "unknown")]
        if pending:
            lines.append(f"    Benötigt noch: {', '.join(pending)}")
        provs_next = get_provides_nonroute(pid, nxt)
        if provs_next:
            out_facts = ", ".join(_label_fact(p["key"]) for p in provs_next)
            lines.append(f"    Liefert: {out_facts}")
        return lines

    def _fmt_route_unlocks(step_name: str) -> List[str]:
        route_keys = _get_provides_route_keys(step_name)
        if not route_keys:
            return []
        unlocked = _unlocked_steps_from_route_keys(pid, step_name, route_keys)
        if not unlocked:
            return []
        return ["  Schaltet frei: " + ", ".join(_label_step(s) for s in unlocked)]

    def _fmt_parallel_status(pid_: str, fact_vals_: Dict[str, Any]) -> List[str]:
        lines = [_section_header("PARALLELE PFADE (Systemtherapie + Humangenetik)")]

        rqs_pj = [r for r in get_requires(pid_, PARALLEL_JOIN_NAME, include_route=True)
                  if str(r["key"]).startswith(ROUTE_PREFIX)]
        for r in rqs_pj:
            have = r["have"]
            if have is not None and str(have) == str(r["needed"]):
                lines.append(f"  ✓ {_label_fact(r['key'])}")
            else:
                lines.append(f"  ✗ {_label_fact(r['key'])}")

        needs_pj = get_needs_with_providers(pid_, PARALLEL_JOIN_NAME)
        if needs_pj:
            pend = []
            for n in needs_pj:
                if n["patient_value"] in (None, "unknown"):
                    provs_txt = _fmt_providers(n["providers"])
                    pend.append(f"{_label_fact(n['key'])} → {provs_txt}")
            if pend:
                lines.append("  Noch fehlend:")
                for p in pend:
                    lines.append(f"    ✗ {p}")
            else:
                lines.append("  Alle Informationen für die parallelen Pfade liegen vor.")

        children = routing_children(PARALLEL_JOIN_NAME)
        compatible: List[str] = []
        for cand_router in children:
            reqs_nonroute = get_requires(pid_, cand_router, include_route=False)
            if not conflicts_with_requires(reqs_nonroute, fact_vals_):
                tgt = routing_child(cand_router) or cand_router
                compatible.append(tgt)
        if compatible:
            lines.append(f"  Voraussichtlicher nächster Schritt: {_label_step(compatible[0])}")
        return lines

    def _check_parallel_reminder(out_lines: List[str]) -> None:
        neo_steps = _steps_for_evidence_key("ev_neoadjuvant_therapy_done")
        adj_steps = _steps_for_evidence_key("ev_adjuvant_therapy_done")
        systh_done = any(_is_done_or_in_progress(pid, s) for s in (neo_steps + adj_steps))
        genetic_steps = _steps_for_evidence_key("ev_genetic_counseling_done")
        genetic_done = any(_is_done_or_in_progress(pid, s) for s in genetic_steps)
        adjuvant_mapping_done = _is_done_or_in_progress(pid, names["adjuvantTherapyMapping"])
        neoadjuvant_mapping_done = _is_done_or_in_progress(pid, names["neoadjuvantTherapyMapping"])

        if genetic_done and not systh_done and not adjuvant_mapping_done and not neoadjuvant_mapping_done:
            out_lines.append("\nHinweis: Parallel zur Genetik sollte die Systemtherapie initiiert werden.")
        elif (systh_done or adjuvant_mapping_done or neoadjuvant_mapping_done) and not genetic_done:
            out_lines.append("\nHinweis: Parallel zur Systemtherapie sollte die humangenetische Beratung (gBRCA) erfolgen, ggf. gefolgt von HRD-Testung.")

    # ── Main output assembly ──

    patient_vals = patient_fact_values(pid)
    ap_rows = anchor_provides_nonroute(pid, a_name)

    out: List[str] = []

    # Section 1: Current position
    out.append(_section_header("AKTUELLER STAND"))
    out.append(f"Schritt: {_label_step(a_name)}")
    out.append(f"Typ: {_step_type_label(a_kind)} | Phase: {a_phase} | Tiefe: {a_depth}")

    if is_routing_step(a_name):
        par = routing_parent(a_name)
        if par:
            out.append(f"Vorangegangener Schritt: {_label_step(par)}")
        ch = routing_child(a_name)
        if ch:
            out.append(f"Zielschritt: {_label_step(ch)}")

    # Section 2: Results from current step
    if ap_rows:
        out.append("")
        out.append("Ergebnisse dieses Schritts:")
        for r in ap_rows:
            val = r["patient_value"]
            val_str = "ausstehend" if val is None else f"'{val}'"
            consumers = []
            for c in r.get("needs_cons", []):
                if c:
                    consumers.append(c)
            for c in r.get("req_cons", []):
                if c:
                    consumers.append(c)
            consumers = sorted(set(consumers))
            consumer_str = ", ".join(_label_step(c) for c in consumers) if consumers else "—"
            out.append(f"  • {_label_fact(r['key'])}: {val_str}")
            out.append(f"    Genutzt von: {consumer_str}")

    # Section 3: Next steps
    next_rows = next_steps_respecting_requires(pid, a_name)
    pj_summary_added = False

    out.append(_section_header("NÄCHSTE SCHRITTE"))

    if not next_rows:
        out.append("Keine weiteren Schritte offen.")
    else:
        step_num = 0
        for nr in next_rows:
            n_name = nr["name"]
            n_kind = nr["kind"]
            n_labels = nr["labels"] or []
            requires_ok = nr.get("requires_ok", True)
            is_router = "Routing" in n_labels

            unlocker_note: Optional[str] = None

            if is_router:
                reqs_all = get_requires(pid, n_name, include_route=True)
                if any(_is_conflict(r["have"], r["needed"]) for r in reqs_all):
                    continue
                display_name, route_ok, route_missing = resolve_effective_display_for_router(n_name, patient_vals)
                effective = display_name

                reqs_nonroute_router = get_requires(pid, n_name, include_route=False)
                missing_router_nonroute = [r for r in reqs_nonroute_router if _is_unknown(r["have"])]

                needs_missing_list: List[str] = []
                if n_name == PARALLEL_JOIN_NAME:
                    pj_needs = get_needs_with_providers(pid, PARALLEL_JOIN_NAME) or []
                    for ninfo in pj_needs:
                        if ninfo["patient_value"] in (None, "unknown"):
                            provs_txt = _fmt_providers(ninfo["providers"])
                            needs_missing_list.append(f"{_label_fact(ninfo['key'])} → {provs_txt}")

                if (not requires_ok) or route_missing or missing_router_nonroute or needs_missing_list:
                    step_num += 1
                    out.append(f"\n[{step_num}] BLOCKIERT: {_label_step(display_name)}")
                    if route_missing:
                        out.append("  Routing-Gates offen:")
                        for s in route_missing:
                            k = s.split(" benötigt ")[0].strip()
                            out.append(f"    ✗ {_label_fact(k)}")
                    if route_ok:
                        out.append("  Routing-Gates erfüllt:")
                        for s in route_ok:
                            k = s.split("=")[0].strip()
                            out.append(f"    ✓ {_label_fact(k)}")
                    if missing_router_nonroute:
                        out.append("  Voraussetzungen offen:")
                        out.extend(_fmt_requires(reqs_nonroute_router))
                    if needs_missing_list:
                        out.append("  Noch fehlende Informationen:")
                        for item in needs_missing_list:
                            out.append(f"    ✗ {item}")
                    if n_name == PARALLEL_JOIN_NAME and not pj_summary_added:
                        out.extend(_fmt_parallel_status(pid, patient_vals))
                        pj_summary_added = True
                    continue

                route_missing = []

            else:
                display_name = n_name
                effective = n_name

                reqs_nonroute = get_requires(pid, n_name, include_route=False)
                if conflicts_with_requires(reqs_nonroute, patient_vals):
                    continue

                step_route_ok, step_route_missing = eval_route_requires(pid, n_name)
                unmet_step_nonroute = [
                    r for r in reqs_nonroute
                    if not (r["have"] is not None and str(r["have"]) == str(r["needed"]))
                ]

                if (not requires_ok) or step_route_missing or unmet_step_nonroute:
                    step_num += 1
                    out.append(f"\n[{step_num}] BLOCKIERT: {_label_step(display_name)}")
                    if step_route_missing:
                        out.append("  Routing-Gates offen:")
                        for s in step_route_missing:
                            k = s.split(" benötigt ")[0].strip()
                            out.append(f"    ✗ {_label_fact(k)}")
                    if unmet_step_nonroute:
                        out.append("  Voraussetzungen offen:")
                        out.extend(_fmt_requires(reqs_nonroute))
                    continue

                if not step_route_ok and not step_route_missing:
                    parent_router = active_routing_parent(pid, n_name, a_name)
                    if parent_router:
                        unlocker_note = f"  Freigeschaltet durch: {_label_step(parent_router)}"
                        pr_route_ok, pr_route_missing, pr_unmet_nonroute = _router_requirements(pid, parent_router)
                        if pr_route_missing or pr_unmet_nonroute:
                            step_num += 1
                            out.append(f"\n[{step_num}] BLOCKIERT: {_label_step(display_name)}")
                            if pr_route_missing:
                                out.append("  Routing-Gates offen:")
                                for s in pr_route_missing:
                                    k = s.split(" benötigt ")[0].strip()
                                    out.append(f"    ✗ {_label_fact(k)}")
                            if pr_unmet_nonroute:
                                out.append("  Voraussetzungen offen:")
                                out.extend(_fmt_requires(get_requires(pid, parent_router, include_route=False)))
                            if parent_router == PARALLEL_JOIN_NAME and not pj_summary_added:
                                out.extend(_fmt_parallel_status(pid, patient_vals))
                                pj_summary_added = True
                            continue

                route_ok, route_missing = step_route_ok, step_route_missing

            # ── Actionable step ──
            step_num += 1
            type_tag = _step_type_label(n_kind).upper()
            out.append(f"\n[{step_num}] {type_tag}: {_label_step(display_name)}")

            if unlocker_note:
                out.append(unlocker_note)

            if route_ok:
                out.append("  Routing: erfüllt")

            if has_only_route_requires(pid, effective):
                out.append("  Keine weiteren fachlichen Voraussetzungen.")

            reqs_nonroute_eff = get_requires(pid, effective, include_route=False)
            if reqs_nonroute_eff:
                out.append("  Voraussetzungen:")
                out.extend(_fmt_requires(reqs_nonroute_eff))

            needs = get_needs_with_providers(pid, effective)
            if needs:
                any_missing = any(n["patient_value"] in (None, "unknown") for n in needs)
                if _is_evaluator(n_kind):
                    if any_missing:
                        out.append("  Benötigte Informationen (teils fehlend):")
                    else:
                        out.append("  Benötigte Informationen (alle vorhanden):")
                else:
                    if any_missing:
                        out.append("  Benötigte Informationen:")
                out.extend(_fmt_needs(needs))

            if not _is_evaluator(n_kind):
                provs = get_provides_nonroute(pid, effective)
                if provs:
                    out.append("  Liefert:")
                    out.extend(_fmt_provides(provs))

                out.extend(_fmt_outcome_preview(effective, n_kind))
                out.extend(_fmt_route_unlocks(effective))

            out.extend(_fmt_next_preview(effective))

            if _is_evaluator(n_kind) and needs:
                any_open = any(n["patient_value"] in (None, "unknown") for n in needs)
                if not any_open:
                    out.append("  → Entscheidung kann sofort getroffen werden.")

        _check_parallel_reminder(out)

        pj_in_next = any(
            nr["name"] == PARALLEL_JOIN_NAME
            for nr in next_rows
        )
        if pj_in_next and not pj_summary_added:
            out.extend(_fmt_parallel_status(pid, patient_vals))

    out.append("")
    return "\n".join(out)
