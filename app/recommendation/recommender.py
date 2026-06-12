import re
from app.recommendation.search import search_products
from app.recommendation.ranking import rerank

INTENT_SEARCH   = "search"
INTENT_BUDGET   = "budget_filter"
INTENT_BRAND    = "brand_filter"
INTENT_FOLLOWUP = "followup"
INTENT_COMPARE  = "compare"

_sessions: dict = {}

# ── Keyword groups: if user says X, product must contain one of the values ──
# Built from actual dataset analysis (103 wireless, 50 wired, 103 bluetooth, etc.)
KEYWORD_GROUPS = {
    # Audio
    "wireless"        : ["wireless", "bluetooth", "tws", "true wireless", "wi-fi"],
    "wired"           : ["wired", "3.5mm", "aux", "jack"],
    "bluetooth"       : ["bluetooth", "wireless", "tws", "true wireless"],
    "tws"             : ["tws", "true wireless", "truly wireless"],
    "true wireless"   : ["tws", "true wireless", "truly wireless"],
    "neckband"        : ["neckband", "neck band", "around neck"],
    "noise cancelling": ["noise cancel", "anc", "active noise"],
    "noise canceling" : ["noise cancel", "anc", "active noise"],
    "in-ear"          : ["in-ear", "in ear", "earbuds", "earbud"],
    "over-ear"        : ["over-ear", "over ear", "headphone"],
    "on-ear"          : ["on-ear", "on ear"],

    # Cables & Charging
    "type-c"          : ["type-c", "type c", "usb-c", "usb c"],
    "type c"          : ["type-c", "type c", "usb-c", "usb c"],
    "lightning"       : ["lightning", "iphone", "apple"],
    "fast charging"   : ["fast charg", "quick charg", "rapid charg", "pd charg"],
    "braided"         : ["braided", "nylon braided", "nylon"],
    "hdmi"            : ["hdmi", "4k", "8k"],

    # Display & TV
    "smart tv"        : ["smart tv", "smart led", "android tv", "smart television"],
    "android tv"      : ["android tv", "google tv"],
    "4k"              : ["4k", "uhd", "ultra hd", "3840"],
    "hd"              : ["hd", "1080p", "720p", "full hd", "hd ready"],
    "oled"            : ["oled"],
    "qled"            : ["qled"],
    "led"             : ["led"],
    "projector"       : ["projector"],

    # Computing
    "gaming"          : ["gaming", "game", "rgb", "mechanical", "esports"],
    "mechanical"      : ["mechanical", "mech"],
    "wireless mouse"  : ["wireless", "bluetooth"],
    "ergonomic"       : ["ergonomic", "ergo"],
    "ssd"             : ["ssd", "solid state", "nvme", "m.2"],
    "hard disk"       : ["hard disk", "hdd", "hard drive", "external drive"],
    "pen drive"       : ["pen drive", "usb drive", "flash drive", "thumb drive"],
    "memory card"     : ["memory card", "microsd", "sd card", "micro sd"],

    # Laptop
    "touchscreen"     : ["touchscreen", "touch screen", "touch display"],
    "backlit"         : ["backlit", "back lit", "rgb backlit"],

    # Mobile
    "5g"              : ["5g"],
    "4g"              : ["4g", "lte"],
    "dual sim"        : ["dual sim"],
    "foldable"        : ["foldable", "fold"],

    # Home appliances
    "portable"        : ["portable", "travel", "compact"],
    "waterproof"      : ["waterproof", "water resistant", "ipx", "water proof"],
    "water resistant" : ["water resistant", "waterproof", "ipx", "splash proof"],
    "cordless"        : ["cordless", "wireless", "battery operated"],
    "rechargeable"    : ["rechargeable", "lithium", "battery"],
    "solar"           : ["solar"],
    "smart"           : ["smart", "wi-fi", "wifi", "app control", "alexa", "google"],

    # Kitchen
    "mixer"           : ["mixer", "grinder", "blender", "juicer"],
    "induction"       : ["induction"],
    "air fryer"       : ["air fryer", "airfryer"],
    "kettle"          : ["kettle", "hot water"],
    "iron"            : ["iron", "steam iron", "dry iron"],

    # Other
    "remote"          : ["remote", "remote control"],
    "usb"             : ["usb"],
    "power bank"      : ["power bank", "powerbank", "portable charger"],
    "router"          : ["router", "wi-fi router", "wifi router"],
    "webcam"          : ["webcam", "web camera"],
    "soundbar"        : ["soundbar", "sound bar"],
}

# ── Category map: keyword → main_category filter ────────────────────────────
CATEGORY_MAP = {
    # Electronics
    "earbuds"      : "Electronics",
    "earbud"       : "Electronics",
    "headphone"    : "Electronics",
    "headphones"   : "Electronics",
    "earphone"     : "Electronics",
    "speaker"      : "Electronics",
    "tv"           : "Electronics",
    "television"   : "Electronics",
    "smartwatch"   : "Electronics",
    "smart watch"  : "Electronics",
    "phone"        : "Electronics",
    "smartphone"   : "Electronics",
    "mobile"       : "Electronics",
    "projector"    : "Electronics",
    "camera"       : "Electronics",
    "remote"       : "Electronics",
    # Computers
    "laptop"       : "Computers&Accessories",
    "cable"        : "Computers&Accessories",
    "cables"       : "Computers&Accessories",
    "mouse"        : "Computers&Accessories",
    "keyboard"     : "Computers&Accessories",
    "monitor"      : "Computers&Accessories",
    "charger"      : "Computers&Accessories",
    "ssd"          : "Computers&Accessories",
    "hard disk"    : "Computers&Accessories",
    "pen drive"    : "Computers&Accessories",
    "memory card"  : "Computers&Accessories",
    "router"       : "Computers&Accessories",
    "webcam"       : "Computers&Accessories",
    "power bank"   : "Computers&Accessories",
    "tablet"       : "Computers&Accessories",
    # Home & Kitchen
    "mixer"        : "Home&Kitchen",
    "iron"         : "Home&Kitchen",
    "kettle"       : "Home&Kitchen",
    "heater"       : "Home&Kitchen",
    "fan"          : "Home&Kitchen",
    "vacuum"       : "Home&Kitchen",
    "air purifier" : "Home&Kitchen",
    "water purifier": "Home&Kitchen",
    "induction"    : "Home&Kitchen",
    "air fryer"    : "Home&Kitchen",
}

# ── Known brands ─────────────────────────────────────────────────────────────
KNOWN_BRANDS = [
    "samsung", "apple", "dell", "hp", "lenovo", "asus", "acer",
    "sony", "lg", "mi", "xiaomi", "realme", "oneplus", "boat",
    "jbl", "bose", "logitech", "corsair", "razer", "anker",
    "amazon", "google", "intel", "amd", "nvidia", "boult",
    "ptron", "zebronics", "portronics", "philips", "bajaj",
    "havells", "prestige", "butterfly", "inalsa", "usha",
    "dyson", "eureka", "kent", "aquaguard", "whirlpool",
    "seagate", "western digital", "wd", "sandisk", "kingston",
    "tplink", "tp-link", "dlink", "d-link", "netgear",
    "canon", "nikon", "epson", "brother", "casio",
    "noise", "firebolt", "fastrack", "titan", "fossil",
    "ibell", "syska", "wipro", "crompton",
]


def detect_intent(query: str) -> str:
    q = query.lower().strip()

    followup_patterns = [
        r"\b(cheaper|cheaper ones|lower price|more affordable)\b",
        r"\b(show more|more options|other options)\b",
        r"\b(better rating|higher rating|more stars|top rated)\b",
        r"\bonly\s+\w+\b",
        r"\bjust\s+\w+\b",
        r"\b(that|those|them|these)\b",
        r"\b(also|instead|alternative)\b",
    ]
    for pat in followup_patterns:
        if re.search(pat, q):
            return INTENT_FOLLOWUP

    if re.search(r"\bcompare\b|\bvs\b|\bversus\b|\bdifference between\b", q):
        return INTENT_COMPARE

    if re.search(r"(under|below|less than|within|upto|up to|₹|rs\.?)\s*[\d,]+", q):
        return INTENT_BUDGET

    if re.search(r"\b(only|just|from)\s+[A-Z][a-z]+", query):
        return INTENT_BRAND

    return INTENT_SEARCH


def extract_entities(query: str) -> dict:
    entities = {"budget": None, "brand": None, "category": None}
    q = query.lower()

    # Budget: "under 80000", "₹80k", "below 1.5 lakh", "rs 500"
    m = re.search(
        r"(under|below|less than|within|upto|up to|₹|rs\.?)\s*([\d,]+\.?\d*)\s*(k|lakh|l)?",
        q
    )
    if m:
        raw   = m.group(2).replace(",", "")
        unit  = (m.group(3) or "").lower()
        value = float(raw)
        if unit == "k":
            value *= 1000
        elif unit in ("lakh", "l"):
            value *= 100000
        entities["budget"] = value

    # Brand: check all known brands
    for brand in KNOWN_BRANDS:
        if brand in q:
            entities["brand"] = brand
            break

    # Category: check all category keywords
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in q:
            entities["category"] = cat
            break

    return entities


def _keyword_filter(products: list, query: str) -> list:
    """
    For every strong keyword in the user's query, ensure returned
    products actually contain that keyword (or a synonym) in
    product_name or about_product.

    Covers: wireless/wired, type-c/lightning, gaming, mechanical,
    waterproof, fast charging, neckband, tws, ssd, hdmi, etc.
    """
    q = query.lower()

    # Collect all keyword groups that match the query
    required_groups = []
    for kw, synonyms in KEYWORD_GROUPS.items():
        if kw in q:
            required_groups.append(synonyms)

    if not required_groups:
        return products  # no strong keywords → skip filter

    def product_matches_group(p: dict, group: list) -> bool:
        text = (
            p.get("product_name", "").lower() + " " +
            p.get("about_product", "").lower()
        )
        return any(syn in text for syn in group)

    # Product must satisfy ALL keyword groups found in query
    filtered = [
        p for p in products
        if all(product_matches_group(p, group) for group in required_groups)
    ]

    # Safety fallback: if filter removes everything return original
    return filtered if filtered else products


def get_session(session_id: str) -> dict:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "last_query"   : None,
            "last_intent"  : None,
            "last_entities": {},
            "last_results" : [],
        }
    return _sessions[session_id]


def update_session(session_id, query, intent, entities, results):
    _sessions[session_id] = {
        "last_query"   : query,
        "last_intent"  : intent,
        "last_entities": entities,
        "last_results" : results,
    }


def recommend(query: str, session_id: str = "default", top_k: int = 5) -> dict:
    intent   = detect_intent(query)
    entities = extract_entities(query)
    session  = get_session(session_id)

    # ── Follow-up: inherit previous session context ──────────
    if intent == INTENT_FOLLOWUP and session["last_query"]:
        prev = session["last_entities"]
        effective_query = session["last_query"]

        if entities["budget"] is None and prev.get("budget"):
            entities["budget"] = prev["budget"]

        # "cheaper" → 60% of previous budget
        if re.search(r"\bcheaper\b", query.lower()) and prev.get("budget"):
            entities["budget"] = prev["budget"] * 0.6

        # "higher rated" / "better rating" → set min_rating in search
        if re.search(r"\b(higher rating|better rating|top rated|more stars)\b", query.lower()):
            entities["min_rating"] = 4.0

        if entities["category"] is None and prev.get("category"):
            entities["category"] = prev["category"]

        if entities["brand"] is None and prev.get("brand"):
            entities["brand"] = prev["brand"]
    else:
        effective_query = query

    # ── Semantic search ───────────────────────────────────────
    raw_results = search_products(
        query          = effective_query,
        top_k          = top_k * 4,   # fetch extra buffer for filtering
        max_price      = entities.get("budget"),
        category_filter= entities.get("category"),
        min_rating     = entities.get("min_rating", 0.0),
    )

    # ── Keyword filter (wireless vs wired, type-c, gaming etc) ─
    raw_results = _keyword_filter(raw_results, effective_query)

    # ── Brand filter (post-search) ────────────────────────────
    if entities.get("brand"):
        brand = entities["brand"].lower()
        brand_filtered = [
            p for p in raw_results
            if brand in p.get("product_name", "").lower()
        ]
        # Safety: if brand filter removes everything, keep original
        raw_results = brand_filtered if brand_filtered else raw_results

    # ── Rerank by quality score ───────────────────────────────
    ranked = rerank(raw_results)[:top_k]

    update_session(session_id, query, intent, entities, ranked)

    return {
        "intent"  : intent,
        "entities": entities,
        "products": ranked,
    }