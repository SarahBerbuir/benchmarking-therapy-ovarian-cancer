WITH $names AS names
CALL (names){
  // Basis
  MATCH (stepIntake:Step {name:names.intake})
  MATCH (stepSonography:Step {name:names.sonography})
  MATCH (stepIota:Step {name:names.iota})
  MATCH (stepCystClassification:Step {name:names.cystClassification})

  // OP & Follow-up Routen
  MATCH (stepOpDecider:Step {name:names.opDecider})
  MATCH (stepRouteFollowUpOp:Step {name:names.routeFollowUpOp})
  MATCH (stepCystectomy:Step {name:names.cystectomy})
  MATCH (stepRouteFollowUpCystectomy:Step {name:names.routeFollowUpCystectomy})
  MATCH (stepRouteAdnexectomyOpPlan:Step {name:names.routeAdnexectomyOpPlan})
  MATCH (stepAdnexectomy:Step {name:names.adnexectomy})
  MATCH (stepRouteFollowUpAdnex:Step {name:names.routeFollowUpAdnex})
  MATCH (stepFollowUp:Step {name:names.followUp})

  // FIGO / CT / DBA
  MATCH (stepCT:Step {name:names.ct})
  MATCH (stepFIGOBucketer:Step {name:names.figoBucketer})
  MATCH (stepRouteAdnexectomyCFigo:Step {name:names.routeAdnexectomyCFigo})
  MATCH (stepDebulkingAss:Step {name:names.debulkingAss})
  MATCH (stepRouteDebulkingAssFIGOBucket:Step {name:names.routeDebulkingAssFIGOBucket})
  MATCH (stepRouteDebulkingAssCystectomy:Step {name:names.routeDebulkingAssCystectomy})
  MATCH (stepRouteDebulkingAssAdnexectomy:Step {name:names.routeDebulkingAssAdnexectomy})
  MATCH (stepFollowUpResectability:Step {name:names.resectabilityEval})

  // Laparotomie/Laparoskopie & TB-Routen
  MATCH (stepLaparotomy:Step {name:names.laparotomy})
  MATCH (stepRouteFollowUpLaparotomy:Step {name:names.routeFollowUpLaparotomy})
  MATCH (stepRouteInterdTbLaparotomy:Step {name:names.routeInterdTbLaparotomy})
  MATCH (stepLaparoscopy:Step {name:names.laparoscopy})
  MATCH (stepRouteFollowUpLaparoscopy:Step {name:names.routeFollowUpLaparoscopy})
  MATCH (stepRouteInterdTbLaparoscopy:Step {name:names.routeInterdTbLaparoscopy})
  MATCH (stepInterdTumorBoard:Step {name:names.interdTb})

  // HRD/BRCA Pfad
  MATCH (stepGeneticCounselingGermlineBRCA:Step {name:names.geneticCounselingGermlineBrca})
  MATCH (stepRouteBrcaHrdResolverGermline:Step {name:names.routeBrcaHrdResolverGermline})

  MATCH (stepTumorHRDTesting:Step {name:names.tumorHRDTesting})
  MATCH (stepRouteBrcaHrdResolverHRDTesting:Step {name:names.routeBrcaHrdResolverHRDTesting})

  MATCH (stepBrcaHrdResolver:Step {name:names.hrcBrcaResolver})
  MATCH (stepParallelJoin:Step {name:names.parallelJoin})

  // Neoadjuvant
  MATCH (stepNeoadjuvantTherapyMapping:Step {name:names.neoadjuvantTherapyMapping})
  MATCH (stepNeoadjuvantTherapy:Step {name:names.neoadjuvantTherapy})
  MATCH (stepNeoadjuvantNextStepMapping:Step {name:names.nextStepMappingNeoAdj})
  MATCH (stepRouteNeoadjuvantNextStep:Step {name:names.routeNeoadjuvantNextStep})
  MATCH (stepInterimRestagingCycle3:Step {name:names.interimRestagingCycle3})
  MATCH (stepChemoProtocolSwitchAndCompletion:Step {name:names.chemoProtocolSwitchAndCompletion})
  MATCH (stepRepeatDebulkingAssessment:Step {name:names.repeatDebulkingAssessment})
  MATCH (stepTherapyReevaluation:Step {name:names.therapyReevaluation})
  MATCH (stepRouteOptimalDebulkingComplRestaging:Step {name:names.routeOptimalDebulkingComplRestaging})
  MATCH (stepRouteOptimalDebulkingComplRepeatDebAss:Step {name:names.routeOptimalDebulkingComplRepeatDebAss})
  MATCH (stepOptimalDebulkingChemoCompl:Step {name:names.optimalDebulkingAndChemoCompletion})
  MATCH (stepRouteSystemDoneNeoadj:Step {name:names.routeSystemDoneNeoadj})

  // Adjuvant
  MATCH (stepAdjuvantTherapyMapping:Step {name:names.adjuvantTherapyMapping})
  MATCH (stepAdjuvantTherapy:Step {name:names.adjuvantTherapy})
  MATCH (stepAdjuvantNextStepMapping:Step {name:names.nextStepMappingAdj})
  MATCH (stepRouteAdjuvantNextStep:Step {name:names.routeAdjuvantNextStep})
  MATCH (stepRouteSystemDoneAdj:Step {name:names.routeSystemDoneAdj})

  // Erhaltungstherapie
  MATCH (stepRouteFollowUpCareSystTh:Step {name:names.routeFollowUpCareSystTh})
  MATCH (stepRouteFollowUpCareMaintTh:Step {name:names.routeFollowUpCareMaintTh})
  MATCH (stepFollowUpCare:Step {name:names.followUpCare})
  MATCH (stepMaintenanceTherapyMapping:Step {name:names.maintenanceTherapyMapping})
  MATCH (stepMaintenanceTherapy:Step {name:names.maintenanceTherapy})

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
    routeFollowUpLaparotomy:    stepRouteFollowUpLaparotomy,
    routeFollowUpLaparoscopy:   stepRouteFollowUpLaparoscopy,
    follow:                     stepFollowUp,
    ct:                         stepCT,
    figo:                       stepFIGOBucketer,
    debulkingAss:               stepDebulkingAss,
    routeDebulkingAssFIGOBucket:    stepRouteDebulkingAssFIGOBucket,
    routeDebulkingAssCystectomy:    stepRouteDebulkingAssCystectomy,
    routeDebulkingAssAdnexectomy:   stepRouteDebulkingAssAdnexectomy,
    followUpResectability:          stepFollowUpResectability,
    laparotomy:                     stepLaparotomy,
    routeInterdTbLaparotomy:        stepRouteInterdTbLaparotomy,
    laparoscopy:                    stepLaparoscopy,
    routeInterdTbLaparoscopy:       stepRouteInterdTbLaparoscopy,
    interdTumorBoard:               stepInterdTumorBoard,
    geneticCounselingGermlineBRCA:  stepGeneticCounselingGermlineBRCA,
    routeBrcaHrdResolverHRDTesting: stepRouteBrcaHrdResolverHRDTesting,
    routeBrcaHrdResolverGermline: stepRouteBrcaHrdResolverGermline,
    tumorHRDTesting:                stepTumorHRDTesting,
    brcaHrdResolver:                stepBrcaHrdResolver,
    parallelJoin:                   stepParallelJoin,
    neoadjuvantTherapyMapping:      stepNeoadjuvantTherapyMapping,
    neoadjuvantTherapy:             stepNeoadjuvantTherapy,
    neoadjuvantNextStepMapping:     stepNeoadjuvantNextStepMapping,
    routeNeoadjuvantNextStep:       stepRouteNeoadjuvantNextStep,
    interimRestagingCycle3:         stepInterimRestagingCycle3,
    chemoProtocolSwitchAndCompletion: stepChemoProtocolSwitchAndCompletion,
    repeatDebulkingAssessment:      stepRepeatDebulkingAssessment,
    therapyReevaluation:            stepTherapyReevaluation,
    routeOptimalDebulkingComplRestaging:    stepRouteOptimalDebulkingComplRestaging,
    routeOptimalDebulkingComplRepeatDebAss: stepRouteOptimalDebulkingComplRepeatDebAss,
    optimalDebulkingChemoCompl:     stepOptimalDebulkingChemoCompl,
    routeSystemDoneNeoadj:          stepRouteSystemDoneNeoadj,
    adjuvantTherapyMapping:         stepAdjuvantTherapyMapping,
    adjuvantTherapy:                stepAdjuvantTherapy,
    adjuvantNextStepMapping:        stepAdjuvantNextStepMapping,
    routeAdjuvantNextStep:          stepRouteAdjuvantNextStep,
    routeSystemDoneAdj:             stepRouteSystemDoneAdj,
    routeFollowUpCareMaintTh:       stepRouteFollowUpCareMaintTh,
    routeFollowUpCareSystTh:        stepRouteFollowUpCareSystTh,
    followUpCare:                   stepFollowUpCare,
    maintenanceTherapyMapping:      stepMaintenanceTherapyMapping,
    maintenanceTherapy:             stepMaintenanceTherapy

  } AS s
}



// provides_fact (sonography → B/M)
WITH s, [
  "B1_unilokulaer","B2_solide_lt7mm","B3_schallschatten",
  "B4_glatt_multilok_lt10cm","B5_keine_doppler_flow",
  "M1_unreg_solid","M2_ascites","M3_ge4_papillae",
  "M4_unreg_multilok_solid_gt10cm","M5_hoher_doppler_flow",
  "ca125_u_ml", "size_cm"
] AS bmKeys
UNWIND bmKeys AS k
MERGE (bmKey:FactKey {key:k})
WITH s, bmKey, s.sonography AS stepSonography, s.iota AS stepIota
MERGE (stepSonography)-[:PROVIDES_FACT]->(bmKey)
//
WITH s, [
  "praemenopausal", "symptoms_present", "growth",
  "persistence", "complex_multiloculaer",
  "psychic_unsure"
] AS bmKeys
UNWIND bmKeys AS k
MERGE (bmKey:FactKey {key:k})
WITH s, bmKey, s.sonography AS stepSonography, s.iota AS stepIota
MERGE (stepSonography)-[:PROVIDES_FACT {hard:true}]->(bmKey)


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
MERGE (stepCystectomy)-[:PROVIDES_FACT {hard:true}]->(fkCystectomyHistology)
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
MERGE (stepAdnexectomy)-[:PROVIDES_FACT {hard:true}]->(fkAdnexectomyHistology)
MERGE (stepRouteFollowUpAdnex)-[:REQUIRES_FACT {value:"benigne"}]->(fkAdnexectomyHistology)
MERGE (stepRouteDebulkingAssAdnexectomy)-[:REQUIRES_FACT {value:"maligne"}]->(fkAdnexectomyHistology)

WITH s
MERGE (fkRouteFollowUp:FactKey {key:"route_follow_up"})
WITH s, fkRouteFollowUp, s.routeFollowUpOp AS stepRouteFollowUpOp, s.routeFollowUpCystectomy AS stepRouteFollowUpCystectomy, s.routeFollowUpAdnex AS stepRouteFollowUpAdnex, s.follow AS stepFollow, s.routeFollowUpLaparotomy AS stepRouteFollowUpLaparotomy, s.routeFollowUpLaparoscopy AS stepRouteFollowUpLaparoscopy
MERGE (stepRouteFollowUpOp)-[:PROVIDES_FACT]->(fkRouteFollowUp)
MERGE (stepRouteFollowUpCystectomy)-[:PROVIDES_FACT]->(fkRouteFollowUp)
MERGE (stepRouteFollowUpAdnex)-[:PROVIDES_FACT]->(fkRouteFollowUp)
MERGE (stepRouteFollowUpLaparotomy)-[:PROVIDES_FACT]->(fkRouteFollowUp)
MERGE (stepRouteFollowUpLaparoscopy)-[:PROVIDES_FACT]->(fkRouteFollowUp)
MERGE (stepFollow)-[:REQUIRES_FACT {value:true}]->(fkRouteFollowUp)

// Right path of IOTA
WITH s
MERGE (fkFigoClinical:FactKey {key:"figo_clinical"})
WITH s, fkFigoClinical, s.ct AS stepCT, s.figo AS stepFIGO
MERGE (stepCT)-[:PROVIDES_FACT {hard:true}]->(fkFigoClinical)
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
WITH s, fkLaparotomyGrade, fkLaparotomyFigoPath, fkLaparotomyHistology, s.laparotomy AS stepLaparotomy, s.routeFollowUpLaparotomy AS stepRouteFollowUpLaparotomy
MERGE (stepLaparotomy)-[:PROVIDES_FACT]->(fkLaparotomyGrade)
MERGE (stepLaparotomy)-[:PROVIDES_FACT]->(fkLaparotomyFigoPath)
MERGE (stepLaparotomy)-[:PROVIDES_FACT {hard:true}]->(fkLaparotomyHistology)
MERGE (stepRouteFollowUpLaparotomy)-[:REQUIRES_FACT {value:"benigne"}]->(fkLaparotomyHistology)


WITH s
MATCH (fkLapEv:FactKey {key:"ev_laparotomy_done"})
WITH s, fkLapEv, s.routeInterdTbLaparotomy as stepRouteInterdTbLaparotomy
MERGE (stepRouteInterdTbLaparotomy)-[:REQUIRES_FACT {value:true}]->(fkLapEv)

WITH s
MERGE (fkLaparoscopyGrade:FactKey {key:"grade_laparoscopy"})
MERGE (fkLaparoscopyFigoPath:FactKey {key:"figo_path_laparoscopy"})
MERGE (fkLaparoscopyHistology:FactKey {key:"histology_laparoscopy"})
WITH s, fkLaparoscopyGrade, fkLaparoscopyFigoPath, fkLaparoscopyHistology, s.laparoscopy AS stepLaparoscopy, s.routeFollowUpLaparoscopy AS stepRouteFollowUpLaparoscopy
MERGE (stepLaparoscopy)-[:PROVIDES_FACT]->(fkLaparoscopyGrade)
MERGE (stepLaparoscopy)-[:PROVIDES_FACT]->(fkLaparoscopyFigoPath)
MERGE (stepLaparoscopy)-[:PROVIDES_FACT {hard:true}]->(fkLaparoscopyHistology)
MERGE (stepRouteFollowUpLaparoscopy)-[:REQUIRES_FACT {value:"benigne"}]->(fkLaparoscopyHistology)

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

// Humangenetische Beratung
WITH s
MERGE (fkgBRCA:FactKey {key:"gBRCA1/2"})
WITH s, fkgBRCA, s.geneticCounselingGermlineBRCA AS stepGeneticCounselingGermlineBRCA, s.tumorHRDTesting AS stepTumorHRDTesting, s.brcaHrdResolver AS stepBrcaHrdResolver, s.routeBrcaHrdResolverGermline AS stepRouteBrcaHrdResolverGermline
MERGE (stepGeneticCounselingGermlineBRCA)-[:PROVIDES_FACT {hard:true}]->(fkgBRCA)
MERGE (stepTumorHRDTesting)-[:REQUIRES_FACT {value:"-"}]->(fkgBRCA)
MERGE (stepRouteBrcaHrdResolverGermline)-[:REQUIRES_FACT {value:"+"}]->(fkgBRCA)
MERGE (stepBrcaHrdResolver)-[:NEEDS_FACT]->(fkgBRCA)

WITH s
MERGE (fksBRCA:FactKey {key:"sBRCA1/2"})
MERGE (fksHRD:FactKey {key:"sHRD"})
WITH s, fksBRCA, fksHRD, s.tumorHRDTesting AS stepTumorHRDTesting, s.brcaHrdResolver AS stepBrcaHrdResolver, s.routeBrcaHrdResolverHRDTesting AS stepRouteBrcaHrdResolverHRDTesting
MERGE (stepTumorHRDTesting)-[:PROVIDES_FACT {hard:true}]->(fksBRCA)
MERGE (stepTumorHRDTesting)-[:PROVIDES_FACT {hard:true}]->(fksHRD)
MERGE (stepRouteBrcaHrdResolverHRDTesting)-[:NEEDS_FACT]->(fksBRCA)
MERGE (stepRouteBrcaHrdResolverHRDTesting)-[:NEEDS_FACT]->(fksHRD)

WITH s
MERGE (fkRouteHrcBrcaResolver:FactKey {key:"route_hrd_brca_resolver"})
WITH s, fkRouteHrcBrcaResolver, s.brcaHrdResolver AS stepBrcaHrdResolver, s.routeBrcaHrdResolverHRDTesting AS stepRouteBrcaHrdResolverHRDTesting, s.routeBrcaHrdResolverGermline AS stepRouteBrcaHrdResolverGermline
MERGE (stepRouteBrcaHrdResolverGermline)-[:PROVIDES_FACT]->(fkRouteHrcBrcaResolver)
MERGE (stepRouteBrcaHrdResolverHRDTesting)-[:PROVIDES_FACT]->(fkRouteHrcBrcaResolver)
MERGE (stepBrcaHrdResolver)-[:REQUIRES_FACT {value:true}]->(fkRouteHrcBrcaResolver)


WITH s
MERGE (fkHRDStatus:FactKey {key:"hrd_status"})
MERGE (fkBRCAStatus:FactKey {key:"brca_status"})
WITH s, fkHRDStatus, fkBRCAStatus, s.brcaHrdResolver AS stepBrcaHrdResolver, s.parallelJoin AS stepParallelJoin
MERGE (stepBrcaHrdResolver)-[:PROVIDES_FACT]->(fkHRDStatus)
MERGE (stepBrcaHrdResolver)-[:PROVIDES_FACT]->(fkBRCAStatus)
MERGE (stepParallelJoin)-[:NEEDS_FACT]->(fkHRDStatus)
MERGE (stepParallelJoin)-[:NEEDS_FACT]->(fkBRCAStatus)

// Systemtherapie Adjuvant
WITH s
MERGE (fkPlanStrategyAdj:FactKey {key:"plan_strategy_adjuvant"})
MERGE (fkPlanNextStepAdj:FactKey {key:"plan_next_step_adjuvant"})
WITH s, fkPlanStrategyAdj, fkPlanNextStepAdj, s.adjuvantTherapyMapping AS stepAdjuvantTherapyMapping
MERGE (stepAdjuvantTherapyMapping)-[:PROVIDES_FACT]->(fkPlanStrategyAdj)
MERGE (stepAdjuvantTherapyMapping)-[:PROVIDES_FACT]->(fkPlanNextStepAdj)

WITH s
MERGE (fkStrategyAdjuvant:FactKey {key:"strategy_adjuvant"})
WITH s, fkStrategyAdjuvant, s.adjuvantTherapy AS stepAdjuvantTherapy, s.adjuvantNextStepMapping AS stepAdjuvantNextStepMapping
MERGE (stepAdjuvantTherapy)-[:PROVIDES_FACT {hard:true}]->(fkStrategyAdjuvant)
MERGE (stepAdjuvantNextStepMapping)-[:NEEDS_FACT]->(fkStrategyAdjuvant)

WITH s
MERGE (fkNextStepAdj:FactKey {key:"next_step_adjuvant"})
WITH s, fkNextStepAdj, s.adjuvantNextStepMapping AS stepAdjuvantNextStepMapping, s.routeAdjuvantNextStep AS stepRouteAdjuvantNextStep, s.routeSystemDoneAdj AS stepRouteSystemDoneAdj
MERGE (stepAdjuvantNextStepMapping)-[:PROVIDES_FACT]->(fkNextStepAdj)
MERGE (stepRouteAdjuvantNextStep)-[:NEEDS_FACT]->(fkNextStepAdj)
MERGE (stepRouteSystemDoneAdj)-[:NEEDS_FACT]->(fkNextStepAdj)

// Neoadjuvant
WITH s
MERGE (fkPlanStrategyNeoAdj:FactKey {key:"plan_strategy_neoadjuvant"})
MERGE (fkPlanNextStepNeoadj:FactKey {key:"plan_next_step_neoadjuvant"})
WITH s, fkPlanStrategyNeoAdj, fkPlanNextStepNeoadj, s.neoadjuvantTherapyMapping AS stepNeoadjuvantTherapyMapping
MERGE (stepNeoadjuvantTherapyMapping)-[:PROVIDES_FACT]->(fkPlanStrategyNeoAdj)
MERGE (stepNeoadjuvantTherapyMapping)-[:PROVIDES_FACT]->(fkPlanNextStepNeoadj)

WITH s
MERGE (fkStrategyNeoadjuvant:FactKey {key:"strategy_neoadjuvant"})
WITH s, fkStrategyNeoadjuvant, s.neoadjuvantTherapy AS stepNeoadjuvantTherapy, s.neoadjuvantNextStepMapping AS stepNeoadjuvantNextStepMapping
MERGE (stepNeoadjuvantTherapy)-[:PROVIDES_FACT {hard:true}]->(fkStrategyNeoadjuvant)
MERGE (stepNeoadjuvantNextStepMapping)-[:NEEDS_FACT]->(fkStrategyNeoadjuvant)

WITH s
MERGE (fkNextStepNeoadj:FactKey {key:"next_step_neoadjuvant"})
WITH s, fkNextStepNeoadj, s.neoadjuvantNextStepMapping AS stepNeoadjuvantNextStepMapping, s.routeNeoadjuvantNextStep AS stepRouteNeoadjuvantNextStep, s.routeSystemDoneNeoadj AS stepRouteSystemDoneNeoadj, s.interimRestagingCycle3 AS stepInterimRestagingCycle3
MERGE (stepNeoadjuvantNextStepMapping)-[:PROVIDES_FACT]->(fkNextStepNeoadj)
MERGE (stepRouteNeoadjuvantNextStep)-[:NEEDS_FACT]->(fkNextStepNeoadj)
MERGE (stepRouteSystemDoneNeoadj)-[:NEEDS_FACT]->(fkNextStepNeoadj)
MERGE (stepInterimRestagingCycle3)-[:NEEDS_FACT]->(fkNextStepNeoadj)

WITH s
MERGE (fkOperabelInterimNeoadj:FactKey {key:"operabel_interim_neoadjuvant"})
WITH s, fkOperabelInterimNeoadj, s.interimRestagingCycle3 AS stepInterimRestagingCycle3, s.chemoProtocolSwitchAndCompletion AS stepChemoProtocolSwitchAndCompletion, s.routeOptimalDebulkingComplRestaging AS stepRouteOptimalDebulkingComplRestaging
MERGE (stepInterimRestagingCycle3)-[:PROVIDES_FACT {hard:true}]->(fkOperabelInterimNeoadj)
MERGE (stepRouteOptimalDebulkingComplRestaging)-[:REQUIRES_FACT {value:true}]->(fkOperabelInterimNeoadj)
MERGE (stepChemoProtocolSwitchAndCompletion)-[:REQUIRES_FACT {value:false}]->(fkOperabelInterimNeoadj)


WITH s
MATCH (fkChemoSwitchCompletionEv:FactKey {key:"ev_chemo_protocol_switch_completion_done"})
WITH s, fkChemoSwitchCompletionEv, s.repeatDebulkingAssessment AS stepRepeatDebulkingAssessment
MERGE (stepRepeatDebulkingAssessment)-[:REQUIRES_FACT {value:true}]->(fkChemoSwitchCompletionEv)

WITH s
MERGE (fkRepeatedDebPoss:FactKey {key:"repeated_debulking_possible"})
WITH s, fkRepeatedDebPoss, s.repeatDebulkingAssessment AS stepRepeatDebulkingAssessment, s.routeOptimalDebulkingComplRepeatDebAss AS stepRouteOptimalDebulkingComplRepeatDebAss, s.therapyReevaluation AS stepTherapyReevaluation
MERGE (stepRepeatDebulkingAssessment)-[:PROVIDES_FACT]->(fkRepeatedDebPoss)
MERGE (stepRouteOptimalDebulkingComplRepeatDebAss)-[:REQUIRES_FACT {value:true}]->(fkRepeatedDebPoss)
MERGE (stepTherapyReevaluation)-[:REQUIRES_FACT {value:false}]->(fkRepeatedDebPoss)

WITH s
MERGE (fkRouteOptDeb:FactKey {key:"route_opt_debulking"})
WITH s, fkRouteOptDeb, s.optimalDebulkingChemoCompl AS stepOptimalDebulkingChemoCompl, s.routeOptimalDebulkingComplRestaging AS stepRouteOptimalDebulkingComplRestaging, s.routeOptimalDebulkingComplRepeatDebAss AS stepRouteOptimalDebulkingComplRepeatDebAss
MERGE (stepRouteOptimalDebulkingComplRepeatDebAss)-[:PROVIDES_FACT]->(fkRouteOptDeb)
MERGE (stepRouteOptimalDebulkingComplRestaging)-[:PROVIDES_FACT]->(fkRouteOptDeb)
MERGE (stepOptimalDebulkingChemoCompl)-[:REQUIRES_FACT {value:true}]->(fkRouteOptDeb)

WITH s
MATCH (fkOptDebChemoComplEv:FactKey {key:"ev_optimal_debulking_completion_done"})
WITH s, fkOptDebChemoComplEv, s.routeSystemDoneNeoadj AS stepRouteSystemDoneNeoadj
MERGE (stepRouteSystemDoneNeoadj)-[:REQUIRES_FACT {value:true}]->(fkOptDebChemoComplEv)

// Zusammenführung Systemtherapie
WITH s
MERGE (fkNextStepSystemTherapy:FactKey {key:"next_step_system_therapy"})
WITH s, fkNextStepSystemTherapy, s.routeAdjuvantNextStep AS stepRouteAdjuvantNextStep, s.routeNeoadjuvantNextStep AS stepRouteNeoadjuvantNextStep, s.parallelJoin AS stepParallelJoin, s.routeFollowUpCareSystTh AS stepRouteFollowUpCareSystTh, s.maintenanceTherapyMapping AS stepMaintenanceTherapyMapping, s.routeSystemDoneAdj AS stepRouteSystemDoneAdj
MERGE (stepRouteAdjuvantNextStep)-[:PROVIDES_FACT]->(fkNextStepSystemTherapy)
MERGE (stepRouteNeoadjuvantNextStep)-[:PROVIDES_FACT]->(fkNextStepSystemTherapy)
MERGE (stepRouteSystemDoneAdj)-[:NEEDS_FACT]->(fkNextStepSystemTherapy)
MERGE (stepParallelJoin)-[:NEEDS_FACT]->(fkNextStepSystemTherapy)
MERGE (stepRouteFollowUpCareSystTh)-[:REQUIRES_FACT {value:"Nachsorge"}]->(fkNextStepSystemTherapy)
MERGE (stepMaintenanceTherapyMapping)-[:REQUIRES_FACT {value:"Erhaltungstherapie"}]->(fkNextStepSystemTherapy)



WITH s
MERGE (fkSystemTherapyDone:FactKey {key:"route_system_therapy_done"})
WITH s, fkSystemTherapyDone, s.routeSystemDoneAdj AS stepRouteSystemDoneAdj, s.routeSystemDoneNeoadj AS stepRouteSystemDoneNeoadj, s.parallelJoin AS stepParallelJoin
MERGE (stepRouteSystemDoneAdj)-[:PROVIDES_FACT]->(fkSystemTherapyDone)
MERGE (stepRouteSystemDoneNeoadj)-[:PROVIDES_FACT]->(fkSystemTherapyDone)
MERGE (stepParallelJoin)-[:REQUIRES_FACT {value:true}]->(fkSystemTherapyDone)


WITH s
MERGE (fkParallelDone:FactKey {key:"paralleldone"})
WITH s, fkParallelDone, s.parallelJoin AS stepParallelJoin, s.routeFollowUpCareSystTh AS stepRouteFollowUpCareSystTh, s.maintenanceTherapyMapping AS stepMaintenanceTherapyMapping, s.maintenanceTherapy AS stepMaintenanceTherapy
MERGE (stepParallelJoin)-[:PROVIDES_FACT]->(fkParallelDone)
MERGE (stepMaintenanceTherapyMapping)-[:REQUIRES_FACT {value:true}]->(fkParallelDone)
MERGE (stepMaintenanceTherapy)-[:REQUIRES_FACT {value:true}]->(fkParallelDone)
MERGE (stepRouteFollowUpCareSystTh)-[:REQUIRES_FACT {value:true}]->(fkParallelDone)

// Erhaltungstherapie

WITH s
MERGE (fkFollowUpCare:FactKey {key:"route_follow_up_care"})
WITH s, fkFollowUpCare, s.routeFollowUpCareMaintTh AS stepRouteFollowUpCareMaintTh, s.routeFollowUpCareSystTh AS stepRouteFollowUpCareSystTh, s.followUpCare AS stepFollowUpCare
MERGE (stepRouteFollowUpCareMaintTh)-[:PROVIDES_FACT]->(fkFollowUpCare)
MERGE (stepRouteFollowUpCareSystTh)-[:PROVIDES_FACT]->(fkFollowUpCare)
MERGE (stepFollowUpCare)-[:REQUIRES_FACT {value:true}]->(fkFollowUpCare)

WITH s
MERGE (fkPlanStrategyMaintenance:FactKey {key:"plan_strategy_maintenance"})
WITH s, fkPlanStrategyMaintenance, s.maintenanceTherapyMapping AS stepMaintenanceTherapyMapping
MERGE (stepMaintenanceTherapyMapping)-[:PROVIDES_FACT]->(fkPlanStrategyMaintenance)

WITH s
MERGE (fkStrategyMaintenance:FactKey {key:"strategy_maintenance"})
WITH s, fkStrategyMaintenance, s.maintenanceTherapy AS stepMaintenanceTherapy, s.routeFollowUpCareMaintTh AS stepRouteFollowUpCareMaintTh
MERGE (stepMaintenanceTherapy)-[:PROVIDES_FACT {hard:true}]->(fkStrategyMaintenance)
MERGE (stepRouteFollowUpCareMaintTh)-[:REQUIRES_FACT {value:true}]->(fkStrategyMaintenance)
