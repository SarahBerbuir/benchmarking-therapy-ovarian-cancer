WITH $names AS names
CALL (names) {
 MERGE (stepIntake:Step:Info {name:names.intake})                  ON CREATE SET stepIntake.kind = "Info"
  MERGE (stepSonography:Step:Diagnostic {name:names.sonography})    ON CREATE SET stepSonography.kind = "Diagnostic"
  MERGE (stepIota:Step:Evaluator {name:names.iota})                 ON CREATE SET stepIota.kind = "Evaluator", stepIota.logic = "iota_simple_rules"

  MERGE (stepCystClassification:Step:Evaluator {name:names.cystClassification})
    ON CREATE SET stepCystClassification.kind = "Evaluator", stepCystClassification.logic = "bd_classification"
  MERGE (stepOpDecider:Step:Evaluator {name:names.opDecider})       ON CREATE SET stepOpDecider.kind = "Evaluator", stepOpDecider.logic = "set_op_plan"
   MERGE (stepRouteFollowUpOp:Step:Evaluator:Routing {name:names.routeFollowUpOp})
    ON CREATE SET stepRouteFollowUpOp.kind="Evaluator", stepRouteFollowUpOp.logic="set_route_flag"
  MERGE (stepCystectomy:Step:Therapy {name:names.cystectomy})       ON CREATE SET stepCystectomy.kind = "Therapy"
  MERGE (stepRouteFollowUpCystectomy:Step:Evaluator:Routing {name:names.routeFollowUpCystectomy})
    ON CREATE SET stepRouteFollowUpCystectomy.kind="Evaluator", stepRouteFollowUpCystectomy.logic="set_route_flag"
  MERGE (stepRouteAdnexectomyOpPlan:Step:Evaluator:Routing {name:names.routeAdnexectomyOpPlan})
    ON CREATE SET stepRouteAdnexectomyOpPlan.kind="Evaluator", stepRouteAdnexectomyOpPlan.logic="set_route_flag"
  MERGE (stepAdnexectomy:Step:Therapy {name:names.adnexectomy})     ON CREATE SET stepAdnexectomy.kind = "Therapy"
  MERGE (stepRouteFollowUpAdnex:Step:Evaluator:Routing {name:names.routeFollowUpAdnex})
    ON CREATE SET stepRouteFollowUpAdnex.kind="Evaluator", stepRouteFollowUpAdnex.logic="set_route_flag"
  MERGE (stepFollowUp:Step:Info {name:names.followUp})              ON CREATE SET stepFollowUp.kind = "Info"

  MERGE (stepCT:Step:Diagnostic {name:names.ct})                    ON CREATE SET stepCT.kind = "Diagnostic"
  MERGE (stepFIGOBucketer:Step:Evaluator {name:names.figoBucketer}) ON CREATE SET stepFIGOBucketer.kind = "Evaluator", stepFIGOBucketer.logic = "set_figo_bucket"
  MERGE (stepRouteAdnexectomyCFigo:Step:Evaluator:Routing {name:names.routeAdnexectomyCFigo})
    ON CREATE SET stepRouteAdnexectomyCFigo.kind="Evaluator", stepRouteAdnexectomyCFigo.logic="set_route_flag"

  MERGE (stepDebulkingAss:Step:Evaluator {name:names.debulkingAss}) ON CREATE SET stepDebulkingAss.kind = "Evaluator", stepDebulkingAss.logic = "set_debulking_possible"
  MERGE (stepRouteDebulkingAssFIGOBucket:Step:Evaluator:Routing {name:names.routeDebulkingAssFIGOBucket})
    ON CREATE SET stepRouteDebulkingAssFIGOBucket.kind="Evaluator", stepRouteDebulkingAssFIGOBucket.logic="set_route_flag"
  MERGE (stepRouteDebulkingAssCystectomy:Step:Evaluator:Routing {name:names.routeDebulkingAssCystectomy})
    ON CREATE SET stepRouteDebulkingAssCystectomy.kind="Evaluator", stepRouteDebulkingAssCystectomy.logic="set_route_flag"
  MERGE (stepRouteDebulkingAssAdnexectomy:Step:Evaluator:Routing {name:names.routeDebulkingAssAdnexectomy})
    ON CREATE SET stepRouteDebulkingAssAdnexectomy.kind="Evaluator", stepRouteDebulkingAssAdnexectomy.logic="set_route_flag"
  MERGE (stepFollowUpResectability:Step:Info {name:names.resectabilityEval})  ON CREATE SET stepFollowUpResectability.kind = "Info"

  MERGE (stepLaparotomy:Step:Therapy {name:names.laparotomy})       ON CREATE SET stepLaparotomy.kind = "Therapy"
  MERGE (stepLaparotomyPathology:Step:Evaluator {name:names.laparotomyPathology})
    ON CREATE SET stepLaparotomyPathology.kind = "Evaluator", stepLaparotomyPathology.logic = "resolve_path_stage_grade_lap"
  MERGE (stepRouteFollowUpLaparotomy:Step:Evaluator:Routing {name:names.routeFollowUpLaparotomy})
    ON CREATE SET stepRouteFollowUpLaparotomy.kind="Evaluator", stepRouteFollowUpLaparotomy.logic="set_route_flag"
  MERGE (stepRouteInterdTbLaparotomy:Step:Evaluator:Routing {name:names.routeInterdTbLaparotomy})
    ON CREATE SET stepRouteInterdTbLaparotomy.kind="Evaluator", stepRouteInterdTbLaparotomy.logic="set_route_flag"


  MERGE (stepLaparoscopy:Step:Therapy {name:names.laparoscopy})       ON CREATE SET stepLaparoscopy.kind = "Therapy"
    MERGE (stepLaparoscopyPathology:Step:Evaluator {name:names.laparoscopyPathology})
    ON CREATE SET stepLaparoscopyPathology.kind = "Evaluator", stepLaparoscopyPathology.logic = "resolve_path_stage_grade_lsk"
  MERGE (stepRouteFollowUpLaparoscopy:Step:Evaluator:Routing {name:names.routeFollowUpLaparoscopy})
    ON CREATE SET stepRouteFollowUpLaparoscopy.kind="Evaluator", stepRouteFollowUpLaparoscopy.logic="set_route_flag"
  MERGE (stepRouteInterdTbLaparoscopy:Step:Evaluator:Routing {name:names.routeInterdTbLaparoscopy})
    ON CREATE SET stepRouteInterdTbLaparoscopy.kind="Evaluator", stepRouteInterdTbLaparoscopy.logic="set_route_flag"

  MERGE (stepInterdTumorBoard:Step:Evaluator {name:names.interdTb})
    ON CREATE SET stepInterdTumorBoard.kind = "Evaluator", stepInterdTumorBoard.logic = "set_route_flag"

  MERGE (stepGeneticCounselingGermlineBRCA:Step:Diagnostic {name:names.geneticCounselingGermlineBrca}) ON CREATE SET stepGeneticCounselingGermlineBRCA.kind = "Diagnostic"
  MERGE (stepRouteBrcaHrdResolverGermline:Step:Evaluator:Routing {name:names.routeBrcaHrdResolverGermline})
    ON CREATE SET stepRouteBrcaHrdResolverGermline.kind="Evaluator", stepRouteBrcaHrdResolverGermline.logic="set_route_flag"

  MERGE (stepTumorHRDTesting:Step:Diagnostic {name:names.tumorHRDTesting}) ON CREATE SET stepTumorHRDTesting.kind = "Diagnostic"
  MERGE (stepRouteBrcaHrdResolverHRDTesting:Step:Evaluator:Routing {name:names.routeBrcaHrdResolverHRDTesting})
    ON CREATE SET stepRouteBrcaHrdResolverHRDTesting.kind="Evaluator", stepRouteBrcaHrdResolverHRDTesting.logic="set_route_flag"

  MERGE (stepBrcaHrdResolver:Step:Evaluator {name:names.hrcBrcaResolver})
    ON CREATE SET stepBrcaHrdResolver.kind="Evaluator", stepBrcaHrdResolver.logic="set_hrd_brca_status"

  MERGE (stepParallelJoin:Step:Evaluator:Routing {name:names.parallelJoin})
    ON CREATE SET stepParallelJoin.kind="Evaluator", stepParallelJoin.logic="set_route_flag"

  MERGE (stepNeoadjuvantTherapyMapping:Step:Evaluator {name:names.neoadjuvantTherapyMapping})
    ON CREATE SET stepNeoadjuvantTherapyMapping.kind="Evaluator", stepNeoadjuvantTherapyMapping.logic="set_planning_neoadjuvant_therapy"
  MERGE (stepNeoadjuvantTherapy:Step:Therapy {name:names.neoadjuvantTherapy})       ON CREATE SET stepNeoadjuvantTherapy.kind = "Therapy"
  MERGE (stepNeoadjuvantNextStepMapping:Step:Evaluator {name:names.nextStepMappingNeoAdj})
    ON CREATE SET stepNeoadjuvantNextStepMapping.kind="Evaluator", stepNeoadjuvantNextStepMapping.logic="set_neoadjuvant_next_step"
  MERGE (stepRouteNeoadjuvantNextStep:Step:Evaluator:Routing {name:names.routeNeoadjuvantNextStep})
    ON CREATE SET stepRouteNeoadjuvantNextStep.kind="Evaluator", stepRouteNeoadjuvantNextStep.logic="set_next_step_therapy"
  MERGE (stepInterimRestagingCycle3:Step:Diagnostic {name:names.interimRestagingCycle3}) ON CREATE SET stepInterimRestagingCycle3.kind = "Diagnostic"

  MERGE (stepChemoProtocolSwitchAndCompletion:Step:Therapy {name:names.chemoProtocolSwitchAndCompletion})       ON CREATE SET stepChemoProtocolSwitchAndCompletion.kind = "Therapy"
  MERGE (stepRepeatDebulkingAssessment:Step:Evaluator {name:names.repeatDebulkingAssessment})
    ON CREATE SET stepRepeatDebulkingAssessment.kind="Evaluator", stepRepeatDebulkingAssessment.logic="set_repeat_debulking_operabel_ass"
  MERGE (stepTherapyReevaluation:Step:Info {name:names.therapyReevaluation})  ON CREATE SET stepTherapyReevaluation.kind = "Info"

  MERGE (stepRouteOptimalDebulkingComplRestaging:Step:Evaluator:Routing {name:names.routeOptimalDebulkingComplRestaging})
    ON CREATE SET stepRouteOptimalDebulkingComplRestaging.kind="Evaluator", stepRouteOptimalDebulkingComplRestaging.logic="set_route_flag"
  MERGE (stepRouteOptimalDebulkingComplRepeatDebAss:Step:Evaluator:Routing {name:names.routeOptimalDebulkingComplRepeatDebAss})
    ON CREATE SET stepRouteOptimalDebulkingComplRepeatDebAss.kind="Evaluator", stepRouteOptimalDebulkingComplRepeatDebAss.logic="set_route_flag"
  MERGE (stepOptimalDebulkingChemoCompl:Step:Therapy {name:names.optimalDebulkingAndChemoCompletion})       ON CREATE SET stepOptimalDebulkingChemoCompl.kind = "Therapy"
  MERGE (stepRouteSystemDoneNeoadj:Step:Evaluator:Routing {name:names.routeSystemDoneNeoadj})
    ON CREATE SET stepRouteSystemDoneNeoadj.kind="Evaluator", stepRouteSystemDoneNeoadj.logic="set_route_flag"

  MERGE (stepAdjuvantTherapyMapping:Step:Evaluator {name:names.adjuvantTherapyMapping})
    ON CREATE SET stepAdjuvantTherapyMapping.kind="Evaluator", stepAdjuvantTherapyMapping.logic="set_planning_adjuvant_therapy"
  MERGE (stepAdjuvantTherapy:Step:Therapy {name:names.adjuvantTherapy})       ON CREATE SET stepAdjuvantTherapy.kind = "Therapy"
  MERGE (stepAdjuvantNextStepMapping:Step:Evaluator {name:names.nextStepMappingAdj})
    ON CREATE SET stepAdjuvantNextStepMapping.kind="Evaluator", stepAdjuvantNextStepMapping.logic="set_adjuvant_next_step"
  MERGE (stepRouteAdjuvantNextStep:Step:Evaluator:Routing {name:names.routeAdjuvantNextStep})
    ON CREATE SET stepRouteAdjuvantNextStep.kind="Evaluator", stepRouteAdjuvantNextStep.logic="set_next_step_therapy"
  MERGE (stepRouteSystemDoneAdj:Step:Evaluator:Routing {name:names.routeSystemDoneAdj})
    ON CREATE SET stepRouteSystemDoneAdj.kind="Evaluator", stepRouteSystemDoneAdj.logic="set_route_flag"

  MERGE (stepRouteFollowUpCareSystTh:Step:Evaluator:Routing {name:names.routeFollowUpCareSystTh})
    ON CREATE SET stepRouteFollowUpCareSystTh.kind="Evaluator", stepRouteFollowUpCareSystTh.logic="set_route_flag"
  MERGE (stepRouteFollowUpCareMaintTh:Step:Evaluator:Routing {name:names.routeFollowUpCareMaintTh})
    ON CREATE SET stepRouteFollowUpCareMaintTh.kind="Evaluator", stepRouteFollowUpCareMaintTh.logic="set_route_flag"

  MERGE (stepMaintenanceTherapyMapping:Step:Evaluator {name:names.maintenanceTherapyMapping})
    ON CREATE SET stepMaintenanceTherapyMapping.kind="Evaluator", stepMaintenanceTherapyMapping.logic="set_maintenance_therapy"
  MERGE (stepMaintenanceTherapy:Step:Therapy {name:names.maintenanceTherapy})       ON CREATE SET stepMaintenanceTherapy.kind = "Therapy"
MERGE (stepFollowUpCare:Step:Info {name:names.followUpCare})  ON CREATE SET stepFollowUpCare.kind = "Info"


  RETURN 1 AS ok
}
WITH ok, names
WITH [
  // 1: op_primary_benign
  names.cystectomy, names.adnexectomy
] AS benign, [
  // 2: op_primary_maligne
  names.laparotomy, names.laparoscopy
] AS malignant, [
  // 3: systematic_therapy
  names.neoadjuvantTherapy, names.adjuvantTherapy
] AS systh, [
  // 4: interim_restaging
  names.interimRestagingCycle3
] AS restaging, [
  // 5: optimales_debulking_neoadjuvant
  names.optimalDebulkingAndChemoCompletion
] AS optdeb, [
  // 5: optimales_debulking_neoadjuvant
  names.parallelJoin
] AS paralleljoin, [
  // 6: erhaltungs_therapy
  names.maintenanceTherapy
] AS maint

FOREACH (n IN benign    | MERGE (s:Step {name:n}) SET s.phase = 1)
FOREACH (n IN malignant | MERGE (s:Step {name:n}) SET s.phase = 2)
FOREACH (n IN systh     | MERGE (s:Step {name:n}) SET s.phase = 3)
FOREACH (n IN restaging | MERGE (s:Step {name:n}) SET s.phase = 4)
FOREACH (n IN optdeb    | MERGE (s:Step {name:n}) SET s.phase = 5)
FOREACH (n IN paralleljoin    | MERGE (s:Step {name:n}) SET s.phase = 6)
FOREACH (n IN maint     | MERGE (s:Step {name:n}) SET s.phase = 7);
