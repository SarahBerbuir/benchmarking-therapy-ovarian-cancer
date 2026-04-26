//Left path - uncomplicated - with CALL & Routing
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
  MERGE (stepFIGOBucketer:Step:Evaluator {name:names.figoBucketer}) ON CREATE SET stepFIGOBucketer.kind = "Evaluator", stepFIGOBucketer.logic = "set_figo_bucket"
  MERGE (stepOpDecider:Step:Evaluator {name:names.opDecider})       ON CREATE SET stepOpDecider.kind = "Evaluator", stepOpDecider.logic = "set_op_plan"
   MERGE (stepRouteFollowUpOp:Step:Evaluator:Routing {name:"Route Verlaufskontrolle (op_plan)"})
    ON CREATE SET stepRouteFollowUpOp.kind="Evaluator", stepRouteFollowUpOp.logic="set_route_flag"
  MERGE (stepCystectomy:Step:Therapy {name:names.cystectomy})       ON CREATE SET stepCystectomy.kind = "Therapy"
  MERGE (stepRouteFollowUpCystectomy:Step:Evaluator:Routing {name:"Route Verlaufskontrolle (Histologie Zystenausschälung)"})
    ON CREATE SET stepRouteFollowUpCystectomy.kind="Evaluator", stepRouteFollowUpCystectomy.logic="set_route_flag"
  MERGE (stepRouteAdnexectomyOpPlan:Step:Evaluator:Routing {name:"Route Adnektomie (op_plan Adnexectomy)"})
    ON CREATE SET stepRouteAdnexectomyOpPlan.kind="Evaluator", stepRouteAdnexectomyOpPlan.logic="set_route_flag"
  MERGE (stepRouteAdnexectomyCFigo:Step:Evaluator:Routing {name:"Route Adnektomie (cFIGO early)"})
    ON CREATE SET stepRouteAdnexectomyCFigo.kind="Evaluator", stepRouteAdnexectomyCFigo.logic="set_route_flag"
  MERGE (stepAdnexectomy:Step:Therapy {name:names.adnexectomy})     ON CREATE SET stepAdnexectomy.kind = "Therapy"
  MERGE (stepRouteFollowUpAdnex:Step:Evaluator:Routing {name:"Route Verlaufskontrolle (Histologie Adnektomie benigne)"})
    ON CREATE SET stepRouteFollowUpAdnex.kind="Evaluator", stepRouteFollowUpAdnex.logic="set_route_flag"
  MERGE (stepFollowUp:Step:Info {name:names.followUp})              ON CREATE SET stepFollowUp.kind = "Info"

  RETURN {
    intake:                     stepIntake,
    sonography:                 stepSonography,
    iota:                       stepIota,
    cyst:                       stepCystClassification,
    ct:                         stepCT,
    figo:                       stepFIGOBucketer,
    op:                         stepOpDecider,
    routeFollowUpOp:            stepRouteFollowUpOp,
    cystectomy:                 stepCystectomy,
    routeAdnexectomyOpPlan:     stepRouteAdnexectomyOpPlan,
    routeAdnexectomyCFigo:      stepRouteAdnexectomyCFigo,
    adnexectomy:                stepAdnexectomy,
    routeFollowUpCystectomy:    stepRouteFollowUpCystectomy,
    routeFollowUpAdnex:         stepRouteFollowUpAdnex,
    follow:                     stepFollowUp
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
  [s.intake,                            s.sonography],
  [s.sonography,                        s.iota],
  [s.iota,                              s.cyst],
  [s.iota,                              s.ct],

  // left path from iota
  [s.cyst,                              s.op],

  [s.op,                                s.routeFollowUpOp],
  [s.op,                                s.cystectomy],
  [s.op,                                s.routeAdnexectomyOpPlan],

  [s.routeAdnexectomyOpPlan,            s.adnexectomy],

  [s.cystectomy,                        s.routeFollowUpCystectomy],
  [s.routeFollowUpCystectomy,           s.follow],

  [s.adnexectomy,                       s.routeFollowUpAdnex],
  [s.routeFollowUpAdnex,                s.follow],

  [s.routeFollowUpOp,                   s.follow],

  //right path from iota
  [s.ct,                                s.figo],
  [s.figo,                              s.routeAdnexectomyCFigo],

  [s.routeAdnexectomyCFigo,            s.adnexectomy]

] AS edge
WITH s, edge[0] AS a, edge[1] AS b
MERGE (a)-[:NEXT]->(b)

// provides_fact (sonography → B/M)
WITH s, [
  "B1_unilokulaer","B2_solide_lt7mm","B3_schallschatten",
  "B4_glatt_multilok_lt10cm","B5_keine_doppler_flow",
  "M1_unreg_solid","M2_ascites","M3_ge4_papillae",
  "M4_unreg_multilok_solid_gt10cm","M5_hoher_doppler_flow",
  "praemenopausal", "symptoms_present", "growth",
  "persistence", "complex_multiloculaer",
  "psychic_unsure", "ca125_u_ml", "size_cm"
] AS bmKeys
UNWIND bmKeys AS k
MERGE (bmKey:FactKey {key:k})
WITH s, bmKey, s.sonography AS stepSonography, s.iota AS stepIota
MERGE (stepSonography)-[:PROVIDES_FACT]->(bmKey)

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


// provides_fact & requires fact & needs fact
WITH s
MERGE (fkIotaRes:FactKey {key:"iota_res"})
WITH s, fkIotaRes, s.iota AS stepIota, s.cyst AS stepCyst, s.ct AS stepCT
MERGE (stepIota)-[:PROVIDES_FACT]->(fkIotaRes)
MERGE (stepCyst)-[:REQUIRES_FACT {value:"benigne_wahrscheinlich"}]->(fkIotaRes)
MERGE (stepCT)-[:REQUIRES_FACT {value:"maligne_wahrscheinlich"}]->(fkIotaRes)
MERGE (stepCT)-[:REQUIRES_FACT {value:"nicht_klassifizierbar"}]->(fkIotaRes)

// left path of iota
WITH s
MERGE (fkCystBd:FactKey {key:"cyst_bd"})
WITH s, fkCystBd, s.cyst AS stepCyst, s.op AS stepOp
MERGE (stepCyst)-[:PROVIDES_FACT]->(fkCystBd)
MERGE (stepOp)-[:NEEDS_FACT]->(fkCystBd)

WITH s, [
  "cyst_bd", "praemenopausal", "symptoms_present", "growth",
  "persistence", "complex_multiloculaer",
  "psychic_unsure", "ca125_u_ml", "size_cm"
] AS opDecKeys
UNWIND opDecKeys AS k
MERGE (fkOpKey:FactKey {key:k})
WITH s, fkOpKey, s.op AS stepOpDecider
MERGE (stepOpDecider)-[:NEEDS_FACT]->(fkOpKey)


WITH s
MERGE (fkOpPlan:FactKey {key:"op_plan"})
WITH s, fkOpPlan, s.op AS stepOp, s.cystectomy AS stepCystectomy, s.routeFollowUpOp as stepRouteFollowUpOp, s.routeAdnexectomyOpPlan AS stepRouteAdnexectomyOpPlan
MERGE (stepOp)-[:PROVIDES_FACT]->(fkOpPlan)
MERGE (stepRouteFollowUpOp)-[:REQUIRES_FACT {value:"no_op"}]->(fkOpPlan)
MERGE (stepCystectomy)-[:REQUIRES_FACT {value:"Zystenausschälung"}]->(fkOpPlan)
MERGE (stepRouteAdnexectomyOpPlan)-[:REQUIRES_FACT {value:"Adnektomie"}]->(fkOpPlan)

WITH s
MERGE (fkCystectomyHistology:FactKey {key:"histology_cystectomy"})
WITH s, fkCystectomyHistology, s.cystectomy AS stepCystectomy, s.routeFollowUpCystectomy AS stepRouteFollowUpCystectomy
MERGE (stepCystectomy)-[:PROVIDES_FACT]->(fkCystectomyHistology)
MERGE (stepRouteFollowUpCystectomy)-[:REQUIRES_FACT {value:"benigne"}]->(fkCystectomyHistology)

WITH s
MERGE (fkRouteAdnexectomy:FactKey {key:"route_adnexectomy"})
WITH s, fkRouteAdnexectomy, s.adnexectomy AS stepAdnexectomy, s.routeAdnexectomyOpPlan AS stepRouteAdnexectomyOpPlan, s.routeAdnexectomyCFigo as stepRouteAdnexectomyCFigo
MERGE (stepRouteAdnexectomyOpPlan)-[:PROVIDES_FACT]->(fkRouteAdnexectomy)
MERGE (stepRouteAdnexectomyCFigo)-[:PROVIDES_FACT]->(fkRouteAdnexectomy)
MERGE (stepAdnexectomy)-[:REQUIRES_FACT {value:true}]->(fkRouteAdnexectomy)

WITH s
MERGE (fkAdnexectomyHistology:FactKey {key:"histology_adnexectomy"})
WITH s, fkAdnexectomyHistology, s.adnexectomy AS stepAdnexectomy, s.routeFollowUpAdnex AS stepRouteFollowUpAdnex
MERGE (stepAdnexectomy)-[:PROVIDES_FACT]->(fkAdnexectomyHistology)
MERGE (stepRouteFollowUpAdnex)-[:REQUIRES_FACT {value:"benigne"}]->(fkAdnexectomyHistology)

WITH s
MERGE (fkRouteFollowUp:FactKey {key:"route_follow_up"})
WITH s, fkRouteFollowUp, s.routeFollowUpOp AS stepRouteFollowUpOp, s.routeFollowUpCystectomy AS stepRouteFollowUpCystectomy, s.routeFollowUpAdnex AS stepRouteFollowUpAdnex, s.follow AS stepFollow
MERGE (stepRouteFollowUpOp)-[:PROVIDES_FACT]->(fkRouteFollowUp)
MERGE (stepRouteFollowUpCystectomy)-[:PROVIDES_FACT]->(fkRouteFollowUp)
MERGE (stepRouteFollowUpAdnex)-[:PROVIDES_FACT]->(fkRouteFollowUp)
MERGE (stepFollow)-[:REQUIRES_FACT {value:true}]->(fkRouteFollowUp)

// Right path of IOTA
WITH s
MERGE (fkFigoClinical:FactKey {key:"figo_clinical"})
WITH s, fkFigoClinical, s.ct AS stepCT, s.figo AS stepFIGO
MERGE (stepCT)-[:PROVIDES_FACT]->(fkFigoClinical)
MERGE (stepFIGO)-[:NEEDS_FACT]->(fkFigoClinical)

WITH s
MERGE (fkFigoBucket:FactKey {key:"figo_bucket"})
WITH s, fkFigoBucket, s.figo AS stepFIGO, s.routeAdnexectomyCFigo as stepRouteAdnexectomyCFigo
MERGE (stepFIGO)-[:PROVIDES_FACT]->(fkFigoBucket)
MERGE (stepRouteAdnexectomyCFigo)-[:REQUIRES_FACT {value:"early"}]->(fkFigoBucket)


