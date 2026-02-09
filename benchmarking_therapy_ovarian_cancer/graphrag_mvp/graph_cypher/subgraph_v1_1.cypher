//Left path - uncomplicated
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
MERGE (stepIntake:Step:Info {name:names.intake})                  ON CREATE SET stepIntake.kind = "Info"
MERGE (stepSonography:Step:Diagnostic {name:names.sonography})    ON CREATE SET stepSonography.kind = "Diagnostic"
MERGE (stepIota:Step:Evaluator {name:names.iota})                 ON CREATE SET stepIota.kind = "Evaluator", stepIota.logic = "iota_simple_rules"
MERGE (stepCystClassification:Step:Evaluator {name:names.cystClassification})
  ON CREATE SET stepCystClassification.kind = "Evaluator", stepCystClassification.logic = "bd_classification"
MERGE (stepCT:Step:Diagnostic {name:names.ct})                    ON CREATE SET stepCT.kind = "Diagnostic"
MERGE (stepFIGOBucketer:Step:Evaluator {name:names.figoBucketer}) ON CREATE SET stepFIGOBucketer.kind = "Evaluator", stepFIGOBucketer.logic = "set_figo_bucket"
MERGE (stepOpDecider:Step:Evaluator {name:names.opDecider})       ON CREATE SET stepOpDecider.kind = "Evaluator", stepOpDecider.logic = "set_op_plan"
MERGE (stepFollowUp:Step:Info {name:names.followUp})              ON CREATE SET stepFollowUp.kind = "Info"
MERGE (stepCystectomy:Step:Therapy {name:names.cystectomy})       ON CREATE SET stepCystectomy.kind = "Therapy"
MERGE (stepAdnexectomy:Step:Therapy {name:names.adnexectomy})     ON CREATE SET stepAdnexectomy.kind = "Therapy"

// evidence factkeys
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, stepFIGOBucketer

MERGE (fkSono:FactKey {key:"ev_sonography_present"})
MERGE (stepSonography)-[:EVIDENCE_HINTS]->(fkSono)

MERGE (fkCT:FactKey   {key:"ev_ct_present"})
MERGE (stepCT)-[:EVIDENCE_HINTS]->(fkCT)

MERGE (fkFollowUpEv:FactKey {key:"ev_followup_present"})
MERGE (stepFollowUp)-[:EVIDENCE_HINTS]->(fkFollowUpEv)

MERGE (fkCystectomyEv:FactKey {key:"ev_cystectomy_done"})
MERGE (stepCystectomy)-[:EVIDENCE_HINTS]->(fkCystectomyEv)

MERGE (fkAdnexectomyEv:FactKey {key:"ev_adnexectomy_done"})
MERGE (stepAdnexectomy)-[:EVIDENCE_HINTS]->(fkAdnexectomyEv)


// flow
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, stepFIGOBucketer

MERGE (stepIntake)-[:NEXT]->(stepSonography)
MERGE (stepSonography)-[:NEXT]->(stepIota)
MERGE (stepIota)-[:NEXT]->(stepCystClassification)
MERGE (stepIota)-[:NEXT]->(stepCT)

MERGE (stepCT)-[:NEXT]->(stepFIGOBucketer)

MERGE (stepCystClassification)-[:NEXT]->(stepOpDecider)

MERGE (stepOpDecider)-[:NEXT]->(stepFollowUp)
MERGE (stepOpDecider)-[:NEXT]->(stepCystectomy)
MERGE (stepOpDecider)-[:NEXT]->(stepAdnexectomy)


// provides_fact (sonography → B/M)
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, stepFIGOBucketer, [
  "B1_unilokulaer","B2_solide_lt7mm","B3_schallschatten",
  "B4_glatt_multilok_lt10cm","B5_keine_doppler_flow",
  "M1_unreg_solid","M2_ascites","M3_ge4_papillae",
  "M4_unreg_multilok_solid_gt10cm","M5_hoher_doppler_flow"
] AS bmKeys
UNWIND bmKeys AS k
MERGE (bmKey:FactKey {key:k})
MERGE (stepSonography)-[:PROVIDES_FACT]->(bmKey)

// provides_fact (iota → iota_res, cyst → cyst_bd)
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, stepFIGOBucketer
MERGE (fkIotaRes:FactKey {key:"iota_res"})
MERGE (stepIota)-[:PROVIDES_FACT]->(fkIotaRes)

//left side from IOTA Auswertung
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, stepFIGOBucketer, fkIotaRes
MERGE (fkCystBd:FactKey {key:"cyst_bd"})
MERGE (stepCystClassification)-[:PROVIDES_FACT]->(fkCystBd)
MERGE (stepOpDecider)-[:NEEDS_FACT]->(fkCystBd)

WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, stepFIGOBucketer, fkIotaRes, fkCystBd
MERGE (fkOpPlan:FactKey {key:"op_plan"})
MERGE (stepOpDecider)-[:PROVIDES_FACT]->(fkOpPlan)

//right side from IOTA Auswertung
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, stepFIGOBucketer, fkIotaRes, fkCystBd, fkOpPlan
MERGE (fkFigoClinical:FactKey {key:"figo_clinical"})
MERGE (stepCT)-[:PROVIDES_FACT]->(fkFigoClinical)
MERGE (stepFIGOBucketer)-[:NEEDS_FACT]->(fkFigoClinical)

WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, stepFIGOBucketer, fkIotaRes, fkCystBd, fkOpPlan
MERGE (fkFigoBucket:FactKey {key:"figo_bucket"})
MERGE (stepFIGOBucketer)-[:PROVIDES_FACT]->(fkFigoBucket)

// needs_fact (iota needs B/M)
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, fkOpPlan, fkIotaRes, [
  "B1_unilokulaer","B2_solide_lt7mm","B3_schallschatten",
  "B4_glatt_multilok_lt10cm","B5_keine_doppler_flow",
  "M1_unreg_solid","M2_ascites","M3_ge4_papillae",
  "M4_unreg_multilok_solid_gt10cm","M5_hoher_doppler_flow"
] AS bmKeys2
UNWIND bmKeys2 AS k
MERGE (fkBM:FactKey {key:k})
MERGE (stepIota)-[:NEEDS_FACT]->(fkBM)

// requires_fact (gate cyst vs. CT via iota_res)
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, fkOpPlan, fkIotaRes
MERGE (stepCystClassification)-[:REQUIRES_FACT {value:"benigne_wahrscheinlich"}]->(fkIotaRes)
MERGE (stepCT)-[:REQUIRES_FACT {value:"maligne_wahrscheinlich"}]->(fkIotaRes)

// requires_fact for post op-decider routing by op_plan
WITH stepIntake, stepSonography, stepIota, stepCystClassification, stepCT,
     stepOpDecider, stepFollowUp, stepCystectomy, stepAdnexectomy, fkOpPlan
MERGE (stepFollowUp)-[:REQUIRES_FACT {value:"no_op"}]->(fkOpPlan)
MERGE (stepCystectomy)-[:REQUIRES_FACT {value:"Zystenausschälung"}]->(fkOpPlan)
MERGE (stepAdnexectomy)-[:REQUIRES_FACT {value:"Adnektomie"}]->(fkOpPlan)

