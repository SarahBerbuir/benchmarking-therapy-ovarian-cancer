WITH $names AS names
CALL (names) {
  MATCH (son:Step {name:names.sonography})
  MATCH (ct:Step  {name:names.ct})
  MATCH (cys:Step {name:names.cystectomy})
  MATCH (adn:Step {name:names.adnexectomy})
  MATCH (lap:Step {name:names.laparotomy})
  MATCH (lscp:Step {name:names.laparoscopy})
  MATCH (gc:Step {name:names.geneticCounselingGermlineBrca})
  MATCH (hrd:Step {name:names.tumorHRDTesting})
  MATCH (neo:Step {name:names.neoadjuvantTherapy})
  MATCH (adj:Step {name:names.adjuvantTherapy})
  MATCH (swc:Step {name:names.chemoProtocolSwitchAndCompletion})
  MATCH (irc:Step {name:names.interimRestagingCycle3})
  MATCH (odcc:Step {name:names.optimalDebulkingAndChemoCompletion})
  MATCH (mt:Step {name:names.maintenanceTherapy})

  RETURN {
    sonography:son, ct:ct, cystectomy:cys, adnexectomy:adn,
    laparotomy:lap, laparoscopy:lscp, genetic:gc, hrd:hrd,
    neo:neo, adj:adj, switchCompl:swc, interimrestaging:irc, optDebCC:odcc, maintTh: mt
  } AS s
}
WITH s
UNWIND [
  ["ev_sonography_present", s.sonography],
  ["ev_ct_present",         s.ct],
  ["ev_cystectomy_done",    s.cystectomy],
  ["ev_adnexectomy_done",   s.adnexectomy],
  ["ev_laparotomy_done",    s.laparotomy],
  ["ev_laparoscopy_done",   s.laparoscopy],
  ["ev_genetic_counseling_done", s.genetic],
  ["ev_hrd_test_done",      s.hrd],
  ["ev_neoadjuvant_therapy_done", s.neo],
  ["ev_adjuvant_therapy_done",    s.adj],
  ["ev_interim_restaging_3_done", s.interimrestaging],
  ["ev_chemo_protocol_switch_completion_done", s.switchCompl],
  ["ev_optimal_debulking_completion_done", s.optDebCC],
  ["ev_maintenance_therapy_done", s.maintTh]


] AS pair
WITH pair[0] AS key, pair[1] AS step
MERGE (fk:FactKey {key:key})
MERGE (step)-[:EVIDENCE_HINTS]->(fk);

WITH $names AS names
UNWIND [
  [names.intake, names.sonography],
  [names.sonography, names.iota],
  [names.iota, names.cystClassification],
  [names.iota, names.ct],

  // left path from iota
  [names.cystClassification, names.opDecider],

  [names.opDecider, names.routeFollowUpOp],
  [names.opDecider, names.cystectomy],
  [names.opDecider, names.routeAdnexectomyOpPlan],

  [names.routeAdnexectomyOpPlan, names.adnexectomy],

  [names.cystectomy, names.routeFollowUpCystectomy],
  [names.routeFollowUpCystectomy, names.followUp],

  [names.adnexectomy, names.routeFollowUpAdnex],
  [names.routeFollowUpAdnex, names.followUp],

  [names.routeFollowUpOp, names.followUp],

  //right path from iota
  [names.ct, names.figoBucketer],

  [names.figoBucketer, names.routeAdnexectomyCFigo],
  [names.routeAdnexectomyCFigo, names.adnexectomy],

  [names.figoBucketer, names.routeDebulkingAssFIGOBucket],
  [names.routeDebulkingAssFIGOBucket, names.debulkingAss],

  [names.cystectomy, names.routeDebulkingAssCystectomy],
  [names.routeDebulkingAssCystectomy, names.debulkingAss],

  [names.adnexectomy, names.routeDebulkingAssAdnexectomy],
  [names.routeDebulkingAssAdnexectomy, names.debulkingAss],

  [names.debulkingAss, names.resectabilityEval],
  [names.debulkingAss, names.laparotomy],
  [names.debulkingAss, names.laparoscopy],

  [names.laparotomy, names.routeFollowUpLaparotomy],
  [names.routeFollowUpLaparotomy, names.followUp],

  [names.laparotomy, names.routeInterdTbLaparotomy],
  [names.routeInterdTbLaparotomy, names.interdTb],

  [names.laparoscopy, names.routeFollowUpLaparoscopy],
  [names.routeFollowUpLaparoscopy, names.followUp],

  [names.laparoscopy, names.routeInterdTbLaparoscopy],
  [names.routeInterdTbLaparoscopy, names.interdTb],

  [names.interdTb, names.geneticCounselingGermlineBrca],

  // Humangenetische Beratung
  [names.geneticCounselingGermlineBrca, names.tumorHRDTesting],
  [names.tumorHRDTesting, names.routeBrcaHrdResolverHRDTesting],
  [names.routeBrcaHrdResolverHRDTesting, names.hrcBrcaResolver],
  [names.geneticCounselingGermlineBrca, names.routeBrcaHrdResolverGermline],
  [names.routeBrcaHrdResolverGermline, names.hrcBrcaResolver],

  [names.hrcBrcaResolver, names.parallelJoin],

  // Adjuvante Therapie
  [names.interdTb, names.adjuvantTherapyMapping],
  [names.adjuvantTherapyMapping, names.adjuvantTherapy],
  [names.adjuvantTherapy, names.nextStepMappingAdj],

  [names.nextStepMappingAdj, names.routeAdjuvantNextStep],
  [names.routeAdjuvantNextStep, names.parallelJoin],

  [names.nextStepMappingAdj, names.routeSystemDoneAdj],
  [names.routeSystemDoneAdj, names.parallelJoin],

  // Neoadjuvante Therapie
  [names.interdTb, names.neoadjuvantTherapyMapping],
  [names.neoadjuvantTherapyMapping, names.neoadjuvantTherapy],
  [names.neoadjuvantTherapy, names.nextStepMappingNeoAdj],

  [names.nextStepMappingNeoAdj, names.routeNeoadjuvantNextStep],
  [names.routeNeoadjuvantNextStep, names.parallelJoin],

  [names.nextStepMappingNeoAdj, names.routeSystemDoneNeoadj],

  [names.nextStepMappingNeoAdj, names.interimRestagingCycle3],
  [names.interimRestagingCycle3, names.chemoProtocolSwitchAndCompletion],
  [names.chemoProtocolSwitchAndCompletion, names.repeatDebulkingAssessment],

  [names.repeatDebulkingAssessment, names.therapyReevaluation],
  [names.repeatDebulkingAssessment, names.routeOptimalDebulkingComplRepeatDebAss],
  [names.routeOptimalDebulkingComplRepeatDebAss, names.optimalDebulkingAndChemoCompletion],

  [names.interimRestagingCycle3, names.routeOptimalDebulkingComplRestaging],
  [names.routeOptimalDebulkingComplRestaging, names.optimalDebulkingAndChemoCompletion],

  [names.optimalDebulkingAndChemoCompletion, names.routeSystemDoneNeoadj],
  [names.routeSystemDoneNeoadj, names.parallelJoin],

  // Erhaltungstherapie
  [names.parallelJoin, names.routeFollowUpCareSystTh],
  [names.routeFollowUpCareSystTh, names.followUpCare],

  [names.parallelJoin, names.maintenanceTherapyMapping],
  [names.maintenanceTherapyMapping, names.maintenanceTherapy],
  [names.maintenanceTherapy, names.routeFollowUpCareMaintTh],
  [names.routeFollowUpCareMaintTh, names.followUpCare]




] AS e
MATCH (a:Step {name:e[0]}), (b:Step {name:e[1]})
MERGE (a)-[:NEXT]->(b)
RETURN count(*) AS edges_upserted;
