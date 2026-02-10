from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from neo4j import GraphDatabase, Driver

import logging
logger = logging.getLogger(__name__)

class KG:

    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j") -> None:
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self) -> None:
        self.driver.close()

    # def _run(self, cypher: str, **params):
    #     with self.driver.session(database=self.database) as s:
    #         return s.run(cypher, **params)

    def run_write(self, cypher: str, **params) -> None:
        with self.driver.session(database=self.database) as session:
            session.run(cypher, **params).consume()

    def run_list(self, cypher: str, **params):
        with self.driver.session(database=self.database) as session:
            res = session.run(cypher, **params)
            return list(res)

    def _run_one(self, cypher: str, **params):
        with self.driver.session(database=self.database) as session:
            return session.run(cypher, **params).single()

    def ensure_constraints(self) -> None:
        self.run_write("CREATE CONSTRAINT step_name IF NOT EXISTS FOR (s:Step) REQUIRE s.name IS UNIQUE")
        self.run_write("CREATE CONSTRAINT fact_key  IF NOT EXISTS FOR (f:FactKey) REQUIRE f.key  IS UNIQUE")
        self.run_write("CREATE CONSTRAINT patient_pid IF NOT EXISTS FOR (p:Patient) REQUIRE p.pid IS UNIQUE")

    def upsert_patient(self, pid: str) -> None:
        # create Patient if missing
        self.run_write("MERGE (:Patient {pid:$pid})", pid=pid)
        #logger.info(f"Upserted patient {pid}")
        print(f"upserted patient {pid}")

    # facts

    def upsert_fact(self, pid: str, key: str, value: Any, source: str, conf: float) -> None:
        """
        Write/overwrite a patient fact. Pattern: (p)-[:HAS_FACT]->(pf)-[:OF_KEY]->(fk)
        """
        query = """
        MATCH (p:Patient {pid:$pid})
        MERGE (fk:FactKey {key: toString($key)})
        MERGE (p)-[:HAS_FACT]->(pf:PatientFact)-[:OF_KEY]->(fk)
        SET 
             pf.name = $val,
             pf.value = $val,
             pf.source = $src,
             pf.conf = coalesce($conf, 1.0),
             pf.ts = datetime()
        """
        self.run_write(query, pid=pid, key=key, val=value, src=source, conf=conf)

    def get_patient_facts(self, pid: str) -> Dict[str, Any]:
        # return {key: value} for a patient
        query = """
        MATCH (p:Patient {pid:$pid})-[:HAS_FACT]->(pf:PatientFact)-[:OF_KEY]->(fk:FactKey)
        RETURN fk.key AS k, pf.value AS v
        """
        rows = self.run_list(query, pid=pid)
        return {row["k"]: row["v"] for row in rows}

    # process status

    def mark_completed(self, pid: str, step_name: str) -> None:
        # mark step as completed for a patient
        query = """
        MATCH (p:Patient {pid:$pid}), (s:Step {name:$name})
        MERGE (p)-[:COMPLETED {ts:datetime()}]->(s)
        """
        self.run_write(query, pid=pid, name=step_name)

    def mark_performed(self, pid: str, step_name: str, reason: str = "evidence") -> None:
        q = """
        MATCH (p:Patient {pid:$pid}), (s:Step {name:$name})
        MERGE (p)-[:PERFORMED {ts:datetime()}]->(s)
        """
        self.run_write(q, pid=pid, name=step_name, reason=reason)

    def step_provides_meta(self, step_name: str) -> list[dict]:
        q = """
        MATCH (:Step {name:$s})-[r:PROVIDES_FACT]->(fk:FactKey)
        RETURN fk.key AS k, coalesce(r.hard,false) AS hard
        ORDER BY fk.key
        """
        return [{"key": row["k"], "hard": bool(row["hard"])} for row in self.run_list(q, s=step_name)]

    def is_completed(self, pid: str, step_name: str) -> bool:
        # check completion flag
        q = """
        MATCH (p:Patient {pid:$pid})-[:COMPLETED]->(s:Step {name:$name})
        RETURN count(*) AS n
        """
        row = self._run_one(q, pid=pid, name=step_name)
        return bool(row and row["n"] > 0)

    # Frountier calculation

    def recompute_on_hold(self, pid: str, root_name: str) -> None:
        self.run_write("""
            MATCH (p:Patient {pid:$pid})-[r:ON_HOLD]->(:Step) DELETE r
        """, pid=pid)

        # for each completed anchor descendents ON_HOLD
        self.run_write("""
            MATCH (p:Patient {pid:$pid})
            MATCH (root:Step {name:$root})
            MATCH (p)-[:COMPLETED]->(anchor:Step)
            MATCH path=(root)-[:NEXT*0..]->(anchor)
            WITH p, nodes(path) AS ns
            UNWIND ns AS s
            WITH p, s
            WHERE NOT (p)-[:COMPLETED]->(s)
            MERGE (p)-[:ON_HOLD]->(s)
        """, pid=pid, root=root_name)

    def run_script(self, script: str) -> None:
        statements = [s.strip() for s in script.split(";") if s.strip()]
        with self.driver.session(database=self.database) as s:
            for st in statements:
                s.run(st)

    def delete_all(self) -> None:
        self.run_write("MATCH (n) DETACH DELETE n")


    def step_needs(self, step_name: str) -> list[str]:
        q = "MATCH (:Step {name:$s})-[:NEEDS_FACT]->(fk:FactKey) RETURN fk.key AS k"
        return [row["k"] for row in self.run_list(q, s=step_name)]

    def step_requires(self, step_name: str) -> list[tuple[str, object]]:
        q = """
        MATCH (s:Step {name:$name})-[r:REQUIRES_FACT]->(fk:FactKey)
        RETURN fk.key AS key, r.value AS val
        """
        rows = self.run_list(q, name=step_name)
        return [(row["key"], row["val"]) for row in rows]

    def step_provides(self, step_name: str) -> list[str]:
        q = "MATCH (:Step {name:$s})-[:PROVIDES_FACT]->(fk:FactKey) RETURN fk.key AS k"
        return [row["k"] for row in self.run_list(q, s=step_name)]

    def step_logic(self, step_name: str) -> str | None:
        row = self._run_one("MATCH (s:Step {name:$s}) RETURN s.logic AS logic", s=step_name)
        return row["logic"] if row else None

    def on_hold_steps(self, pid: str) -> list[str]:
        rows = self.run_list("""
            MATCH (p:Patient {pid:$pid})-[:ON_HOLD]->(s:Step)
            RETURN s.name AS name
        """, pid=pid)
        return [row["name"] for row in rows]

    def rebuild_from_cypher(self, cypher_file: str | Path) -> None:
        """
        MVP-Reinit:
          1) Delete all nodes/rels
          2) Constraints/Indices
          3) Create KG with Cypher-Script
        """
        path = Path(cypher_file)
        if not path.exists():
            raise FileNotFoundError(f"Cypher file not found: {path}")

        self.delete_all()
        self.ensure_constraints()

        script = path.read_text(encoding="utf-8")
        self.run_script(script)

    def frontier_steps(self, pid: str, root_name: str = "Vorsorge/Symptome") -> list[tuple[str, str, int]]:
        """
        Steps where all REQUIRES_FACT are satisfied by patient's facts and which are not completed yet.
        Route-Frontier:
          - reachable from root
          - all REQUIRES_FACT met
          - not COMPLETED
          - not ON_HOLD
          - Scope-gating: missing NEEDS_FACT block if provider are not completed yet
        """
        q = """
            WITH $pid AS pid, $root AS rootName
            MATCH (p:Patient {pid: pid})
            MATCH (root:Step {name : rootName})
            MATCH (s:Step)

            OPTIONAL MATCH sp = shortestPath( (root)-[:NEXT*0..]->(s) )
            WITH p, s, sp IS NOT NULL AS reachable,
                CASE WHEN sp IS NULL THEN -1 ELSE length(sp) END AS depth 
            
            OPTIONAL MATCH (p)-[oh:ON_HOLD]->(s)
            WITH p, s, depth, reachable, (oh IS NOT NULL) AS is_on_hold
        
            OPTIONAL MATCH (s)-[rq:REQUIRES_FACT]->(fkReq:FactKey)
            WITH p, s, depth, reachable, is_on_hold, [ r IN collect(CASE WHEN fkReq IS NULL THEN NULL ELSE {k: fkReq.key, v: rq.value} END)
            WHERE r IS NOT NULL ] AS reqs

            WITH p, s, depth, reachable, is_on_hold, ALL (r IN reqs WHERE EXISTS {
                MATCH (p)-[:HAS_FACT]->(pfR:PatientFact)-[:OF_KEY]->(:FactKey {key :r.k})
                WHERE pfR.value = r.v
                }) AS requires_ok

            WITH p, s, depth, reachable, requires_ok, is_on_hold,
                EXISTS { MATCH (p)-[:COMPLETED]->(s) } AS is_completed
            
            WHERE reachable
              AND requires_ok
              AND NOT is_completed
              AND (s.kind = 'Evaluator' OR NOT is_on_hold)
              
              AND NOT EXISTS {
                MATCH (s)-[:NEEDS_FACT]->(fkNeed:FactKey)
                MATCH (prov:Step)-[:PROVIDES_FACT]->(fkNeed)
                WITH p, fkNeed, collect(DISTINCT prov) AS provs
                WHERE size(provs) > 0
                  AND NONE(pr IN provs WHERE EXISTS { MATCH (p)-[:COMPLETED]->(pr) })
                RETURN 1
              }
            
            WITH DISTINCT s, depth, CASE s.kind
                WHEN 'Evaluator' THEN 4
                WHEN 'Diagnostic' THEN 3
                WHEN 'Therapy' THEN 2
                WHEN 'Info' THEN 1
                ELSE 0
            END 
            AS prio
        RETURN s.name AS name, s.kind AS kind, depth
        ORDER BY depth ASC, prio DESC, name ASC 
        """
        rows = self.run_list(q, pid=pid, root=root_name)
        return [(row["name"], row["kind"], int(row["depth"])) for row in rows]

