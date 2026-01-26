// constraints
CREATE CONSTRAINT step_name IF NOT EXISTS
FOR (s:Step) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT fact_key IF NOT EXISTS
FOR (f:FactKey) REQUIRE f.key IS UNIQUE;

// names
WITH {
  intake: "Vorsorge/Symptome",
  sonography: "Gynäkologische Untersuchung & Sonographie",
  iota: "IOTA-Auswertung (Simple Rules)",
  cystClassification: "Zystenklassifikation (BD-Klassifikation)",
  ct: "CT Thorax/Abdomen"
} AS names

// steps
MERGE (stepIntake:Step:Info {name:names.intake})                  ON CREATE SET stepIntake.kind = "Info"
MERGE (stepSonography:Step:Diagnostic {name:names.sonography})    ON CREATE SET stepSonography.kind = "Diagnostic"
MERGE (stepIota:Step:Evaluator {name:names.iota})                 ON CREATE SET stepIota.kind = "Evaluator", stepIota.logic = "iota_simple_rules"
MERGE (stepCystClassification:Step:Evaluator {name:names.cystClassification})
  ON CREATE SET stepCystClassification.kind = "Evaluator", stepCystClassification.logic = "cyst_bd_rules"
MERGE (stepCT:Step:Diagnostic {name:names.ct})                    ON CREATE SET stepCT.kind = "Diagnostic"

// evidence factkeys
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT

MERGE (fkSono:FactKey {key:"ev_sonography_present"})
MERGE (fkCT:FactKey   {key:"ev_ct_present"})
MERGE (stepSonography)-[:EVIDENCE_HINTS]->(fkSono)
MERGE (stepCT)-[:EVIDENCE_HINTS]->(fkCT)

// flow
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT

MERGE (stepIntake)-[:NEXT]->(stepSonography)
MERGE (stepSonography)-[:NEXT]->(stepIota)
MERGE (stepIota)-[:NEXT]->(stepCystClassification)
MERGE (stepIota)-[:NEXT]->(stepCT)

// provides_fact (sonography → B/M)
WITH stepSonography, stepIota, stepCystClassification, stepCT, [
  "B1_unilokulaer","B2_solide_lt7mm","B3_schallschatten",
  "B4_glatt_multilok_lt10cm","B5_keine_doppler_flow",
  "M1_unreg_solid","M2_ascites","M3_ge4_papillae",
  "M4_unreg_multilok_solid_gt10cm","M5_hoher_doppler_flow"
] AS bmKeys
UNWIND bmKeys AS k
MERGE (bmKey:FactKey {key:k})
MERGE (stepSonography)-[:PROVIDES_FACT]->(bmKey)

// provides_fact (iota → iota_res; cyst → cyst_bd)
WITH stepIota, stepCystClassification, stepCT
MERGE (fkIotaRes:FactKey {key:"iota_res"})
MERGE (stepIota)-[:PROVIDES_FACT]->(fkIotaRes)

MERGE (fkCystBd:FactKey {key:"cyst_bd"})
MERGE (stepCystClassification)-[:PROVIDES_FACT]->(fkCystBd)

// needs_fact (iota needs B/M)
WITH stepIota, stepCystClassification, stepCT, fkIotaRes, [
  "B1_unilokulaer","B2_solide_lt7mm","B3_schallschatten",
  "B4_glatt_multilok_lt10cm","B5_keine_doppler_flow",
  "M1_unreg_solid","M2_ascites","M3_ge4_papillae",
  "M4_unreg_multilok_solid_gt10cm","M5_hoher_doppler_flow"
] AS bmKeys2
UNWIND bmKeys2 AS k
MERGE (fkBM:FactKey {key:k})
MERGE (stepIota)-[:NEEDS_FACT]->(fkBM)

// requires_fact (gate cyst vs. CT via iota_res)
WITH stepCystClassification, stepCT, fkIotaRes
MERGE (stepCystClassification)-[:REQUIRES_FACT {value:"benigne_wahrscheinlich"}]->(fkIotaRes)
MERGE (stepCT)-[:REQUIRES_FACT {value:"maligne_wahrscheinlich"}]->(fkIotaRes)

