from typing import List, Dict, Any, Optional, Tuple
from .knowledge_graph import KG
from graph_cypher.cypher_graph.definitions import definitions

ROUTE_PREFIX = "route_"
PARALLEL_JOIN_NAME = "Parallel Join"
TEXT_MODE = "clinical"
SHOW_KEYS = False


# Labeling

def _step_def(name: str) -> Optional[str]:
    return (definitions.get("steps") or {}).get(name) or None

def _fact_def(key: str) -> Optional[str]:
    return (definitions.get("facts") or {}).get(key) or None

def _label_step(name: str) -> str:
    d = _step_def(name)
    if TEXT_MODE == "clinical":
        return f"{name}" if not d else f"{name} — {d}"
    return name if not d else f"{name} ({d})"

def _label_fact(key: str) -> str:
    d = _fact_def(key)
    if TEXT_MODE == "clinical":
        if d and SHOW_KEYS:
            return f"{d} [{key}]"
        return d or key
    return f"{key} ({d})" if d else key

def _fmt_have(v: Any) -> str:
    return "fehlt" if v is None else f"'{v}'"

def _is_actionable(kind: Optional[str]) -> bool:
    return (kind or "").lower() in {"diagnostic", "therapy", "info"}

def _is_evaluator(kind: Optional[str]) -> bool:
    return (kind or "").lower() == "evaluator"

# Verbalization

def verbalize_subgraph_from_anchor(kg: KG, pid: str, anchor) -> str:
    if not anchor:
        return "Kein Schritt gefunden."

    a_name, a_kind, a_depth, a_phase = anchor["name"], anchor["kind"], anchor["depth"], anchor["phase"]

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

    def has_only_route_requires(pid_: str, step: str) -> bool:
        rqs_all = get_requires(pid_, step, include_route=True)
        if not rqs_all:
            return False
        return all(str(r["key"]).startswith(ROUTE_PREFIX) for r in rqs_all)

    def active_routing_parent(pid_: str, child: str, anchor_name: str) -> Optional[str]:
        # 1) Wenn Anchor Routing ist und direkt auf child zeigt, ist er der relevante Parent
        if is_routing_step(anchor_name):
            hit = kg._run_one(
                "MATCH (:Step {name:$a})-[:NEXT]->(:Step {name:$c}) RETURN 1 AS ok",
                a=anchor_name, c=child
            )
            if hit:
                return anchor_name

        # 2) Sonst: wähle Routing-Parent, der beim Patienten completed/performed ist
        q = """
        MATCH (p:Patient {pid:$pid})
        MATCH (par:Step)-[:NEXT]->(c:Step {name:$child})
        WHERE 'Routing' IN labels(par)
        WITH par,
             CASE
               WHEN (p)-[:COMPLETED]->(par) THEN 2
               WHEN (p)-[:PERFORMED]->(par) THEN 1
               ELSE 0
             END AS score
        RETURN par.name AS parent, score
        ORDER BY score DESC, parent ASC
        """
        rows = kg.run_list(q, pid=pid_, child=child)
        if not rows:
            return None

        best = rows[0]["score"]
        # 3) Wenn keiner aktiv ist und mehrere Kandidaten existieren -> nicht raten
        if best == 0 and len(rows) > 1:
            return None
        return rows[0]["parent"]

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
        for r in reqs_nonroute:
            k, need = r["key"], r["needed"]
            if k in anchor_vals and anchor_vals[k] is not None and str(anchor_vals[k]) != str(need):
                return True
        return False

    def resolve_effective_display_for_router(router_name: str, anchor_vals: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
        # 1) Voraussetzungen für diesen Weg bewerten (route_*)
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

        # 3) Parallel Join: kompatible Zielrouter bestimmen
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
        # WICHTIG: Router NICHT herausfiltern – requires_ok wird nur zurückgegeben.
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

    def _router_requirements(pid_: str, router_name: str) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """Gibt (route_ok, route_missing, unmet_nonroute) für einen Router zurück."""
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
        """
        Sucht NUR die direkten Weichen hinter 'provider_step':
        provider_step -[:PROVIDES_FACT]->(fk)
        provider_step -[:NEXT]->(r) -[:REQUIRES_FACT {value: v}]-> (fk)
        und löst Router auf ihr Kind auf.
        """
        q = """
        MATCH (src:Step {name:$name})-[:PROVIDES_FACT]->(fk:FactKey)
        MATCH (src)-[:NEXT]->(r:Step)-[rq:REQUIRES_FACT]->(fk)
        WITH fk, rq.value AS needed, r
        OPTIONAL MATCH (r)-[:NEXT]->(child:Step)
        RETURN fk.key AS key,
               needed AS needed_value,
               r.name  AS router_name,
               labels(r) AS router_labels,
               child.name AS child_name
        ORDER BY key, needed_value, router_name, child_name
        """
        rows = kg.run_list(q, name=provider_step)
        branches: List[Dict[str, Any]] = []
        for r in rows:
            is_router = "Routing" in (r.get("router_labels") or [])
            target = r.get("child_name") if is_router and r.get("child_name") else r.get("router_name")
            if not target:
                continue
            branches.append({
                "key": r["key"],
                "value": r["needed_value"],
                "target": target
            })
        uniq, out = set(), []
        for b in branches:
            t = (b["key"], str(b["value"]), b["target"])
            if t in uniq:
                continue
            uniq.add(t)
            out.append(b)
        return out


    def _providers_with_status(providers: List[Dict[str, Any]]) -> str:
        items = []
        for p in providers:
            name = p.get("provider")
            if not name or name == "<kein Provider modelliert>":
                continue
            items.append(f"{name}")
        return ", ".join(items) or "—"

    def _say_routing(route_ok: List[str], route_missing: List[str]) -> List[str]:
        lines: List[str] = []
        if route_missing:
            readable = []
            for s in route_missing:
                k = s.split(" benötigt ")[0].strip()
                readable.append(_label_fact(k))
            lines.append("   – Weg noch gesperrt durch: " + ", ".join(readable))
        elif route_ok:
            readable = []
            for s in route_ok:
                k = s.split("=")[0].strip()
                readable.append(_label_fact(k))
            lines.append("   – Voraussetzungen für diesen Weg erfüllt: " + ", ".join(readable))
        return lines

    def _say_requires(reqs_nonroute_eff: List[Dict[str, Any]]) -> List[str]:
        if not reqs_nonroute_eff:
            return ["   – Keine zusätzlichen Voraussetzungen."]
        open_items, ok_items = [], []
        for r in reqs_nonroute_eff:
            have = r["have"]
            need = r["needed"]
            if have is not None and str(have) == str(need):
                ok_items.append(_label_fact(r["key"]))
            else:
                open_items.append(f"{_label_fact(r['key'])} (sollte '{need}' sein; aktuell {_fmt_have(have)})")
        lines: List[str] = []
        if open_items:
            lines.append("   – Offen: " + "; ".join(open_items))
        if ok_items and not open_items:
            lines.append("   – Passt bereits: " + ", ".join(ok_items))
        return lines

    def _say_needs(needs: List[Dict[str, Any]], *, for_evaluator: bool) -> List[str]:
        if not needs:
            return ["   – Entscheidung ist mit den vorliegenden Informationen möglich."
                    ] if for_evaluator else ["   – Zusätzliche Informationen sind hierfür nicht erforderlich."]
        pending = []
        for n in needs:
            pval = n["patient_value"]
            if pval in (None, "unknown"):
                provs_txt = _providers_with_status(n["providers"])
                pending.append(f"{_label_fact(n['key'])} (wird geliefert durch: {provs_txt})")
        if pending:
            if for_evaluator:
                return ["   – Um entscheiden zu können, benötigen wir noch: " + "; ".join(pending)]
            return ["   – Dafür brauchen wir noch: " + "; ".join(pending)]
        return ["   – Entscheidung ist mit den vorliegenden Informationen möglich."
                ] if for_evaluator else ["   – Alle benötigten Informationen liegen bereits vor."]

    def _say_provides(provs: List[Dict[str, Any]]) -> List[str]:
        if not provs:
            return []
        items = []
        for pr in provs:
            have = pr["patient_value"]
            status = "liegt bereits vor" if have not in (None, "unknown") else "durchführen"
            items.append(f"{_label_fact(pr['key'])} ({status})")
        return ["   – Ergebnis dieses Schritts: " + ", ".join(items)]

    def _say_outcome_preview(step_name: str, kind: Optional[str]) -> List[str]:
        if not _is_actionable(kind):
            return []
        branches = get_outcome_branches(pid, step_name)
        if not branches:
            return []
        grouped: Dict[str, List[Tuple[str, str]]] = {}
        for b in branches:
            grouped.setdefault(b["key"], []).append((str(b["value"]), b["target"]))
        lines = ["   – Mögliche Weichen nach diesem Schritt (abhängig vom Ergebnis):"]
        for fk, pairs in grouped.items():
            seen, ordered = set(), []
            for v, t in sorted(pairs, key=lambda x: (x[0], x[1])):
                if (v, t) not in seen:
                    ordered.append((v, t))
                    seen.add((v, t))
            bullets = "; ".join([f"{_label_fact(fk)} = '{v}' → {_label_step(t)}" for v, t in ordered])
            lines.append("     – " + bullets)
        return lines

    def _summarize_parallel_join_requirements(pid_: str, anchor_vals_: Dict[str, Any]) -> List[str]:
        lines: List[str] = []
        lines.append("Parallel laufende Phasen (Systemtherapie und humangenetische Beratung gleichzeitig) – Status:")

        rqs_pj = [r for r in get_requires(pid_, PARALLEL_JOIN_NAME, include_route=True)
                  if str(r["key"]).startswith(ROUTE_PREFIX)]
        ok, missing = [], []
        for r in rqs_pj:
            have = r["have"]
            if have is not None and str(have) == str(r["needed"]):
                ok.append(_label_fact(r["key"]))
            else:
                missing.append(_label_fact(r["key"]))
        if ok:
            lines.append("   – Erfüllt: " + ", ".join(ok))
        if missing:
            lines.append("   – Offen: " + ", ".join(missing))

        needs_pj = get_needs_with_providers(pid_, PARALLEL_JOIN_NAME)
        if needs_pj:
            pend = []
            for n in needs_pj:
                if n["patient_value"] in (None, "unknown"):
                    provs_txt = _providers_with_status(n["providers"])
                    pend.append(f"{_label_fact(n['key'])} (wird geliefert durch: {provs_txt})")
            if pend:
                lines.append("   – Noch fehlend: " + "; ".join(pend))
            else:
                lines.append("   – Für die parallel laufenden Punkte liegen alle nötigen Informationen vor.")
        else:
            lines.append("   – Der Parallelschritt hat keine eigenen Informationsanforderungen.")

        # Nach Abschluss Parallel
        children = routing_children(PARALLEL_JOIN_NAME)
        compatible: List[str] = []
        for cand_router in children:
            reqs_nonroute = get_requires(pid_, cand_router, include_route=False)
            if not anchor_conflicts_with_requires(reqs_nonroute, anchor_vals_):
                tgt = routing_child(cand_router) or cand_router
                compatible.append(tgt)

        if compatible:
            primary_target = compatible[0]
            lines.append("Voraussichtlich nächster Zielschritt nach Abschluss: " + _label_step(primary_target))
            needs_target = get_needs_with_providers(pid_, primary_target)
            if needs_target:
                pend2 = []
                for n in needs_target:
                    if n["patient_value"] in (None, "unknown"):
                        provs_txt = _providers_with_status(n["providers"])
                        pend2.append(f"{_label_fact(n['key'])} (wird geliefert durch: {provs_txt})")
                if pend2:
                    lines.append("   – Dafür noch erforderlich: " + "; ".join(pend2))
                else:
                    lines.append("   – Dafür liegt alles Relevante bereits vor.")
        else:
            lines.append("Aktuell keine mit der Situation kompatible Zielspur gefunden.")

        return lines

    # Anchor
    anchor_vals = anchor_fact_values(pid, a_name)
    ap_rows = anchor_provides_nonroute(pid, a_name)

    out: List[str] = []
    out.append(f"Aktueller Stand: {_label_step(a_name)}")
    if is_routing_step(a_name):
        out.append("Weichenstellung: Voraussetzungen prüfen.\n")
    else:
        out.append(f"(Phase: {a_phase})\n")

    # Hinweis bei Routing-Knoten
    if is_routing_step(a_name):
        par = routing_parent(a_name)
        if par:
            out.append(f"Vorangegangener Schritt: {_label_step(par)}.")
        ch = routing_child(a_name)
        if ch:
            out.append(f"Nächster Zielschritt entlang dieses Weges: {_label_step(ch)}.\n")

    # Next steps
    next_rows = next_steps_respecting_requires(pid, a_name)
    pj_summary_added = False

    if not next_rows:
        out.append("Es sind aktuell keine weiteren sinnvollen Schritte offen.\n")
    else:
        out.append("Als nächstes sinnvoll umsetzen:")
        for nr in next_rows:
            n_name, n_kind, n_labels, requires_ok = nr["name"], nr["kind"], nr["labels"] or [], nr.get("requires_ok", True)
            is_router = "Routing" in n_labels

            if is_router:
                display_name, route_ok, route_missing = resolve_effective_display_for_router(n_name, anchor_vals)
                effective = display_name

                # fachliche REQUIRES direkt am Router prüfen (z. B. parallel_done=True)
                reqs_nonroute_router = get_requires(pid, n_name, include_route=False)
                unmet_router_nonroute = [
                    r for r in reqs_nonroute_router
                    if not (r["have"] is not None and str(r["have"]) == str(r["needed"]))
                ]

                # NEEDS am Parallel-Join als Blocker
                needs_missing_list: List[str] = []
                if n_name == PARALLEL_JOIN_NAME:
                    pj_needs = get_needs_with_providers(pid, PARALLEL_JOIN_NAME) or []
                    for ninfo in pj_needs:
                        if ninfo["patient_value"] in (None, "unknown"):
                            provs_txt = _providers_with_status(ninfo["providers"])
                            needs_missing_list.append(f"{_label_fact(ninfo['key'])} (wird geliefert durch: {provs_txt})")

                # Wenn Router fachlich/NEEDS/route_* nicht ok ODER requires_ok==False → "Noch nicht möglich"
                if (not requires_ok) or route_missing or unmet_router_nonroute or needs_missing_list:
                    out.append(f"• Noch nicht möglich: {_label_step(display_name)}")
                    out.extend(_say_routing(route_ok, route_missing))
                    if unmet_router_nonroute:
                        out.extend(_say_requires(reqs_nonroute_router))
                    if needs_missing_list:
                        out.append("   – Noch fehlend: " + "; ".join(needs_missing_list))

                    if (n_name == PARALLEL_JOIN_NAME) and not pj_summary_added:
                        out.extend(_summarize_parallel_join_requirements(pid, anchor_vals))
                        pj_summary_added = True
                    out.append("")  # optische Trennung
                    continue

                # Router ist ok :„normale“ Behandlung wie Nicht-Router
                display_name = effective
                route_ok, route_missing = route_ok, []

            else:
                # Nicht-Router: nur eigene fachliche REQUIRES prüfen
                reqs_nonroute = get_requires(pid, n_name, include_route=False)
                if anchor_conflicts_with_requires(reqs_nonroute, anchor_vals):
                    # Unvereinbar mit bereits vorliegenden Anchor-Werten
                    continue

                display_name = n_name
                effective = n_name
                route_ok, route_missing = [], []

                # Falls es einen direkten Router-Vorgänger gibt (z. B. Parallel Join),
                # blockiere diesen Schritt, wenn dessen route_* oder fachliche REQUIRES noch offen sind.
                parent_router = active_routing_parent(pid, n_name, a_name)
                if parent_router and is_routing_step(parent_router):
                    out.append(f"   – Freigeschaltet durch: {_label_step(parent_router)} (Routing-Entscheidung).")
                if parent_router:
                    pr_route_ok, pr_route_missing, pr_unmet_nonroute = _router_requirements(pid, parent_router)
                    if pr_route_missing or pr_unmet_nonroute:
                        out.append(f"• Noch nicht möglich: {_label_step(display_name)}")
                        out.extend(_say_routing(pr_route_ok, pr_route_missing))
                        if pr_unmet_nonroute:
                            out.extend(_say_requires(get_requires(pid, parent_router, include_route=False)))
                        if parent_router == PARALLEL_JOIN_NAME and not pj_summary_added:
                            out.extend(_summarize_parallel_join_requirements(pid, anchor_vals))
                            pj_summary_added = True
                        out.append("")
                        continue

            # Headline
            title = _label_step(display_name)
            if _is_evaluator(n_kind):
                out.append(f"• Entscheidungspunkt: {title}")
            elif _is_actionable(n_kind):
                out.append(f"• Veranlassen: {title}")
            else:
                out.append(f"• Nächster Schritt: {title}")

            out.extend(_say_routing(route_ok, route_missing))

            reqs_nonroute_eff = get_requires(pid, effective, include_route=False)
            out.extend(_say_requires(reqs_nonroute_eff))

            if not reqs_nonroute_eff and has_only_route_requires(pid, effective):
                out.append(
                    "   – Keine zusätzlichen fachlichen Voraussetzungen (nur Routing-Gates, keine Handlungsempfehlung).")
            # NEEDS
            needs = get_needs_with_providers(pid, effective)
            out.extend(_say_needs(needs, for_evaluator=_is_evaluator(n_kind)))

            # PROVIDES (not evaluator)
            if not _is_evaluator(n_kind):
                provs = get_provides_nonroute(pid, effective)
                out.extend(_say_provides(provs))
                # Outcome-Preview (nur bei Actionables)
                out.extend(_say_outcome_preview(effective, n_kind))

            # Evaluator: wenn nichts mehr fehlt, Hinweis „Entscheidung möglich“
            if _is_evaluator(n_kind):
                any_open = any((n["patient_value"] in (None, "unknown")) for n in (needs or []))
                if not any_open:
                    out.append("   – Entscheidung kann mit den vorliegenden Informationen getroffen werden.")

            out.append("")

        # Falls die Parallelphase unter den nächsten Schritten ist und noch keine Zusammenfassung angehängt wurde:
        pj_in_next = any(
            nr["name"] == PARALLEL_JOIN_NAME or ("Routing" in (nr["labels"] or []) and nr["name"] == PARALLEL_JOIN_NAME)
            for nr in next_rows
        )
        if pj_in_next and not pj_summary_added:
            out.extend(_summarize_parallel_join_requirements(pid, anchor_vals))
            out.append("")

    # Provides step
    if not ap_rows:
        out.append("Bisher dokumentierte Ergebnisse aus dem aktuellen Schritt: Keine")
    else:
        out.append("Bisher dokumentierte Ergebnisse aus dem aktuellen Schritt:")
        for r in ap_rows:
            val = r["patient_value"]
            val_str = "noch offen" if val is None else f"'{val}'"
            needs_cons = ", ".join([_label_step(c) for c in r["needs_cons"] if c]) or "—"
            req_cons   = ", ".join([_label_step(c) for c in r["req_cons"] if c]) or "—"
            out.append(f"• {_label_fact(r['key'])}: {val_str} | genutzt in: {needs_cons} / {req_cons}")

    return "\n".join(out)
