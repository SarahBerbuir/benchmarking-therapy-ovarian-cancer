// === FIGO IA G1 → OP ===
MERGE (s1:Stage {name: "FIGO IA G1"})
MERGE (op1:Therapy {name: "OP (FIGO IA G1)"})
MERGE (s1)-[:RECOMMENDED_TREATMENT]->(op1)


// === FIGO IA G2, IB G1AC/2 → OP → ggf. 6x Carboplatin ===
MERGE (s2:Stage {name: "FIGO IA G2, IB G1AC/2"})
MERGE (op2:Therapy {name: "OP (FIGO IA G2/IB)"})
MERGE (carbo:Therapy {name: "6x Carboplatin"})
MERGE (s2)-[:RECOMMENDED_TREATMENT]->(op2)
MERGE (op2)-[:OPTIONAL_FOLLOW_UP]->(carbo)


// === FIGO IC o. IA/B und G3 → OP → 6x Carboplatin ===
MERGE (s3:Stage {name: "FIGO IC o. IA/B und G3"})
MERGE (op3:Therapy {name: "OP (FIGO IC/G3)"})
MERGE (s3)-[:RECOMMENDED_TREATMENT]->(op3)
MERGE (op3)-[:FOLLOWED_BY]->(carbo)


// === FIGO II → OP → 6x Carboplatin / Paclitaxel ===
MERGE (s4:Stage {name: "FIGO II"})
MERGE (op4:Therapy {name: "OP (FIGO II)"})
MERGE (carbo_pacli:Therapy {name: "6x Carboplatin / Paclitaxel"})
MERGE (s4)-[:RECOMMENDED_TREATMENT]->(op4)
MERGE (op4)-[:FOLLOWED_BY]->(carbo_pacli)

// === FIGO III–IV ===
MERGE (s5:Stage {name: "FIGO III–IV"})
MERGE (op5:Therapy {name: "OP (FIGO III–IV)"})
MERGE (s5)-[:RECOMMENDED_TREATMENT]->(op5)

// === Subtypes ===
MERGE (lowgrade:Subtype {name: "Low-grade"})
MERGE (highgrade:Subtype {name: "High-grade"})

MERGE (op5)-[:LEADS_TO_SUBTYPE]->(lowgrade)
MERGE (op5)-[:LEADS_TO_SUBTYPE]->(highgrade)

// === Low-grade Behandlung ===
MERGE (low_chemo:Therapy {name: "6x Carboplatin / Paclitaxel (Low-grade)"})
MERGE (lowgrade)-[:RECOMMENDED_TREATMENT]->(low_chemo)

// === BRCA+ / HRD+ ===
MERGE (brca_pos_hrd_pos:Subtype {name: "BRCA+ / HRD+"})
MERGE (highgrade)-[:HAS_SUBGROUP]->(brca_pos_hrd_pos)

// === Erstlinientherapien ===
MERGE (chemo_std_brca_pos:Therapy {name: "6x Carboplatin / Paclitaxel (BRCA+/HRD+)"})
MERGE (chemo_bev_brca_pos:Therapy {name: "6x Carboplatin / Paclitaxel + Bevacizumab (BRCA+/HRD+)"})
MERGE (brca_pos_hrd_pos)-[:RECOMMENDED_TREATMENT]->(chemo_std_brca_pos)
MERGE (brca_pos_hrd_pos)-[:RECOMMENDED_TREATMENT]->(chemo_bev_brca_pos)

// === Erhaltungstherapien ===
MERGE (bev_olap:Therapy {name: "Bevacizumab + Olaparib"})
MERGE (olaparib:Therapy {name: "Olaparib"})
MERGE (bevacizumab:Therapy {name: "Bevacizumab"})
MERGE (niraparib:Therapy {name: "Niraparib"})


FOREACH (t IN [chemo_std_brca_pos, chemo_bev_brca_pos] |
    MERGE (t)-[:FOLLOWED_BY]->(bev_olap)
    MERGE (t)-[:FOLLOWED_BY]->(olaparib)
    MERGE (t)-[:FOLLOWED_BY]->(bevacizumab)
    MERGE (t)-[:FOLLOWED_BY]->(niraparib)
)

// === BRCA- / HRD+ ===
MERGE (brca_neg_hrd_pos:Subtype {name: "BRCA- / HRD+"})
MERGE (highgrade)-[:HAS_SUBGROUP]->(brca_neg_hrd_pos)

// === Erstlinientherapien ===
MERGE (chemo_std_brca_neg:Therapy {name: "6x Carboplatin / Paclitaxel (BRCA-/HRD+)"})
MERGE (chemo_bev_brca_neg:Therapy {name: "6x Carboplatin / Paclitaxel + Bevacizumab (BRCA-/HRD+)"})
MERGE (brca_neg_hrd_pos)-[:RECOMMENDED_TREATMENT]->(chemo_std_brca_neg)
MERGE (brca_neg_hrd_pos)-[:RECOMMENDED_TREATMENT]->(chemo_bev_brca_neg)

// === Erhaltungstherapie ===
FOREACH (t IN [chemo_std_brca_neg, chemo_bev_brca_neg] |
    MERGE (t)-[:FOLLOWED_BY]->(bev_olap)
    MERGE (t)-[:FOLLOWED_BY]->(olaparib)
    MERGE (t)-[:FOLLOWED_BY]->(bevacizumab)
    MERGE (t)-[:FOLLOWED_BY]->(niraparib)
)

// === HRD- ===
MERGE (hrd_neg:Subtype {name: "HRD-"})
MERGE (highgrade)-[:HAS_SUBGROUP]->(hrd_neg)

MERGE (chemo_bev_hrd_neg:Therapy {name: "6x Carboplatin / Paclitaxel + Bevacizumab (HRD-)"})
MERGE (hrd_neg)-[:RECOMMENDED_TREATMENT]->(chemo_bev_hrd_neg)

// === Erhaltungstherapie ===
MERGE (chemo_bev_hrd_neg)-[:FOLLOWED_BY]->(bevacizumab)
MERGE (chemo_bev_hrd_neg)-[:FOLLOWED_BY]->(niraparib)
