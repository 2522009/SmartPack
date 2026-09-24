"""
SmartPack shared packaging knowledge database + deterministic rule engine.

IMPORTANT:
- This is the single fast packaging knowledge source for both:
  1) Manufacturer Portal
  2) Recommendation page
- Do not put a second packaging decision table in app.py.
- SmartPack AI can explain/enrich the database result, but the database/rule
  engine remains the common baseline so both pages stay consistent.
- External sources below are reference sources, not approval of a specific
  package. Product-specific compatibility, compliance and shelf-life testing
  are still required.
"""

from copy import deepcopy


# ============================================================
# TRUSTED REFERENCE SOURCES
# ============================================================

AUTHORITATIVE_SOURCES = [
    {
        "source": "FSSAI",
        "title": "Food Safety and Standards (Packaging) Regulations",
        "url": "https://www.fssai.gov.in/food-law/regulations",
        "reason_used": (
            "Indian regulatory reference for food-contact packaging and "
            "applicable packaging requirements."
        ),
    },
    {
        "source": "U.S. FDA",
        "title": "Packaging & Food Contact Substances",
        "url": (
            "https://www.fda.gov/food/food-ingredients-packaging/"
            "packaging-food-contact-substances-fcs"
        ),
        "reason_used": (
            "Reference for food-contact substances and packaging safety."
        ),
    },
    {
        "source": "European Commission",
        "title": "Food Contact Materials",
        "url": (
            "https://food.ec.europa.eu/food-safety/chemical-safety/"
            "food-contact-materials_en"
        ),
        "reason_used": (
            "Reference for food-contact material safety and compliance."
        ),
    },
    {
        "source": "EFSA",
        "title": "European Food Safety Authority",
        "url": "https://www.efsa.europa.eu/",
        "reason_used": (
            "Scientific risk-assessment reference for food-contact materials."
        ),
    },
]


# ============================================================
# PACKAGING KNOWLEDGE
# ============================================================

def _record(
    name,
    packaging,
    material,
    aliases,
    requirements,
    benefits,
    why,
    tradeoffs,
    conditions,
):
    return {
        "name": name,
        "packaging": packaging,
        "material": material,
        "category_aliases": aliases,
        "requirements": requirements,
        "benefits": benefits,
        "why": why,
        "tradeoffs": tradeoffs,
        "conditions": conditions,
    }


PACKAGING_KNOWLEDGE = {

    # --------------------------------------------------------
    # SNACKS / NAMKEEN / GATHIYA / CHIPS / KHAKHRA
    # --------------------------------------------------------

    "snacks": _record(
        "High-barrier snack packaging",
        "High-barrier flexible pouch",
        "PET / Metallized PET / PE",
        [
            "snacks", "snack", "namkeen", "chips",
            "gathiya", "khakhra"
        ],
        [
            "Moisture barrier",
            "Oxygen barrier",
            "Good heat sealability",
            "Mechanical protection",
        ],
        [
            "Moisture protection",
            "Oxygen protection",
            "Good heat sealability",
            "Mechanical protection",
        ],
        [
            "Dry snack products benefit from moisture and oxygen protection.",
            "The high-barrier laminate helps limit environmental exposure.",
            "Heat sealing helps protect the filled pack.",
        ],
        [
            "Multilayer structures can have recycling limitations.",
            "Actual barrier performance depends on structure, thickness and seal quality.",
        ],
        {
            "moisture_high": 12,
            "moisture_medium": 6,
            "oxygen_high": 12,
            "oxygen_medium": 6,
            "light_high": 5,
            "perishability_high": 4,
        },
    ),

    # --------------------------------------------------------
    # DRY FRUITS / NUTS
    # --------------------------------------------------------

    "dry_fruits": _record(
        "High-barrier dry-fruit packaging",
        "High-barrier laminated pouch",
        "PET / Metallized PET / PE",
        [
            "dry fruit", "dry fruits", "dryfruit", "dry fruits / nuts",
            "nuts", "almond", "almonds", "badam",
            "cashew", "kaju", "pistachio", "pista", "walnut"
        ],
        [
            "Oxygen barrier",
            "Moisture barrier",
            "Good sealability",
            "Mechanical protection",
        ],
        [
            "Oxygen protection",
            "Moisture protection",
            "Good sealability",
            "Mechanical protection",
        ],
        [
            "Dry fruits and nuts need protection from moisture and oxygen exposure.",
            "A high-barrier laminate is suitable as a common packaging baseline.",
            "Strong sealing helps limit ingress through the closure.",
        ],
        [
            "Barrier needs vary with fat content, moisture and storage conditions.",
            "Multilayer/metallized structures can have recycling limitations.",
        ],
        {
            "moisture_high": 14,
            "moisture_medium": 7,
            "oxygen_high": 14,
            "oxygen_medium": 7,
            "light_high": 5,
            "perishability_high": 3,
        },
    ),

    # --------------------------------------------------------
    # FRESH FRUIT
    # --------------------------------------------------------

    "fruit": _record(
        "Breathable fresh-produce packaging",
        "Breathable produce packaging",
        "Food-grade perforated film",
        [
            "fruit", "fresh fruit", "fresh fruits"
        ],
        [
            "Controlled ventilation",
            "Moisture management",
            "Mechanical protection",
            "Appropriate gas exchange",
        ],
        [
            "Controlled ventilation",
            "Moisture management",
            "Mechanical protection",
            "Condensation management when appropriately designed",
        ],
        [
            "Fresh produce may continue respiration after harvest.",
            "Controlled ventilation supports appropriate gas exchange.",
            "Perforation can help manage moisture and condensation.",
        ],
        [
            "Perforated film provides less barrier than a fully sealed high-barrier pack.",
            "Perforation must match the product and storage conditions.",
            "Temperature strongly affects fresh-produce packaging performance.",
        ],
        {
            "respiration_high": 18,
            "respiration_medium": 8,
            "perishability_high": 12,
            "perishability_medium": 5,
            "moisture_high": 8,
            "moisture_medium": 4,
        },
    ),

    # --------------------------------------------------------
    # FRESH VEGETABLE
    # --------------------------------------------------------

    "vegetable": _record(
        "Breathable fresh-produce packaging",
        "Breathable produce packaging",
        "Food-grade perforated film",
        [
            "vegetable", "vegetables",
            "fresh vegetable", "fresh vegetables"
        ],
        [
            "Controlled ventilation",
            "Moisture management",
            "Mechanical protection",
            "Appropriate gas exchange",
        ],
        [
            "Controlled ventilation",
            "Moisture management",
            "Mechanical protection",
            "Condensation management when appropriately designed",
        ],
        [
            "Fresh vegetables may continue respiration after harvest.",
            "Controlled ventilation supports gas exchange.",
            "Perforation can help manage moisture and condensation.",
        ],
        [
            "Perforation provides less barrier than a fully sealed high-barrier pack.",
            "Perforation must match the particular vegetable and storage condition.",
            "Cold-chain conditions can strongly influence performance.",
        ],
        {
            "respiration_high": 18,
            "respiration_medium": 8,
            "perishability_high": 12,
            "perishability_medium": 5,
            "moisture_high": 8,
            "moisture_medium": 4,
        },
    ),

    # --------------------------------------------------------
    # DAIRY
    # --------------------------------------------------------

    "dairy": _record(
        "Sealed food-grade dairy packaging",
        "Sealed food-grade dairy packaging",
        "Food-grade polymer / multilayer structure",
        [
            "dairy", "milk", "paneer", "curd",
            "yogurt", "yoghurt", "cheese"
        ],
        [
            "Food-contact suitability",
            "Leak resistance",
            "Contamination protection",
            "Appropriate barrier",
            "Strong closure",
        ],
        [
            "Leak resistance",
            "Contamination protection",
            "Food-contact compatibility",
            "Mechanical protection",
        ],
        [
            "Dairy products need protection from contamination and leakage.",
            "A sealed structure separates the product from the environment.",
            "The final material must match the product and storage conditions.",
        ],
        [
            "Dairy products can have very different packaging requirements.",
            "Refrigerated storage may be necessary depending on the product.",
            "Exact barrier needs depend on formulation and processing.",
        ],
        {
            "perishability_high": 18,
            "perishability_medium": 8,
            "moisture_high": 6,
            "oxygen_high": 8,
            "oxygen_medium": 4,
        },
    ),

    # --------------------------------------------------------
    # FROZEN
    # --------------------------------------------------------

    "frozen": _record(
        "Freezer-compatible high-barrier packaging",
        "Freezer-grade high-barrier packaging",
        "Freezer-compatible multilayer polymer",
        [
            "frozen", "frozen food", "frozen foods"
        ],
        [
            "Low-temperature flexibility",
            "Moisture barrier",
            "Seal integrity",
            "Mechanical durability",
        ],
        [
            "Low-temperature flexibility",
            "Moisture protection",
            "Seal integrity",
            "Mechanical protection",
        ],
        [
            "Frozen products need packaging that remains functional at low temperature.",
            "Moisture protection helps limit environmental moisture transfer.",
            "Seal integrity is important during freezing and handling.",
        ],
        [
            "Material selection must account for low-temperature performance.",
            "Freeze-thaw cycles can affect packaging performance.",
        ],
        {
            "moisture_high": 10,
            "moisture_medium": 5,
            "perishability_high": 10,
            "oxygen_high": 8,
            "oxygen_medium": 4,
        },
    ),

    # --------------------------------------------------------
    # SPICES
    # --------------------------------------------------------

    "spice": _record(
        "High-barrier spice packaging",
        "High-barrier spice pouch",
        "PET / Metallized PET / PE",
        [
            "spice", "spices", "masala", "masalas"
        ],
        [
            "Moisture barrier",
            "Oxygen barrier",
            "Light protection",
            "Good sealability",
        ],
        [
            "Moisture protection",
            "Oxygen protection",
            "Light protection",
            "Good sealability",
        ],
        [
            "Spices benefit from moisture and environmental protection.",
            "A high-barrier structure can reduce exposure to oxygen and moisture.",
            "Light protection may help where the product is light sensitive.",
        ],
        [
            "Required barrier level varies by formulation and shelf-life target.",
            "Multilayer structures can have recycling limitations.",
        ],
        {
            "moisture_high": 14,
            "moisture_medium": 7,
            "oxygen_high": 10,
            "oxygen_medium": 5,
            "light_high": 10,
            "perishability_high": 3,
        },
    ),

    # --------------------------------------------------------
    # BISCUITS / BAKERY
    # --------------------------------------------------------

    "biscuit": _record(
        "Moisture-resistant bakery packaging",
        "Moisture-resistant flexible packaging",
        "PET / PE or suitable laminate",
        [
            "biscuit", "biscuits", "bakery",
            "bakery products", "cookies", "cookie"
        ],
        [
            "Moisture barrier",
            "Good sealability",
            "Mechanical protection",
        ],
        [
            "Moisture protection",
            "Good sealability",
            "Mechanical protection",
            "Protection from external contamination",
        ],
        [
            "Biscuits and many dry bakery products are sensitive to moisture pickup.",
            "Moisture-resistant packaging helps maintain texture.",
            "Good sealing limits environmental exposure.",
        ],
        [
            "Barrier requirements vary by formulation and target shelf life.",
            "Higher-barrier laminates can have recycling limitations.",
        ],
        {
            "moisture_high": 16,
            "moisture_medium": 8,
            "oxygen_high": 8,
            "oxygen_medium": 4,
            "perishability_high": 4,
        },
    ),

    # --------------------------------------------------------
    # READY-TO-EAT / COOKED FOOD
    # --------------------------------------------------------

    "ready_to_eat": _record(
        "Food-grade high-barrier ready-food packaging",
        "Food-grade high-barrier packaging",
        "Suitable multilayer food-contact structure",
        [
            "ready-to-eat", "ready to eat",
            "ready-to-eat / cooked food",
            "cooked food", "cooked", "meal", "prepared food"
        ],
        [
            "Contamination protection",
            "Oxygen/moisture control",
            "Strong sealing",
            "Product-material compatibility",
        ],
        [
            "Contamination protection",
            "Moisture and oxygen control",
            "Strong sealing",
            "Mechanical protection",
        ],
        [
            "Prepared foods need protection from external contamination.",
            "A sealed food-contact structure separates food from the environment.",
            "Barrier needs depend on processing and storage conditions.",
        ],
        [
            "Chilled, ambient, hot-filled and retort applications differ substantially.",
            "Shelf life cannot be inferred from packaging alone.",
        ],
        {
            "perishability_high": 16,
            "perishability_medium": 7,
            "oxygen_high": 10,
            "oxygen_medium": 5,
            "moisture_high": 6,
            "moisture_medium": 3,
        },
    ),

    # --------------------------------------------------------
    # PICKLE
    # --------------------------------------------------------

    "pickle": _record(
        "Leak-resistant compatible pickle packaging",
        "Leak-resistant barrier packaging",
        "Food-grade compatible container or multilayer structure",
        [
            "pickle", "pickles", "achar", "achaar"
        ],
        [
            "Leak resistance",
            "Chemical compatibility",
            "Strong sealing",
            "Food-contact suitability",
        ],
        [
            "Leak resistance",
            "Strong sealing",
            "Contamination protection",
            "Suitable barrier when properly selected",
        ],
        [
            "Pickles may contain acidic, salty or oily components.",
            "Leak resistance matters during storage and transport.",
            "Container and closure compatibility must match the formulation.",
        ],
        [
            "Generic food-grade status does not prove compatibility with every formulation.",
            "Actual formulation-specific compatibility should be evaluated.",
        ],
        {
            "perishability_high": 5,
            "oxygen_high": 7,
            "oxygen_medium": 3,
            "moisture_high": 5,
        },
    ),

    # --------------------------------------------------------
    # SAUCE
    # --------------------------------------------------------

    "sauce": _record(
        "Leak-resistant sauce packaging",
        "Leak-resistant barrier packaging",
        "Food-grade compatible container or multilayer structure",
        [
            "sauce", "sauces", "ketchup", "tomato sauce"
        ],
        [
            "Leak resistance",
            "Chemical compatibility",
            "Strong sealing",
            "Food-contact suitability",
        ],
        [
            "Leak resistance",
            "Contamination protection",
            "Strong sealing",
            "Suitable barrier when properly selected",
        ],
        [
            "Sauces require reliable containment for liquid or semi-liquid products.",
            "Leak resistance and closure integrity matter during handling.",
            "The material should be compatible with the formulation.",
        ],
        [
            "Acidity, oils, salts and other ingredients can affect compatibility.",
            "Dispensing format can change the packaging requirement.",
        ],
        {
            "perishability_high": 6,
            "oxygen_high": 7,
            "oxygen_medium": 3,
            "moisture_high": 4,
        },
    ),

    # --------------------------------------------------------
    # CHUTNEY
    # --------------------------------------------------------

    "chutney": _record(
        "Leak-resistant chutney packaging",
        "Leak-resistant barrier packaging",
        "Food-grade compatible container or multilayer structure",
        [
            "chutney", "chutneys"
        ],
        [
            "Leak resistance",
            "Chemical compatibility",
            "Strong sealing",
            "Food-contact suitability",
        ],
        [
            "Leak resistance",
            "Contamination protection",
            "Strong sealing",
            "Suitable barrier when properly selected",
        ],
        [
            "Chutney is generally moist or semi-liquid and needs reliable containment.",
            "Leak resistance is important for storage and transport.",
            "The package should match the actual formulation.",
        ],
        [
            "Refrigerated and ambient chutneys can have different requirements.",
            "Material compatibility and shelf-life validation remain necessary.",
        ],
        {
            "perishability_high": 10,
            "perishability_medium": 5,
            "oxygen_high": 8,
            "oxygen_medium": 4,
            "moisture_high": 4,
        },
    ),
}


# ============================================================
# FALLBACK
# ============================================================

FALLBACK_RECORD = _record(
    "Food-grade protective packaging",
    "Food-grade protective barrier packaging",
    "Food-grade multilayer material",
    ["other"],
    [
        "Food-contact suitability",
        "Moisture protection",
        "Mechanical protection",
    ],
    [
        "Food-contact packaging suitability",
        "Moisture protection",
        "Mechanical protection",
    ],
    [
        "No specialized category record matched the input.",
        "A conservative food-grade protective baseline is used.",
    ],
    [
        "The exact material cannot be selected reliably from limited information.",
        "Product-specific compatibility and shelf-life validation are required.",
    ],
    {},
)


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value):
    return str(value or "").strip().lower()


def normalize_category(category):
    value = normalize(category)

    aliases = {
        "dry fruits": "dry_fruits",
        "dry fruit": "dry_fruits",
        "dryfruit": "dry_fruits",
        "nuts": "dry_fruits",

        "fresh fruit": "fruit",
        "fresh fruits": "fruit",

        "fresh vegetable": "vegetable",
        "fresh vegetables": "vegetable",

        "frozen food": "frozen",
        "frozen foods": "frozen",

        "ready-to-eat": "ready_to_eat",
        "ready to eat": "ready_to_eat",
        "ready-to-eat / cooked food": "ready_to_eat",
        "cooked food": "ready_to_eat",

        "spices": "spice",

        "bakery": "biscuit",
        "bakery products": "biscuit",
    }

    return aliases.get(value, value)


# ============================================================
# KNOWLEDGE MATCHING
# ============================================================

def find_knowledge_record(data):
    data = data or {}

    category = normalize_category(data.get("category"))
    product = normalize(data.get("product"))

    if category in PACKAGING_KNOWLEDGE:
        return PACKAGING_KNOWLEDGE[category]

    for record in PACKAGING_KNOWLEDGE.values():
        aliases = record.get("category_aliases", [])

        for alias in aliases:
            alias_value = normalize(alias)

            if (
                category == alias_value
                or alias_value in category
                or category in alias_value
            ):
                return record

    product_words = (
        product.replace("/", " ")
        .replace("-", " ")
        .split()
    )

    for record in PACKAGING_KNOWLEDGE.values():
        aliases = [
            normalize(x)
            for x in record.get("category_aliases", [])
        ]

        for word in product_words:
            if len(word) < 3:
                continue

            if any(word in alias for alias in aliases):
                return record

    return None


# ============================================================
# RULE SCORING
# ============================================================

def score_record(record, data):
    data = data or {}

    score = 100
    matched_rules = []

    for characteristic in (
        "moisture",
        "oxygen",
        "light",
        "perishability",
        "respiration",
    ):
        value = normalize(data.get(characteristic))
        key = f"{characteristic}_{value}"

        if key in record.get("conditions", {}):
            points = int(record["conditions"][key])
            score += points

            matched_rules.append(
                {
                    "characteristic": characteristic,
                    "value": value,
                    "points": points,
                }
            )

    return score, matched_rules


# ============================================================
# SMALL OUTPUT HELPERS
# ============================================================

def _append_unique(items, value):
    if value and value not in items:
        items.append(value)


def build_benefits(record, data):
    benefits = list(record.get("benefits", []))
    data = data or {}

    moisture = normalize(data.get("moisture"))
    oxygen = normalize(data.get("oxygen"))
    light = normalize(data.get("light"))
    perishability = normalize(data.get("perishability"))
    respiration = normalize(data.get("respiration"))

    if moisture == "high":
        _append_unique(
            benefits,
            "High moisture-barrier requirement",
        )
    elif moisture == "medium":
        _append_unique(
            benefits,
            "Moderate moisture protection",
        )

    if oxygen == "high":
        _append_unique(
            benefits,
            "High oxygen-barrier requirement",
        )
    elif oxygen == "medium":
        _append_unique(
            benefits,
            "Moderate oxygen protection",
        )

    if light == "high":
        _append_unique(
            benefits,
            "Additional light protection requirement",
        )

    if perishability == "high":
        _append_unique(
            benefits,
            "Strong contamination and handling protection",
        )

    if respiration == "high":
        _append_unique(
            benefits,
            "Controlled gas exchange / ventilation",
        )

    # Keep recommendation-page output compact.
    return benefits[:7]


def build_why_selected(record, data):
    data = data or {}

    reasons = []

    # Put the strongest reason first.
    record_reasons = list(record.get("why", []))

    for reason in record_reasons:
        _append_unique(reasons, reason)

    if normalize(data.get("moisture")) == "high":
        _append_unique(
            reasons,
            "High moisture sensitivity increases the need for moisture protection.",
        )

    if normalize(data.get("oxygen")) == "high":
        _append_unique(
            reasons,
            "High oxygen sensitivity increases the need for oxygen-barrier performance.",
        )

    if normalize(data.get("light")) == "high":
        _append_unique(
            reasons,
            "High light sensitivity increases the need for light protection.",
        )

    if normalize(data.get("perishability")) == "high":
        _append_unique(
            reasons,
            "High perishability increases the need for strong contamination protection.",
        )

    if normalize(data.get("respiration")) == "high":
        _append_unique(
            reasons,
            "High respiration activity increases the importance of suitable gas exchange.",
        )

    if not reasons:
        reasons.append(
            "The selected packaging matches the product category."
        )

    return reasons[:4]


def build_requirements(record, data):
    requirements = list(record.get("requirements", []))
    data = data or {}

    if normalize(data.get("moisture")) == "high":
        _append_unique(requirements, "High moisture barrier")

    if normalize(data.get("oxygen")) == "high":
        _append_unique(requirements, "High oxygen barrier")

    if normalize(data.get("light")) == "high":
        _append_unique(requirements, "Light protection")

    if normalize(data.get("respiration")) == "high":
        _append_unique(requirements, "Controlled gas exchange")

    return requirements[:6]


# ============================================================
# TRUSTED EVIDENCE
# ============================================================

def get_authoritative_sources():
    return deepcopy(AUTHORITATIVE_SOURCES)


def get_database_evidence(data=None):
    return get_authoritative_sources()


# ============================================================
# COST / SUSTAINABILITY
# ============================================================

def build_cost_comparison(data, material):
    data = data or {}

    return {
        "show": False,
        "old_material": str(
            data.get("old_material", "")
        ).strip(),
        "old_cost": str(
            data.get("old_packaging_cost", "")
        ).strip(),
        "new_material": material,
        "new_cost": "",
        "difference": "",
        "reason": (
            "A reliable current market-price table for the selected "
            "new packaging material is not available, so no price is invented."
        ),
    }


def build_sustainable_option(record, data):
    return {
        "show": False,
        "material": "",
        "benefit": "",
        "tradeoff": "",
        "reason": (
            "A sustainable alternative is not selected automatically. "
            "Barrier performance, food-contact compatibility, availability "
            "and end-of-life conditions must be evaluated together."
        ),
    }


# ============================================================
# MAIN DATABASE RECOMMENDATION
# ============================================================

def get_database_recommendation(data):
    data = data or {}

    required_shelf_life = str(
        data.get("required_shelf_life", "")
    ).strip()

    record = find_knowledge_record(data)
    fallback_used = record is None

    if fallback_used:
        record = FALLBACK_RECORD

    score, matched_rules = score_record(
        record,
        data,
    )

    why_selected = build_why_selected(
        record,
        data,
    )

    if fallback_used:
        why_selected.insert(
            0,
            "No specialized category record matched, so a conservative food-grade baseline was used.",
        )

    benefits = build_benefits(
        record,
        data,
    )

    requirements = build_requirements(
        record,
        data,
    )

    if fallback_used:
        assessment = (
            "General packaging guidance; more product-specific information is required."
        )
        match_type = "fallback"

    elif score >= 125:
        assessment = (
            "Strong match between the product category and entered packaging characteristics."
        )
        match_type = "specialized_knowledge_record"

    elif score >= 110:
        assessment = (
            "Good match between the product category and entered packaging characteristics."
        )
        match_type = "specialized_knowledge_record"

    else:
        assessment = (
            "Category-based packaging match; product-specific validation is still required."
        )
        match_type = "specialized_knowledge_record"

    validation_note = (
        "Prototype guidance only. Final commercial packaging selection requires "
        "food-contact compliance, material compatibility, applicable migration/"
        "compliance assessment, packaging performance testing and shelf-life validation."
    )

    return {
        # Main output — intentionally the same decision used by Manufacturer.
        "final_packaging": record["packaging"],
        "final_material": record["material"],

        # Compact explanation for Recommendation page.
        "why_selected": why_selected,
        "packaging_requirements": requirements,
        "benefits": benefits,
        "tradeoffs": list(record.get("tradeoffs", []))[:3],

        # Rule-engine information.
        "rule_engine": {
            "engine": "SmartPack Shared Packaging Knowledge Rule Engine",
            "match_type": match_type,
            "score": score,
            "assessment": assessment,
            "matched_characteristics": matched_rules,
        },

        # Shelf life is always a target.
        "shelf_life": {
            "user_target": required_shelf_life,
            "assessment": "Requires shelf-life validation.",
            "note": "The entered shelf life is a target, not a guaranteed result.",
        },

        # No invented price.
        "cost_comparison": build_cost_comparison(
            data,
            record["material"],
        ),

        # No automatic greenwashing.
        "sustainable_option": build_sustainable_option(
            record,
            data,
        ),

        # Trusted external references.
        "evidence": get_database_evidence(data),

        "validation_note": validation_note,

        # Useful compact fields for a redesigned Recommendation page.
        "display": {
            "title": "SmartPack Database Analysis",
            "summary": (
                f"{record['packaging']} using {record['material']}."
            ),
            "decision": "Database recommendation ready",
            "compact": True,
        },
    }


# ============================================================
# BACKWARD-COMPATIBLE RULE ENGINE
# ============================================================

def old_rule_engine(data):
    """
    Compatibility wrapper.

    Existing Manufacturer code can continue calling old_rule_engine().
    It now reads from the same database used by Recommendation.
    """

    recommendation = get_database_recommendation(
        data or {}
    )

    return {
        "packaging": recommendation["final_packaging"],
        "material": recommendation["final_material"],
        "features": recommendation["benefits"],
    }


__all__ = [
    "AUTHORITATIVE_SOURCES",
    "PACKAGING_KNOWLEDGE",
    "get_database_recommendation",
    "get_authoritative_sources",
    "get_database_evidence",
    "old_rule_engine",
]
