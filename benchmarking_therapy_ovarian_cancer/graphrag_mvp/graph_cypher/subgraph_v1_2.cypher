//Left path - uncomplicated - with CALL
// names
WITH {
  intake: "Vorsorge/Symptome",
  sonography: "Gynäkologische Untersuchung & Sonographie",
  iota: "IOTA-Auswertung (Simple Rules)",
  cystClassification: "Zystenklassifikation (BD-Klassifikation)",
  ct: "CT Thorax/Abdomen",
  figoBucketer: "FIGO Bucketer",
  opDecider: "OP-Entscheider",
  followUp: "Verlaufskontrolle",
  cystectomy: "Zystenausschälung",
  adnexectomy: "Adnektomie"
} AS names

// steps
CALL (names) {
  MERGE (stepIntake:Step:Info {name:names.intake})                  ON CREATE SET stepIntake.kind = "Info"
  MERGE (stepSonography:Step:Diagnostic {name:names.sonography})    ON CREATE SET stepSonography.kind = "Diagnostic"
  MERGE (stepIota:Step:Evaluator {name:names.iota})                 ON CREATE SET stepIota.kind = "Evaluator", stepIota.logic = "iota_simple_rules"
  MERGE (stepCystClassification:Step:Evaluator {name:names.cystClassification})
    ON CREATE SET stepCystClassification.kind = "Evaluator", stepCystClassification.logic = "bd_classification"
  MERGE (stepCT:Step:Diagnostic {name:names.ct})                    ON CREATE SET stepCT.kind = "Diagnostic"
  MERGE (stepFIGOBucketer:Step:Evaluator {name:names.figoBucketer}) ON CREATE SET stepFIGOBucketer.kind = "Evaluator", stepFIGOBucketer.logic = "get_figo_bucket"
  MERGE (stepOpDecider:Step:Evaluator {name:names.opDecider})       ON CREATE SET stepOpDecider.kind = "Evaluator", stepOpDecider.logic = "get_op_plan"
  MERGE (stepFollowUp:Step:Info {name:names.followUp})              ON CREATE SET stepFollowUp.kind = "Info"
  MERGE (stepCystectomy:Step:Therapy {name:names.cystectomy})       ON CREATE SET stepCystectomy.kind = "Therapy"
  MERGE (stepAdnexectomy:Step:Therapy {name:names.adnexectomy})     ON CREATE SET stepAdnexectomy.kind = "Therapy"

  RETURN {
    intake:       stepIntake,
    sonography:   stepSonography,
    iota:         stepIota,
    cyst:         stepCystClassification,
    ct:           stepCT,
    figo:         stepFIGOBucketer,
    op:           stepOpDecider,
    follow:       stepFollowUp,
    cystectomy:   stepCystectomy,
    adnexectomy:  stepAdnexectomy
  } AS s
}

// evidence factkeys
WITH s
UNWIND [
  ["ev_sonography_present", s.sonography],
  ["ev_ct_present",         s.ct],
  ["ev_cystectomy_done",    s.cystectomy],
["ev_adnexectomy_done",   s.adnexectomy]
] AS pair
WITH s, pair[0] AS key, pair[1] AS step
MERGE (fk:FactKey {key:key})
MERGE (step)-[:EVIDENCE_HINTS]->(fk)

// flow
WITH s
UNWIND [
  [s.intake,     s.sonography],
  [s.sonography, s.iota],
  [s.iota,       s.cyst],
  [s.iota,       s.ct],
  [s.ct,         s.figo],
  [s.cyst,       s.op],
  [s.op,         s.follow],
  [s.op,         s.cystectomy],
  [s.op,         s.adnexectomy]
] AS edge
WITH s, edge[0] AS a, edge[1] AS b
MERGE (a)-[:NEXT]->(b)

// provides_fact (sonography → B/M)
WITH s, [
  "B1_unilokulaer","B2_solide_lt7mm","B3_schallschatten",
  "B4_glatt_multilok_lt10cm","B5_keine_doppler_flow",
  "M1_unreg_solid","M2_ascites","M3_ge4_papillae",
  "M4_unreg_multilok_solid_gt10cm","M5_hoher_doppler_flow"
] AS bmKeys
UNWIND bmKeys AS k
MERGE (bmKey:FactKey {key:k})
WITH s, bmKey, s.sonography AS stepSonography
MERGE (stepSonography)-[:PROVIDES_FACT]->(bmKey)

// provides_fact (iota → iota_res, cyst → cyst_bd)
WITH s
MERGE (fkIotaRes:FactKey {key:"iota_res"})
WITH s, fkIotaRes, s.iota AS stepIota
MERGE (stepIota)-[:PROVIDES_FACT]->(fkIotaRes)

// IOTA (cyst_bd, op needs cyst_bd)
WITH s
MERGE (fkCystBd:FactKey {key:"cyst_bd"})
WITH s, fkCystBd, s.cyst AS stepCyst, s.op AS stepOp
MERGE (stepCyst)-[:PROVIDES_FACT]->(fkCystBd)
MERGE (stepOp)-[:NEEDS_FACT]->(fkCystBd)

// op_decider → op_plan
WITH s
MERGE (fkOpPlan:FactKey {key:"op_plan"})
WITH s, fkOpPlan, s.op AS stepOp
MERGE (stepOp)-[:PROVIDES_FACT]->(fkOpPlan)

// Right path of IOTA
WITH s
MERGE (fkFigoClinical:FactKey {key:"figo_clinical"})
WITH s, fkFigoClinical, s.ct AS stepCT, s.figo AS stepFIGO
MERGE (stepCT)-[:PROVIDES_FACT]->(fkFigoClinical)
MERGE (stepFIGO)-[:NEEDS_FACT]->(fkFigoClinical)

WITH s
MERGE (fkFigoBucket:FactKey {key:"figo_bucket"})
WITH s, fkFigoBucket, s.figo AS stepFIGO
MERGE (stepFIGO)-[:PROVIDES_FACT]->(fkFigoBucket)

// needs_fact (iota needs B/M)
WITH s, [
  "B1_unilokulaer","B2_solide_lt7mm","B3_schallschatten",
  "B4_glatt_multilok_lt10cm","B5_keine_doppler_flow",
  "M1_unreg_solid","M2_ascites","M3_ge4_papillae",
  "M4_unreg_multilok_solid_gt10cm","M5_hoher_doppler_flow"
] AS bmKeys2
UNWIND bmKeys2 AS k
MERGE (fkBM:FactKey {key:k})
WITH s, fkBM, s.iota AS stepIota
MERGE (stepIota)-[:NEEDS_FACT]->(fkBM)

// requires_fact (gate cyst vs. CT via iota_res)
WITH s
MATCH (fkIotaRes:FactKey {key:"iota_res"})
WITH s, fkIotaRes, s.cyst AS stepCyst, s.ct AS stepCT
MERGE (stepCyst)-[:REQUIRES_FACT {value:"benigne_wahrscheinlich"}]->(fkIotaRes)
MERGE (stepCT)-[:REQUIRES_FACT {value:"maligne_wahrscheinlich"}]->(fkIotaRes)

// requires_fact for post op-decider routing by op_plan
WITH s
MATCH (fkOpPlan:FactKey {key:"op_plan"})
WITH s, fkOpPlan, s.follow AS stepFollow, s.cystectomy AS stepCystectomy, s.adnexectomy AS stepAdnexectomy
MERGE (stepFollow)-[:REQUIRES_FACT {value:"no_op"}]->(fkOpPlan)
MERGE (stepCystectomy)-[:REQUIRES_FACT {value:"Zystenausschälung"}]->(fkOpPlan)
MERGE (stepAdnexectomy)-[:REQUIRES_FACT {value:"Adnektomie"}]->(fkOpPlan)

