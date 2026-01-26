from __future__ import annotations
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

    def frontier_steps(self, pid: str) -> list[tuple[str, str]]:
        """
        Steps where all REQUIRES_FACT are satisfied by patient's facts and which are not completed yet.
        Route-Frontier:
          - all REQUIRES_FACT met
          - not COMPLETED
          - not ON_HOLD
          - missing NEEDS_FACT block if at least one provider (of a needed fact) is evaluator
        """
        # language=Cypher
        q = """
      WITH $pid AS pid
MATCH (p:Patient {pid: pid})
MATCH (s:Step)
          
OPTIONAL MATCH (s)-[rq:REQUIRES_FACT]->(fk:FactKey)
WITH p, s,
     collect(CASE WHEN fk IS NULL THEN null ELSE {k: fk.key, v: rq.value} END) AS reqsRaw
WITH p, s, [r IN reqsRaw WHERE r IS NOT NULL] AS reqs
          
WHERE
  ALL (r IN reqs WHERE EXISTS {
    MATCH (p)-[:HAS_FACT]->(pf:PatientFact)-[:OF_KEY]->(:FactKey {key: r.k})
    WHERE pf.value = r.v
  })
  AND NOT EXISTS { MATCH (p)-[:COMPLETED]->(s) }
  AND NOT EXISTS { MATCH (p)-[:ON_HOLD]->(s) }
    
AND (
  NOT EXISTS {
    MATCH (s)-[:NEEDS_FACT]->(fkNeed:FactKey)
    OPTIONAL MATCH (prov:Step)-[:PROVIDES_FACT]->(fkNeed)
    WITH p, s, fkNeed, collect(DISTINCT prov.kind) AS provKindsPerKey
    WHERE "Evaluator" IN provKindsPerKey
    OPTIONAL MATCH (p)-[:HAS_FACT]->(pfN:PatientFact)-[:OF_KEY]->(fkNeed)
    WHERE pfN IS NULL OR pfN.value IS NULL OR pfN.value = "unknown"
    RETURN 1
  }
)
RETURN s.name AS name, s.kind AS kind;
        """

        rows = self.run_list(q, pid=pid)
        return [(row["name"], row["kind"]) for row in rows]

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
