B_KEYS = [
    "B1_unilokulaer",
    "B2_solide_lt7mm",
    "B3_schallschatten",
    "B4_glatt_multilok_lt10cm",
    "B5_keine_doppler_flow",
]

M_KEYS = [
    "M1_unreg_solid",
    "M2_ascites",
    "M3_ge4_papillae",
    "M4_unreg_multilok_solid_gt10cm",
    "M5_hoher_doppler_flow",
]

def iota_simple_rules(facts: dict) -> str:
    # True, False/None/"unknown" don´t count
    b = sum(1 for k in B_KEYS if facts.get(k) is True)
    m = sum(1 for k in M_KEYS if facts.get(k) is True)

    values = [facts.get(k) for k in (B_KEYS + M_KEYS)]
    any_known = any(v is True or v is False for v in values)

    if  not any_known:
        iota_res = "unknown"
    elif m >= 1 and b == 0:
        iota_res = "maligne_wahrscheinlich"
    elif m > b:
        iota_res = "maligne_wahrscheinlich"
    elif b >= 1 and m == 0:
        iota_res = "benigne_wahrscheinlich"
    else:
        # b==0 and m==0, b>=m
        iota_res = "nicht_klassifizierbar"

    print(f"Count benign: {b}, Count malignant: {m}, Iota: {iota_res}")
    return iota_res
