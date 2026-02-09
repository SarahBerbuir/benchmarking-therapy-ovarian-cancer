//Left path - uncomplicated - with CALL & Routing until deb ass & Whole OP Entscheider
// names
WITH {
  intake: "Vorsorge/Symptome",
  sonography: "Gynäkologische Untersuchung & Sonographie",
  iota: "IOTA-Auswertung (Simple Rules)",
  cystClassification: "Zystenklassifikation (BD-Klassifikation)",
  ct: "CT Thorax/Abdomen",
  figoBucketer: "FIGO Bucketer",
  debulkingAss: "Debulking Assessment",
  opDecider: "OP-Entscheider",
  followUp: "Verlaufskontrolle",
  cystectomy: "Zystenausschälung",
  adnexectomy: "Adnektomie",
  resectabilityEval: "Beurteilung Resektabilität im Tumorboard",
  laparotomy: "Laparotomie, SS",
  laparoscopy: "Laparoskopie oder Minilaparotomie",
  interdTb: "Interdisziplinäres Tumorboard",
  geneticCounselingGermlineBrca: "Humangenetische Beratung (gBRCA)",
  tumorHRDTesting: "HRD Testung (sBRCA & sHRD)",
  neoadjuvantTherapyMapping: "Neoadjuvante Therapie Mapping",
  neoadjuvantTherapy: "Neoadjuvante Therapie",
  nextStepMappingNeoAdj: "Next Step Mapping Neoadjuvant",
  adjuvantTherapyMapping: "Adjuvante Therapie Mapping",
  adjuvantTherapy: "Adjuvante Therapie",
  nextStepMappingAdj: "Next Step Mapping Adjuvant",
  interimRestagingCycle3: "Reevaluation nach 3 Zyklen, CT Thorax Abdomen, CA125, Operapabilität Assessment",
  chemoProtocolSwitchAndCompletion: "Wechsel Therapieprotokoll & Komplementtierung Chemotherapie (3x)",
  optimalDebulkingAndChemoCompletion: "Optimales Debulking & Komplementtierung Chemotherapie (3x)",
  repeatDebulkingAssessment: "Wiederholung Debulking Assessment",
  therapyReevaluation: "Therapie Reevaluation",
  parallelJoin: "Parallel Join",
  followUpCare: "Nachsorge"
} AS names

// steps
CALL (names) {
  MERGE (stepIntake:Step:Info {name:names.intake})                  ON CREATE SET stepIntake.kind = "Info"
  MERGE (stepSonography:Step:Diagnostic {name:names.sonography})    ON CREATE SET stepSonography.kind = "Diagnostic"
  MERGE (stepIota:Step:Evaluator {name:names.iota})                 ON CREATE SET stepIota.kind = "Evaluator", stepIota.logic = "iota_simple_rules"

  MERGE (stepCystClassification:Step:Evaluator {name:names.cystClassification})
    ON CREATE SET stepCystClassification.kind = "Evaluator", stepCystClassification.logic = "bd_classification"
  MERGE (stepOpDecider:Step:Evaluator {name:names.opDecider})       ON CREATE SET stepOpDecider.kind = "Evaluator", stepOpDecider.logic = "set_op_plan"
   MERGE (stepRouteFollowUpOp:Step:Evaluator:Routing {name:"Route Verlaufskontrolle (op_plan)"})
    ON CREATE SET stepRouteFollowUpOp.kind="Evaluator", stepRouteFollowUpOp.logic="set_route_flag"
  MERGE (stepCystectomy:Step:Therapy {name:names.cystectomy})       ON CREATE SET stepCystectomy.kind = "Therapy"
  MERGE (stepRouteFollowUpCystectomy:Step:Evaluator:Routing {name:"Route Verlaufskontrolle (Histologie Zystenausschälung)"})
    ON CREATE SET stepRouteFollowUpCystectomy.kind="Evaluator", stepRouteFollowUpCystectomy.logic="set_route_flag"
  MERGE (stepRouteAdnexectomyOpPlan:Step:Evaluator:Routing {name:"Route Adnektomie (op_plan Adnexectomy)"})
    ON CREATE SET stepRouteAdnexectomyOpPlan.kind="Evaluator", stepRouteAdnexectomyOpPlan.logic="set_route_flag"
  MERGE (stepAdnexectomy:Step:Therapy {name:names.adnexectomy})     ON CREATE SET stepAdnexectomy.kind = "Therapy"
  MERGE (stepRouteFollowUpAdnex:Step:Evaluator:Routing {name:"Route Verlaufskontrolle (Histologie Adnektomie)"})
    ON CREATE SET stepRouteFollowUpAdnex.kind="Evaluator", stepRouteFollowUpAdnex.logic="set_route_flag"
  MERGE (stepFollowUp:Step:Info {name:names.followUp})              ON CREATE SET stepFollowUp.kind = "Info"

  MERGE (stepCT:Step:Diagnostic {name:names.ct})                    ON CREATE SET stepCT.kind = "Diagnostic"
  MERGE (stepFIGOBucketer:Step:Evaluator {name:names.figoBucketer}) ON CREATE SET stepFIGOBucketer.kind = "Evaluator", stepFIGOBucketer.logic = "set_figo_bucket"
  MERGE (stepRouteAdnexectomyCFigo:Step:Evaluator:Routing {name:"Route Adnektomie (cFIGO early)"})
    ON CREATE SET stepRouteAdnexectomyCFigo.kind="Evaluator", stepRouteAdnexectomyCFigo.logic="set_route_flag"

  MERGE (stepDebulkingAss:Step:Evaluator {name:names.debulkingAss}) ON CREATE SET stepDebulkingAss.kind = "Evaluator", stepDebulkingAss.logic = "set_debulking_possible"
  MERGE (stepRouteDebulkingAssFIGOBucket:Step:Evaluator:Routing {name:"Route Debulking Assessment (FIGO Bucket)"})
    ON CREATE SET stepRouteDebulkingAssFIGOBucket.kind="Evaluator", stepRouteDebulkingAssFIGOBucket.logic="set_route_flag"
  MERGE (stepRouteDebulkingAssCystectomy:Step:Evaluator:Routing {name:"Route Debulking Assessment (Zystenausschälung)"})
    ON CREATE SET stepRouteDebulkingAssCystectomy.kind="Evaluator", stepRouteDebulkingAssCystectomy.logic="set_route_flag"
  MERGE (stepRouteDebulkingAssAdnexectomy:Step:Evaluator:Routing {name:"Route Debulking Assessment (Adnektomie)"})
    ON CREATE SET stepRouteDebulkingAssAdnexectomy.kind="Evaluator", stepRouteDebulkingAssAdnexectomy.logic="set_route_flag"
  MERGE (stepFollowUpResectability:Step:Info {name:names.resectabilityEval})  ON CREATE SET stepFollowUpResectability.kind = "Info"

  MERGE (stepLaparotomy:Step:Therapy {name:names.laparotomy})       ON CREATE SET stepLaparotomy.kind = "Therapy"
  MERGE (stepRouteInterdTbLaparotomy:Step:Evaluator:Routing {name:"Route Interdisziplinäres Tumorboard (Laparotomie)"})
    ON CREATE SET stepRouteInterdTbLaparotomy.kind="Evaluator", stepRouteInterdTbLaparotomy.logic="set_route_flag"


  MERGE (stepLaparoscopy:Step:Therapy {name:names.laparoscopy})       ON CREATE SET stepLaparoscopy.kind = "Therapy"
  MERGE (stepRouteInterdTbLaparoscopy:Step:Evaluator:Routing {name:"Route Interdisziplinäres Tumorboard (Laparoskopie)"})
    ON CREATE SET stepRouteInterdTbLaparoscopy.kind="Evaluator", stepRouteInterdTbLaparoscopy.logic="set_route_flag"

  MERGE (stepInterdTumorBoard:Step:Evaluator {name:names.interdTb})
    ON CREATE SET stepInterdTumorBoard.kind = "Evaluator", stepInterdTumorBoard.logic = "set_route_flag"

  MERGE (stepGeneticCounselingGermlineBRCA:Step:Diagnostic {name:names.geneticCounselingGermlineBrca}) ON CREATE SET stepGeneticCounselingGermlineBRCA.kind = "Diagnostic"
  MERGE (stepTumorHRDTesting:Step:Diagnostic {name:names.tumorHRDTesting}) ON CREATE SET stepTumorHRDTesting.kind = "Diagnostic"
  MERGE (stepBrcaHrdResolver:Step:Evaluator {name:"HRD/BRCA Resolver"})
    ON CREATE SET stepBrcaHrdResolver.kind="Evaluator", stepBrcaHrdResolver.logic="set_hrd_brca_status"

  MERGE (stepParallelJoin:Step:Evaluator {name:names.parallelJoin})
    ON CREATE SET stepParallelJoin.kind="Evaluator", stepParallelJoin.logic="set_route_flag"

  MERGE (stepNeoadjuvantTherapyMapping:Step:Evaluator {name:names.neoadjuvantTherapyMapping})
    ON CREATE SET stepNeoadjuvantTherapyMapping.kind="Evaluator", stepNeoadjuvantTherapyMapping.logic="set_neoadjuvant_therapy"
  MERGE (stepNeoadjuvantTherapy:Step:Therapy {name:names.neoadjuvantTherapy})       ON CREATE SET stepNeoadjuvantTherapy.kind = "Therapy"
  MERGE (stepNeoadjuvantNextStepMapping:Step:Evaluator {name:names.nextStepMappingNeoAdj})
    ON CREATE SET stepNeoadjuvantNextStepMapping.kind="Evaluator", stepNeoadjuvantNextStepMapping.logic="set_neo_adjuvant_next_step"
  MERGE (stepRouteNeoadjuvantNextStep:Step:Evaluator:Routing {name:"Route Next Step (Neoadjuvant)"})
    ON CREATE SET stepRouteNeoadjuvantNextStep.kind="Evaluator", stepRouteNeoadjuvantNextStep.logic="set_route_flag"
  MERGE (stepInterimRestagingCycle3:Step:Evaluator {name:names.interimRestagingCycle3})
    ON CREATE SET stepInterimRestagingCycle3.kind="Evaluator", stepInterimRestagingCycle3.logic="set_interim_restaging_operabel_ass"

  MERGE (stepChemoProtocolSwitchAndCompletion:Step:Therapy {name:names.chemoProtocolSwitchAndCompletion})       ON CREATE SET stepChemoProtocolSwitchAndCompletion.kind = "Therapy"
  MERGE (stepRepeatDebulkingAssessment:Step:Evaluator {name:names.repeatDebulkingAssessment})
    ON CREATE SET stepRepeatDebulkingAssessment.kind="Evaluator", stepRepeatDebulkingAssessment.logic="set_interim_restaging_operabel_ass"
  MERGE (stepTherapyReevaluation:Step:Info {name:names.therapyReevaluation})  ON CREATE SET stepTherapyReevaluation.kind = "Info"

  MERGE (stepRouteOptimalDebulkingComplRestaging:Step:Evaluator:Routing {name:"Route Optimales Debulking & Komplementtierung Chemotherapie (3x) (Interim Restaging)"})
    ON CREATE SET stepRouteOptimalDebulkingComplRestaging.kind="Evaluator", stepRouteOptimalDebulkingComplRestaging.logic="set_route_flag"
  MERGE (stepRouteOptimalDebulkingComplRepeatDebAss:Step:Evaluator:Routing {name:"Route Optimales Debulking & Komplementtierung Chemotherapie (3x) (Repeated Debulking Assessment)"})
    ON CREATE SET stepRouteOptimalDebulkingComplRepeatDebAss.kind="Evaluator", stepRouteOptimalDebulkingComplRepeatDebAss.logic="set_route_flag"
  MERGE (stepOptimalDebulkingChemoCompl:Step:Therapy {name:names.optimalDebulkingAndChemoCompletion})       ON CREATE SET stepOptimalDebulkingChemoCompl.kind = "Therapy"
  MERGE (stepRouteSystemDoneNeoadj:Step:Evaluator:Routing {name:"Route Systemtherapie Done (Neoaduvant)"})
    ON CREATE SET stepRouteSystemDoneNeoadj.kind="Evaluator", stepRouteSystemDoneNeoadj.logic="set_route_flag"

  MERGE (stepAdjuvantTherapyMapping:Step:Evaluator {name:names.adjuvantTherapyMapping})
    ON CREATE SET stepAdjuvantTherapyMapping.kind="Evaluator", stepAdjuvantTherapyMapping.logic="set_adjuvant_therapy"
  MERGE (stepAdjuvantTherapy:Step:Therapy {name:names.adjuvantTherapy})       ON CREATE SET stepAdjuvantTherapy.kind = "Therapy"
  MERGE (stepAdjuvantNextStepMapping:Step:Evaluator {name:names.nextStepMappingAdj})
    ON CREATE SET stepAdjuvantNextStepMapping.kind="Evaluator", stepAdjuvantNextStepMapping.logic="set_neo_adjuvant_next_step"
  MERGE (stepRouteAdjuvantNextStep:Step:Evaluator:Routing {name:"Route Next Step (Adjuvant)"})
    ON CREATE SET stepRouteAdjuvantNextStep.kind="Evaluator", stepRouteAdjuvantNextStep.logic="set_route_flag"
  MERGE (stepRouteSystemDoneAdj:Step:Evaluator:Routing {name:"Route Systemtherapie Done (Adjuvant)"})
    ON CREATE SET stepRouteSystemDoneAdj.kind="Evaluator", stepRouteSystemDoneAdj.logic="set_route_flag"

  RETURN {
    intake:                     stepIntake,
    sonography:                 stepSonography,
    iota:                       stepIota,
    cyst:                       stepCystClassification,
    op:                         stepOpDecider,
    routeFollowUpOp:            stepRouteFollowUpOp,
    cystectomy:                 stepCystectomy,
    routeAdnexectomyOpPlan:     stepRouteAdnexectomyOpPlan,
    routeAdnexectomyCFigo:      stepRouteAdnexectomyCFigo,
    adnexectomy:                stepAdnexectomy,
    routeFollowUpCystectomy:    stepRouteFollowUpCystectomy,
    routeFollowUpAdnex:         stepRouteFollowUpAdnex,
    follow:                     stepFollowUp,
    ct:                         stepCT,
    figo:                       stepFIGOBucketer,
    debulkingAss:               stepDebulkingAss,
    routeDebulkingAssFIGOBucket:    stepRouteDebulkingAssFIGOBucket,            //s.routeDebulkingAssFIGOBucket AS stepRouteDebulkingAssFIGOBucket,
    routeDebulkingAssCystectomy:    stepRouteDebulkingAssCystectomy,            //s.routeDebulkingAssCystectomy AS stepRouteDebulkingAssCystectomy,
    routeDebulkingAssAdnexectomy:   stepRouteDebulkingAssAdnexectomy,           //s.routeDebulkingAssAdnexectomy AS stepRouteDebulkingAssAdnexectomy,
    followUpResectability:          stepFollowUpResectability,                  //s.followUpResectability AS stepFollowUpResectability
    laparotomy:                     stepLaparotomy,                             //s.laparotomy AS stepLaparotomy,
    routeInterdTbLaparotomy:        stepRouteInterdTbLaparotomy,                //s.routeInterdTbLaparotomy AS stepRouteInterdTbLaparotomy,
    laparoscopy:                    stepLaparoscopy,                            //s.laparoscopy AS stepLaparoscopy,
    routeInterdTbLaparoscopy:       stepRouteInterdTbLaparoscopy,               //s.routeInterdTbLaparoscopy AS stepRouteInterdTbLaparoscopy,
    interdTumorBoard:               stepInterdTumorBoard,                       //s.interdTumorBoard AS stepInterdTumorBoard,
    geneticCounselingGermlineBRCA:  stepGeneticCounselingGermlineBRCA,          //s.geneticCounselingGermlineBRCA AS stepGeneticCounselingGermlineBRCA,
    tumorHRDTesting:                stepTumorHRDTesting,                        //s.tumorHRDTesting AS stepTumorHRDTesting,
    brcaHrdResolver:                stepBrcaHrdResolver,                        //s.brcaHrdResolver AS stepBrcaHrdResolver,
    parallelJoin:                   stepParallelJoin,                            //s.parallelJoin AS stepParallelJoin,
    neoadjuvantTherapyMapping:              stepNeoadjuvantTherapyMapping,              // s.neoadjuvantTherapyMapping AS stepNeoadjuvantTherapyMapping,
    neoadjuvantTherapy:                     stepNeoadjuvantTherapy,                     // s.neoadjuvantTherapy AS stepNeoadjuvantTherapy,
    neoadjuvantNextStepMapping:             stepNeoadjuvantNextStepMapping,             // s.neoadjuvantNextStepMapping AS stepNeoadjuvantNextStepMapping,
    routeNeoadjuvantNextStep:               stepRouteNeoadjuvantNextStep,               // s.routeNeoadjuvantNextStep AS stepRouteNeoadjuvantNextStep,
    interimRestagingCycle3:                 stepInterimRestagingCycle3,                 // s.interimRestagingCycle3 AS stepInterimRestagingCycle3,
    chemoProtocolSwitchAndCompletion:       stepChemoProtocolSwitchAndCompletion,       // s.chemoProtocolSwitchAndCompletion AS stepChemoProtocolSwitchAndCompletion,
    repeatDebulkingAssessment:              stepRepeatDebulkingAssessment,              // s.repeatDebulkingAssessment AS stepRepeatDebulkingAssessment,
    therapyReevaluation:                    stepTherapyReevaluation,                    // s.therapyReevaluation AS stepTherapyReevaluation,
    routeOptimalDebulkingComplRestaging:    stepRouteOptimalDebulkingComplRestaging,    // s.routeOptimalDebulkingComplRestaging AS stepRouteOptimalDebulkingComplRestaging,
    routeOptimalDebulkingComplRepeatDebAss: stepRouteOptimalDebulkingComplRepeatDebAss, // s.routeOptimalDebulkingComplRepeatDebAss AS stepRouteOptimalDebulkingComplRepeatDebAss,
    optimalDebulkingChemoCompl:             stepOptimalDebulkingChemoCompl,             // s.optimalDebulkingChemoCompl AS stepOptimalDebulkingChemoCompl,
    routeSystemDoneNeoadj:                  stepRouteSystemDoneNeoadj,                  // s.routeSystemDoneNeoadj AS stepRouteSystemDoneNeoadj,
    adjuvantTherapyMapping:                 stepAdjuvantTherapyMapping,                 // s.adjuvantTherapyMapping AS stepAdjuvantTherapyMapping,
    adjuvantTherapy:                        stepAdjuvantTherapy,                        // s.adjuvantTherapy AS stepAdjuvantTherapy,
    adjuvantNextStepMapping:                stepAdjuvantNextStepMapping,                // s.adjuvantNextStepMapping AS stepAdjuvantNextStepMapping,
    routeAdjuvantNextStep:                  stepRouteAdjuvantNextStep,                  // s.routeAdjuvantNextStep AS stepRouteAdjuvantNextStep,
    routeSystemDoneAdj:                     stepRouteSystemDoneAdj                      // s.routeSystemDoneAdj AS stepRouteSystemDoneAdj,



  } AS s
}

// evidence factkeys
WITH s
UNWIND [
  ["ev_sonography_present", s.sonography],
  ["ev_ct_present",         s.ct],
  ["ev_cystectomy_done",    s.cystectomy],
  ["ev_adnexectomy_done",   s.adnexectomy],
  ["ev_laparotomy_done",   s.laparotomy],
  ["ev_laparoscopy_done",   s.laparoscopy],
  ["ev_genetic_counseling_done", s.geneticCounselingGermlineBRCA],
  ["ev_hrd_test_done", s.tumorHRDTesting],
  ["ev_neoadjuvant_therapy_done", s.neoadjuvantTherapy],
  ["ev_adjuvant_therapy_done", s.adjuvantTherapy],
  ["ev_chemo_protocol_switch_completion_done", s.chemoProtocolSwitchAndCompletion],
  ["ev_optimal_debulking_completion_done", s.optimalDebulkingChemoCompl]
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
  [s.routeAdnexectomyCFigo,             s.adnexectomy],

  [s.figo,                              s.routeDebulkingAssFIGOBucket],
  [s.routeDebulkingAssFIGOBucket,       s.debulkingAss],

  [s.cystectomy,                        s.routeDebulkingAssCystectomy],
  [s.routeDebulkingAssCystectomy,       s.debulkingAss],

  [s.adnexectomy,                       s.routeDebulkingAssAdnexectomy],
  [s.routeDebulkingAssAdnexectomy,      s.debulkingAss],

  [s.debulkingAss,                      s.followUpResectability],
  [s.debulkingAss,                      s.laparotomy],
  [s.debulkingAss,                      s.laparoscopy],

  [s.laparotomy,                        s.routeInterdTbLaparotomy],
  [s.routeInterdTbLaparotomy,           s.interdTumorBoard],

  [s.laparoscopy,                       s.routeInterdTbLaparoscopy],
  [s.routeInterdTbLaparoscopy,          s.interdTumorBoard],

  [s.interdTumorBoard,                  s.geneticCounselingGermlineBRCA],
  [s.geneticCounselingGermlineBRCA,     s.tumorHRDTesting],
  [s.tumorHRDTesting,                   s.brcaHrdResolver],
  [s.geneticCounselingGermlineBRCA,     s.brcaHrdResolver],

  [s.brcaHrdResolver,                   s.parallelJoin]


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
// TODO MERGE (stepCT)-[:REQUIRES_FACT {value:"nicht_klassifizierbar"}]->(fkIotaRes) CT Routing

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
WITH s, fkCystectomyHistology, s.cystectomy AS stepCystectomy, s.routeFollowUpCystectomy AS stepRouteFollowUpCystectomy, s.routeDebulkingAssCystectomy AS stepRouteDebulkingAssCystectomy
MERGE (stepCystectomy)-[:PROVIDES_FACT]->(fkCystectomyHistology)
MERGE (stepRouteFollowUpCystectomy)-[:REQUIRES_FACT {value:"benigne"}]->(fkCystectomyHistology)
MERGE (stepRouteDebulkingAssCystectomy)-[:REQUIRES_FACT {value:"maligne"}]->(fkCystectomyHistology)

WITH s
MERGE (fkRouteAdnexectomy:FactKey {key:"route_adnexectomy"})
WITH s, fkRouteAdnexectomy, s.adnexectomy AS stepAdnexectomy, s.routeAdnexectomyOpPlan AS stepRouteAdnexectomyOpPlan, s.routeAdnexectomyCFigo as stepRouteAdnexectomyCFigo
MERGE (stepRouteAdnexectomyOpPlan)-[:PROVIDES_FACT]->(fkRouteAdnexectomy)
MERGE (stepRouteAdnexectomyCFigo)-[:PROVIDES_FACT]->(fkRouteAdnexectomy)
MERGE (stepAdnexectomy)-[:REQUIRES_FACT {value:true}]->(fkRouteAdnexectomy)

WITH s
MERGE (fkAdnexectomyHistology:FactKey {key:"histology_adnexectomy"})
WITH s, fkAdnexectomyHistology, s.adnexectomy AS stepAdnexectomy, s.routeFollowUpAdnex AS stepRouteFollowUpAdnex, s.routeDebulkingAssAdnexectomy AS stepRouteDebulkingAssAdnexectomy
MERGE (stepAdnexectomy)-[:PROVIDES_FACT]->(fkAdnexectomyHistology)
MERGE (stepRouteFollowUpAdnex)-[:REQUIRES_FACT {value:"benigne"}]->(fkAdnexectomyHistology)
MERGE (stepRouteDebulkingAssAdnexectomy)-[:REQUIRES_FACT {value:"maligne"}]->(fkAdnexectomyHistology)

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
WITH s, fkFigoBucket, s.figo AS stepFIGO, s.routeAdnexectomyCFigo as stepRouteAdnexectomyCFigo, s.routeDebulkingAssFIGOBucket AS stepRouteDebulkingAssFIGOBucket
MERGE (stepFIGO)-[:PROVIDES_FACT]->(fkFigoBucket)
MERGE (stepRouteAdnexectomyCFigo)-[:REQUIRES_FACT {value:"early"}]->(fkFigoBucket)
MERGE (stepRouteDebulkingAssFIGOBucket)-[:REQUIRES_FACT {value:"advanced"}]->(fkFigoBucket)


WITH s
MERGE (fkRouteDebAss:FactKey {key:"route_debulking_assessment"})
WITH s, fkRouteDebAss, s.debulkingAss AS stepDebulkingAss, s.routeDebulkingAssFIGOBucket AS stepRouteDebulkingAssFIGOBucket, s.routeDebulkingAssCystectomy AS stepRouteDebulkingAssCystectomy, s.routeDebulkingAssAdnexectomy AS stepRouteDebulkingAssAdnexectomy
MERGE (stepRouteDebulkingAssFIGOBucket)-[:PROVIDES_FACT]->(fkRouteDebAss)
MERGE (stepRouteDebulkingAssCystectomy)-[:PROVIDES_FACT]->(fkRouteDebAss)
MERGE (stepRouteDebulkingAssAdnexectomy)-[:PROVIDES_FACT]->(fkRouteDebAss)
MERGE (stepDebulkingAss)-[:REQUIRES_FACT {value:true}]->(fkRouteDebAss)

WITH s
MERGE (fkDebPoss:FactKey {key:"debulking_possible"}) //bool3
WITH s, fkDebPoss, s.debulkingAss AS stepDebulkingAss, s.followUpResectability AS stepFollowUpResectability, s.laparotomy AS stepLaparotomy, s.laparoscopy AS stepLaparoscopy
MERGE (stepDebulkingAss)-[:PROVIDES_FACT]->(fkDebPoss)
MERGE (stepFollowUpResectability)-[:REQUIRES_FACT {value:"unknown"}]->(fkDebPoss)
MERGE (stepLaparotomy)-[:REQUIRES_FACT {value:true}]->(fkDebPoss)
MERGE (stepLaparoscopy)-[:REQUIRES_FACT {value:false}]->(fkDebPoss)

WITH s
MERGE (fkLaparotomyGrade:FactKey {key:"grade_laparotomy"})
MERGE (fkLaparotomyFigoPath:FactKey {key:"figo_path_laparotomy"})
MERGE (fkLaparotomyHistology:FactKey {key:"histology_laparotomy"})
WITH s, fkLaparotomyGrade, fkLaparotomyFigoPath, fkLaparotomyHistology, s.laparotomy AS stepLaparotomy
MERGE (stepLaparotomy)-[:PROVIDES_FACT]->(fkLaparotomyGrade)
MERGE (stepLaparotomy)-[:PROVIDES_FACT]->(fkLaparotomyFigoPath)
MERGE (stepLaparotomy)-[:PROVIDES_FACT]->(fkLaparotomyHistology)

WITH s
MATCH (fkLapEv:FactKey {key:"ev_laparotomy_done"})
WITH s, s.routeInterdTbLaparotomy as stepRouteInterdTbLaparotomy
MERGE (stepRouteInterdTbLaparotomy)-[:REQUIRES_FACT {value:true}]->(fkLapEv)

WITH s
MERGE (fkLaparoscopyGrade:FactKey {key:"grade_laparoscopy"})
MERGE (fkLaparoscopyFigoPath:FactKey {key:"figo_path_laparoscopy"})
MERGE (fkLaparoscopyHistology:FactKey {key:"histology_laparoscopy"})
WITH s, fkLaparoscopyGrade, fkLaparoscopyFigoPath, fkLaparoscopyHistology, s.laparoscopy AS stepLaparoscopy
MERGE (stepLaparoscopy)-[:PROVIDES_FACT]->(fkLaparoscopyGrade)
MERGE (stepLaparoscopy)-[:PROVIDES_FACT]->(fkLaparoscopyFigoPath)
MERGE (stepLaparoscopy)-[:PROVIDES_FACT]->(fkLaparoscopyHistology)

WITH s
MERGE (fkRouteInterdTb:FactKey {key:"route_interdisciplinary_tumorboard"})
WITH s, fkRouteInterdTb, s.routeInterdTbLaparotomy AS stepRouteInterdTbLaparotomy, s.routeInterdTbLaparoscopy AS stepRouteInterdTbLaparoscopy, s.interdTumorBoard AS stepInterdTumorBoard
MERGE (stepRouteInterdTbLaparotomy)-[:PROVIDES_FACT]->(fkRouteInterdTb)
MERGE (stepRouteInterdTbLaparoscopy)-[:PROVIDES_FACT]->(fkRouteInterdTb)
MERGE (stepInterdTumorBoard)-[:REQUIRES_FACT {value:true}]->(fkRouteInterdTb)

WITH s
MERGE (fkRouteLaparotomy:FactKey {key:"route_laparotomy"})
WITH s, fkRouteLaparotomy, s.routeInterdTbLaparotomy AS stepRouteInterdTbLaparotomy
MERGE (stepRouteInterdTbLaparotomy)-[:PROVIDES_FACT]->(fkRouteLaparotomy)

WITH s
MERGE (fkRouteLaparoscopy:FactKey {key:"route_laparoscopy"})
WITH s, fkRouteLaparoscopy, s.routeInterdTbLaparoscopy AS stepRouteInterdTbLaparoscopy
MERGE (stepRouteInterdTbLaparoscopy)-[:PROVIDES_FACT]->(fkRouteLaparoscopy)


WITH s
MERGE (fkParallelStarting:FactKey {key:"parallel_starting"})
WITH s, fkParallelStarting, s.interdTumorBoard AS stepInterdTumorBoard, s.geneticCounselingGermlineBRCA AS stepGeneticCounselingGermlineBRCA, s.brcaHrdResolver AS stepBrcaHrdResolver
MERGE (stepInterdTumorBoard)-[:PROVIDES_FACT]->(fkParallelStarting)
MERGE (stepGeneticCounselingGermlineBRCA)-[:REQUIRES_FACT {value:true}]->(fkParallelStarting)
MERGE (stepBrcaHrdResolver)-[:REQUIRES_FACT {value:true}]->(fkParallelStarting)

WITH s
MERGE (fkgBRCA:FactKey {key:"gBRCA1/2"})
WITH s, fkgBRCA, s.geneticCounselingGermlineBRCA AS stepGeneticCounselingGermlineBRCA, s.tumorHRDTesting AS stepTumorHRDTesting, s.brcaHrdResolver AS stepBrcaHrdResolver
MERGE (stepGeneticCounselingGermlineBRCA)-[:PROVIDES_FACT]->(fkgBRCA)
MERGE (stepTumorHRDTesting)-[:REQUIRES_FACT {value:"-"}]->(fkgBRCA)
MERGE (stepBrcaHrdResolver)-[:NEEDS_FACT]->(fkgBRCA)

WITH s
MERGE (fksBRCA:FactKey {key:"sBRCA1/2"})
MERGE (fksHRD:FactKey {key:"sHRD"})
WITH s, fksBRCA, fksHRD, s.tumorHRDTesting AS stepTumorHRDTesting, s.brcaHrdResolver AS stepBrcaHrdResolver
MERGE (stepTumorHRDTesting)-[:PROVIDES_FACT]->(fksBRCA)
MERGE (stepTumorHRDTesting)-[:PROVIDES_FACT]->(fksHRD)
MERGE (stepBrcaHrdResolver)-[:NEEDS_FACT]->(fksBRCA)
MERGE (stepBrcaHrdResolver)-[:NEEDS_FACT]->(fksHRD)

WITH s
MERGE (fkHRDStatus:FactKey {key:"hrd_status"})
MERGE (fkBRCAStatus:FactKey {key:"brca_status"})
WITH s, fkHRDStatus, fkBRCAStatus, s.brcaHrdResolver AS stepBrcaHrdResolver, s.parallelJoin AS stepParallelJoin
MERGE (stepBrcaHrdResolver)-[:PROVIDES_FACT]->(fkHRDStatus)
MERGE (stepBrcaHrdResolver)-[:PROVIDES_FACT]->(fkBRCAStatus)
MERGE (stepParallelJoin)-[:NEEDS_FACT]->(fkHRDStatus)
MERGE (stepParallelJoin)-[:NEEDS_FACT]->(fkBRCAStatus)

WITH s
MERGE (fkParallelDone:FactKey {key:"parallel_done"})
WITH s, fkParallelDone, s.parallelJoin AS stepParallelJoin
MERGE (stepParallelJoin)-[:PROVIDES_FACT]->(fkParallelDone)
