from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

from datetime import datetime
import uuid
import os
import json
import re


# ============================================================
# APP SETUP
# ============================================================

app = Flask(__name__)

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = os.getenv(
    "BASE_URL",
    "http://127.0.0.1:5000"
).strip().rstrip("/")


# ============================================================
# SMARTPACK AI CONFIGURATION
# ============================================================

SMARTPACK_AI_MODEL = "gemini-3.6-flash"


SMARTPACK_AI_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
    os.getenv("GEMINI_API_KEY_5"),
]


SMARTPACK_AI_KEYS = [
    key.strip()
    for key in SMARTPACK_AI_KEYS
    if key and key.strip()
]


current_key_index = 0


# ============================================================
# TEMPORARY PRODUCT DATABASE
# ============================================================

PRODUCT_DATABASE = {}


# ============================================================
# SMARTPACK AI CLIENT
# ============================================================

def get_smartpack_ai_client():

    global current_key_index

    if not SMARTPACK_AI_KEYS:
        return None

    current_key = SMARTPACK_AI_KEYS[
        current_key_index
    ]

    return genai.Client(
        api_key=current_key
    )


def move_to_next_key():

    global current_key_index

    if not SMARTPACK_AI_KEYS:
        return

    current_key_index = (
        current_key_index + 1
    ) % len(SMARTPACK_AI_KEYS)


# ============================================================
# DETECT 429 / QUOTA ERRORS
# ============================================================

def is_quota_error(error_text):

    text = str(error_text).lower()

    quota_words = [
        "resource_exhausted",
        "quota exceeded",
        "quota_exceeded",
        "generate_requests_per_day",
        "generaterequestsperday",
        "429"
    ]

    for word in quota_words:

        if word in text:
            return True

    return False


def is_temporary_rate_limit(error_text):

    text = str(error_text).lower()

    temporary_words = [
        "rate_limit_exceeded",
        "too many requests",
        "retryinfo",
        "requests per minute",
        "requests per second"
    ]

    for word in temporary_words:

        if word in text:
            return True

    return False


# ============================================================
# CLEAN SMARTPACK AI ERROR
# ============================================================

def get_user_friendly_ai_error(error_text):

    if is_quota_error(error_text):

        return (
            "SmartPack AI is temporarily unavailable "
            "because the current AI usage limit has "
            "been reached. Please try again later."
        )

    if is_temporary_rate_limit(error_text):

        return (
            "SmartPack AI is temporarily busy. "
            "Please wait a moment and try again."
        )

    return (
        "SmartPack AI could not process the request "
        "right now. Please try again."
    )


# ============================================================
# SMARTPACK AI TEXT REQUEST
# ============================================================

def run_smartpack_ai_request(
    prompt,
    system_instruction
):

    if not SMARTPACK_AI_KEYS:

        return {
            "success": False,
            "error_type": "configuration",
            "error":
                "SmartPack AI is not configured."
        }


    attempts = len(
        SMARTPACK_AI_KEYS
    )

    last_error = (
        "Unknown SmartPack AI error."
    )

    quota_detected = False


    for attempt in range(attempts):

        try:

            client = (
                get_smartpack_ai_client()
            )


            response = (
                client.interactions.create(

                    model=SMARTPACK_AI_MODEL,

                    input=prompt,

                    system_instruction=
                        system_instruction

                )
            )


            return {

                "success": True,

                "text":
                    response.output_text

            }


        except Exception as e:

            last_error = str(e)


            print()
            print(
                "SmartPack AI request error:"
            )

            print(last_error)
            print()


            # --------------------------------------------
            # QUOTA ERROR
            # --------------------------------------------

            if is_quota_error(
                last_error
            ):

                quota_detected = True

                print(
                    "SmartPack AI quota detected."
                )

                # Do not blindly retry all keys
                # because project-level quotas
                # are not bypassed by key rotation.

                break


            # --------------------------------------------
            # TEMPORARY RATE LIMIT
            # --------------------------------------------

            if is_temporary_rate_limit(
                last_error
            ):

                print(
                    "Temporary SmartPack AI "
                    "rate limit detected."
                )

                move_to_next_key()

                continue


            # --------------------------------------------
            # OTHER ERROR
            # --------------------------------------------

            move_to_next_key()


    if quota_detected:

        return {

            "success": False,

            "error_type": "quota",

            "error":
                get_user_friendly_ai_error(
                    last_error
                )

        }


    return {

        "success": False,

        "error_type": "api",

        "error":
            get_user_friendly_ai_error(
                last_error
            )

    }


# ============================================================
# SMARTPACK AI IMAGE REQUEST
# ============================================================

def run_smartpack_ai_image_request(
    image_bytes,
    mime_type,
    prompt
):

    if not SMARTPACK_AI_KEYS:

        return {

            "success": False,

            "error_type":
                "configuration",

            "error":
                "SmartPack AI is not configured."

        }


    attempts = len(
        SMARTPACK_AI_KEYS
    )

    last_error = (
        "Unknown SmartPack AI error."
    )

    quota_detected = False


    for attempt in range(attempts):

        try:

            client = (
                get_smartpack_ai_client()
            )


            image_part = (
                types.Part.from_bytes(

                    data=image_bytes,

                    mime_type=mime_type

                )
            )


            response = (
                client.models.generate_content(

                    model=SMARTPACK_AI_MODEL,

                    contents=[
                        image_part,
                        prompt
                    ]

                )
            )


            return {

                "success": True,

                "text":
                    response.text

            }


        except Exception as e:

            last_error = str(e)


            print()
            print(
                "SmartPack AI image request error:"
            )

            print(last_error)
            print()


            # --------------------------------------------
            # DAILY / PROJECT QUOTA
            # --------------------------------------------

            if is_quota_error(
                last_error
            ):

                quota_detected = True

                print(
                    "SmartPack AI image quota "
                    "detected."
                )

                break


            # --------------------------------------------
            # TEMPORARY RATE LIMIT
            # --------------------------------------------

            if is_temporary_rate_limit(
                last_error
            ):

                print(
                    "Temporary SmartPack AI "
                    "image rate limit detected."
                )

                move_to_next_key()

                continue


            move_to_next_key()


    if quota_detected:

        return {

            "success": False,

            "error_type":
                "quota",

            "error":
                get_user_friendly_ai_error(
                    last_error
                )

        }


    return {

        "success": False,

        "error_type":
            "api",

        "error":
            get_user_friendly_ai_error(
                last_error
            )

    }


# ============================================================
# API ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def handle_not_found(error):

    if request.path.startswith("/api/"):

        return jsonify({
            "success": False,
            "error": "API endpoint not found: " + request.path
        }), 404

    return error


@app.errorhandler(500)
def handle_server_error(error):

    if request.path.startswith("/api/"):

        return jsonify({
            "success": False,
            "error": "SmartPack server error while processing the request."
        }), 500

    return error


# ============================================================
# BASIC PAGES
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route("/recommendation")
def recommendation():

    return render_template(
        "recommendation.html"
    )


@app.route("/manufacturer")
def manufacturer():

    return render_template(
        "manufacturer.html"
    )


@app.route("/inspector")
def inspector():

    return render_template(
        "inspector.html"
    )


# ============================================================
# SMARTPACK AI CHATBOT PAGE
# ============================================================

@app.route("/chatbot")
def chatbot():

    return render_template(
        "chatbot.html"
    )


# ============================================================
# PRODUCT QR PAGE
# ============================================================

@app.route(
    "/product/<product_id>"
)
def product_page(product_id):

    product = PRODUCT_DATABASE.get(
        product_id
    )


    if not product:

        return render_template(

            "product.html",

            product=None,

            error=(
                "This product information "
                "is not available on the server."
            )

        ), 404


    return render_template(

        "product.html",

        product=product,

        error=None

    )


# ============================================================
# RULE-BASED PACKAGING ENGINE
# ============================================================

def old_rule_engine(data):

    product = data.get(
        "product",
        ""
    ).strip()


    category = data.get(
        "category",
        ""
    ).strip().lower()


    moisture = data.get(
        "moisture",
        ""
    ).strip().lower()


    oxygen = data.get(
        "oxygen",
        ""
    ).strip().lower()


    light = data.get(
        "light",
        ""
    ).strip().lower()


    perishability = data.get(
        "perishability",
        ""
    ).strip().lower()


    respiration = data.get(
        "respiration",
        ""
    ).strip().lower()


    # --------------------------------------------------------
    # CATEGORY RECOMMENDATIONS
    # --------------------------------------------------------

    if category in [
        "snacks",
        "namkeen",
        "chips",
        "gathiya",
        "khakhra"
    ]:

        packaging = (
            "High-barrier flexible pouch"
        )

        material = (
            "PET / Metallized PET / PE"
        )

        features = [

            "Moisture barrier",

            "Oxygen barrier",

            "Good heat sealability"

        ]


    elif category in [
        "dry fruit",
        "dry fruits",
        "nuts"
    ]:

        packaging = (
            "High-barrier laminated pouch"
        )

        material = (
            "PET / Metallized PET / PE"
        )

        features = [

            "Oxygen barrier",

            "Moisture barrier",

            "Good sealability"

        ]


    elif category in [
        "fruit",
        "fresh fruit"
    ]:

        packaging = (
            "Breathable produce packaging"
        )

        material = (
            "Food-grade perforated film"
        )

        features = [

            "Controlled ventilation",

            "Moisture management",

            "Mechanical protection"

        ]


    elif category in [
        "vegetable",
        "fresh vegetable"
    ]:

        packaging = (
            "Breathable produce packaging"
        )

        material = (
            "Food-grade perforated film"
        )

        features = [

            "Controlled ventilation",

            "Moisture management",

            "Mechanical protection"

        ]


    elif category in [
        "dairy",
        "milk"
    ]:

        packaging = (
            "Sealed food-grade dairy packaging"
        )

        material = (
            "Food-grade polymer / "
            "multilayer structure"
        )

        features = [

            "Leak resistance",

            "Contamination protection",

            "Suitable barrier"

        ]


    elif category in [
        "frozen",
        "frozen food"
    ]:

        packaging = (
            "Freezer-grade high-barrier packaging"
        )

        material = (
            "Freezer-compatible multilayer polymer"
        )

        features = [

            "Low-temperature flexibility",

            "Moisture barrier",

            "Seal integrity"

        ]


    elif category in [
        "spice",
        "spices"
    ]:

        packaging = (
            "High-barrier spice pouch"
        )

        material = (
            "PET / Metallized PET / PE"
        )

        features = [

            "Moisture barrier",

            "Light protection",

            "Oxygen barrier"

        ]


    elif category in [
        "biscuit",
        "bakery"
    ]:

        packaging = (
            "Moisture-resistant flexible packaging"
        )

        material = (
            "PET / PE or suitable laminate"
        )

        features = [

            "Moisture barrier",

            "Good sealability",

            "Mechanical protection"

        ]


    elif category in [
        "ready-to-eat",
        "cooked food"
    ]:

        packaging = (
            "Food-grade high-barrier packaging"
        )

        material = (
            "Suitable multilayer "
            "food-contact structure"
        )

        features = [

            "Contamination protection",

            "Oxygen/moisture control",

            "Strong sealing"

        ]


    elif category in [
        "pickle",
        "sauce",
        "chutney"
    ]:

        packaging = (
            "Leak-resistant barrier packaging"
        )

        material = (
            "Food-grade compatible container "
            "or multilayer structure"
        )

        features = [

            "Leak resistance",

            "Chemical compatibility",

            "Strong sealing"

        ]


    else:

        packaging = (
            "Food-grade protective barrier packaging"
        )

        material = (
            "Food-grade multilayer material"
        )

        features = [

            "Food-contact suitability",

            "Moisture protection",

            "Mechanical protection"

        ]


    # --------------------------------------------------------
    # CHARACTERISTICS
    # --------------------------------------------------------

    if moisture == "high":

        features.append(
            "High moisture barrier"
        )

    elif moisture == "medium":

        features.append(
            "Moderate moisture protection"
        )


    if oxygen == "high":

        features.append(
            "High oxygen barrier"
        )

    elif oxygen == "medium":

        features.append(
            "Moderate oxygen barrier"
        )


    if light == "high":

        features.append(
            "Light protection"
        )


    if perishability == "high":

        features.append(
            "Strong contamination protection"
        )


    if respiration == "high":

        features.append(
            "Controlled gas exchange / ventilation"
        )


    features = list(
        dict.fromkeys(features)
    )


    return {

        "packaging":
            packaging,

        "material":
            material,

        "features":
            features

    }


# ============================================================
# SMARTPACK AI PACKAGING ANALYSIS
# ============================================================

def smartpack_ai_analysis(
    data,
    baseline
):

    prompt_data = {

        "product":
            data.get("product"),

        "category":
            data.get("category"),

        "moisture":
            data.get("moisture"),

        "oxygen":
            data.get("oxygen"),

        "light":
            data.get("light"),

        "perishability":
            data.get("perishability"),

        "respiration":
            data.get("respiration"),

        "old_material":
            data.get("old_material"),

        "pack_size":
            data.get("pack_size"),

        "old_packaging_cost":
            data.get("old_packaging_cost"),

        "required_shelf_life":
            data.get("required_shelf_life"),

        "baseline_recommendation":
            baseline

    }


    system_instruction = """

You are SmartPack AI, the intelligent analysis
engine of an intelligent food packaging
recommendation system.

Your job is to improve and explain the existing
rule-based packaging recommendation.

IMPORTANT RULES:

1. Never blindly replace the existing recommendation.

2. Use the existing recommendation as the baseline.

3. Improve it only when product characteristics
justify the improvement.

4. Do not invent packaging prices.

5. Do not invent market prices.

6. Do not invent laboratory test results.

7. Do not claim that a material guarantees a
specific shelf life.

8. The user's required shelf life is a TARGET.

9. Shelf life depends on food formulation,
processing, packaging, storage, temperature,
humidity and validation testing.

10. If the required shelf life cannot be confidently
assessed from available information, say:

"Requires shelf-life validation."

11. Only show cost comparison when enough reliable
cost information exists.

12. If cost information is missing, return:

"Not available"

13. The old packaging material must be clearly
identified before comparing it with a new material.

14. If the old material already appears technically
suitable and there is no meaningful improvement,
do not force a new material recommendation.

15. A bio-based, compostable or sustainable material
is OPTIONAL.

16. Suggest a sustainable option only if it can
reasonably satisfy the product's required barrier,
food-contact and shelf-life requirements.

17. Do not call sustainable packaging automatically
better.

18. Mention trade-offs such as cost, barrier
performance, availability or validation when relevant.

19. Keep final information compact.

20. Prefer short tables or bullet points.

21. Never write long paragraphs.

22. Clearly explain WHY the material was selected.

23. Evidence must be clearly separated from
the recommendation.

24. Do not claim that a source was checked unless
that source is actually available.

25. The recommendation is prototype guidance and
not a certified food-safety or packaging approval.

Return ONLY valid JSON.

Use exactly this structure:

{
    "final_packaging": "",
    "final_material": "",
    "why_selected": [],
    "benefits": [],
    "shelf_life": {
        "user_target": "",
        "assessment": ""
    },
    "cost_comparison": {
        "show": false,
        "old_material": "",
        "old_cost": "",
        "new_material": "",
        "new_cost": "",
        "difference": "",
        "reason": ""
    },
    "sustainable_option": {
        "show": false,
        "material": "",
        "benefit": "",
        "tradeoff": ""
    },
    "evidence": [
        {
            "source": "",
            "reason_used": ""
        }
    ],
    "validation_note": ""
}

Keep arrays short.

"""


    prompt = json.dumps(
        prompt_data,
        indent=2
    )


    result = run_smartpack_ai_request(

        prompt,

        system_instruction

    )


    if not result["success"]:

        return {

            "available": False,

            "error_type":
                result.get(
                    "error_type",
                    "api"
                ),

            "error":
                result["error"]

        }


    try:

        text = result[
            "text"
        ].strip()


        if text.startswith("```"):

            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()


        parsed = json.loads(
            text
        )


        return {

            "available": True,

            "result":
                parsed

        }


    except json.JSONDecodeError as e:

        return {

            "available": False,

            "error_type":
                "invalid_response",

            "error":
                "SmartPack AI returned an invalid result."

        }


# ============================================================
# RECOMMENDATION API
# ============================================================

@app.route(
    "/api/recommend",
    methods=["POST"]
)
@app.route(
    "/api/recommendation",
    methods=["POST"]
)
@app.route(
    "/api/recommend/start",
    methods=["POST"]
)
def recommend():

    data = request.get_json(silent=True) or {}


    if not data:

        return jsonify({

            "success": False,

            "error":
                "No product information received."

        }), 400


    product = data.get(
        "product",
        ""
    ).strip()


    if not product:

        return jsonify({

            "success": False,

            "error":
                "Please enter a product name."

        }), 400


    # Rule engine always works locally

    baseline = old_rule_engine(
        data
    )


    # SmartPack AI improvement

    ai_result = smartpack_ai_analysis(
        data,
        baseline
    )


    if ai_result["available"]:

        return jsonify({

            "success": True,

            "engine":
                "Rule Engine + SmartPack AI",

            "product":
                product,

            "baseline":
                baseline,

            "recommendation":
                ai_result["result"]

        })


    # --------------------------------------------------------
    # SAFE FALLBACK
    # --------------------------------------------------------

    return jsonify({

        "success": True,

        "engine":
            "Rule Engine",

        "ai_status":
            ai_result.get(
                "error_type",
                "unavailable"
            ),

        "ai_message":
            ai_result.get(
                "error",
                "SmartPack AI is temporarily unavailable."
            ),

        "product":
            product,

        "recommendation": {

            "final_packaging":
                baseline["packaging"],

            "final_material":
                baseline["material"],

            "why_selected": [

                "Recommendation generated from "
                "the entered product characteristics."

            ],

            "benefits":
                baseline["features"],

            "shelf_life": {

                "user_target":
                    data.get(
                        "required_shelf_life",
                        ""
                    ),

                "assessment":
                    "Requires shelf-life validation."

            },

            "cost_comparison": {

                "show":
                    False,

                "old_material":
                    data.get(
                        "old_material",
                        ""
                    ),

                "old_cost":
                    data.get(
                        "old_packaging_cost",
                        ""
                    ),

                "new_material":
                    baseline["material"],

                "new_cost":
                    "",

                "difference":
                    "",

                "reason":
                    "Reliable cost data is not available."

            },

            "sustainable_option": {

                "show":
                    False,

                "material":
                    "",

                "benefit":
                    "",

                "tradeoff":
                    ""

            },

            "evidence": [

                {

                    "source":
                        "FSSAI",

                    "reason_used":
                        "Food-contact packaging requirements."

                },

                {

                    "source":
                        "Relevant BIS standard",

                    "reason_used":
                        "Packaging material requirements."

                },

                {

                    "source":
                        "Verified technical literature",

                    "reason_used":
                        "Material and barrier properties."

                }

            ],

            "validation_note":
                "Final commercial packaging selection "
                "requires material compatibility and "
                "shelf-life validation."

        }

    })


# ============================================================
# SMARTPACK AI CHATBOT
# ============================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "error":
                "No message received."

        }), 400


    message = data.get(
        "message",
        ""
    ).strip()


    if not message:

        return jsonify({

            "success": False,

            "error":
                "Please enter a question."

        }), 400


    system_instruction = """

You are SmartPack AI, the conversational assistant
inside a Smart Food Packaging system.

Your job is to answer users naturally and helpfully
about food packaging and closely related topics.

IMPORTANT: The FAQ list is only a starting point.
Users are NOT limited to the FAQ questions. Answer
any reasonable packaging-related question the user
asks.

MAIN TOPICS:

1. Food packaging basics
2. Indian food packaging
3. Packaging materials
4. Moisture, oxygen and light protection
5. Shelf-life concepts
6. Storage and cold chain
7. Food logistics
8. Sustainable packaging
9. Packaging cost and comparison
10. Packaging inspection
11. QR/product information
12. General SmartPack system questions

COMMUNICATION STYLE:

- Use simple English.
- Sound like a helpful human, not a textbook.
- Keep normal answers short and practical.
- Explain technical words in simple words when needed.
- Use short bullets when they make the answer clearer.
- Do not repeat the user's question unnecessarily.
- If the user asks for more detail, then explain more.

NATURAL QUESTION EXAMPLES:

Users may ask things like:
- "What should I use for paneer?"
- "My namkeen gets soft. Why?"
- "Can I use paper instead of plastic?"
- "My packet is leaking. What should I check?"
- "Is this packaging too expensive?"
- "How can I increase shelf life?"
- "Do I need cold storage?"

Handle these naturally even when the exact question
is not listed in the FAQ.

SCOPE:

If a question is clearly unrelated to food packaging
or the SmartPack system, politely say that you are
focused on food packaging and related topics, then
invite the user to ask a relevant question.

SAFETY AND ACCURACY:

- Do not invent scientific facts, prices, regulations
  or laboratory test results.
- Do not claim that packaging guarantees a specific
  shelf life.
- Do not claim that an image alone proves food safety
  or freshness.
- If information is insufficient, say so clearly.
- Commercial packaging decisions need suitable
  food-contact compliance, compatibility and
  shelf-life validation.
- Do not pretend that a source was checked if it was
  not actually provided or available.

"""


    result = run_smartpack_ai_request(

        message,

        system_instruction

    )


    if not result["success"]:

        return jsonify({

            "success":
                False,

            "error":
                result["error"],

            "error_type":
                result.get(
                    "error_type",
                    "api"
                )

        }), 200


    return jsonify({

        "success":
            True,

        "reply":
            result["text"]

    })


# ============================================================
# MANUFACTURER PORTAL
# ============================================================

@app.route(
    "/api/manufacturer/create",
    methods=["POST"]
)
def manufacturer_create():

    data = request.get_json()


    if not data:

        return jsonify({

            "success":
                False,

            "error":
                "No manufacturer information received."

        }), 400


    manufacturer_name = data.get(
        "manufacturer_name",
        ""
    ).strip()


    brand_name = data.get(
        "brand_name",
        ""
    ).strip()


    manufacturer_address = data.get(
        "manufacturer_address",
        ""
    ).strip()


    product = data.get(
        "product",
        ""
    ).strip()


    category = data.get(
        "category",
        ""
    ).strip()


    pack_size = data.get(
        "pack_size",
        ""
    ).strip()


    batch_number = data.get(
        "batch_number",
        ""
    ).strip()


    manufacturing_date = data.get(
        "manufacturing_date",
        ""
    ).strip()


    expiry_date = data.get(
        "expiry_date",
        ""
    ).strip()


    required_shelf_life = data.get(
        "required_shelf_life",
        ""
    ).strip()


    old_material = data.get(
        "old_material",
        ""
    ).strip()


    old_packaging_cost = data.get(
        "old_packaging_cost",
        ""
    ).strip()


    moisture = data.get(
        "moisture",
        ""
    ).strip()


    oxygen = data.get(
        "oxygen",
        ""
    ).strip()


    light = data.get(
        "light",
        ""
    ).strip()


    perishability = data.get(
        "perishability",
        ""
    ).strip()


    respiration = data.get(
        "respiration",
        ""
    ).strip()


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not manufacturer_name:

        return jsonify({

            "success":
                False,

            "error":
                "Please enter manufacturer."

        }), 400


    if not brand_name:

        return jsonify({

            "success":
                False,

            "error":
                "Please enter brand."

        }), 400


    if not product:

        return jsonify({

            "success":
                False,

            "error":
                "Please enter product."

        }), 400


    if not category:

        return jsonify({

            "success":
                False,

            "error":
                "Please select a category."

        }), 400


    if not pack_size:

        return jsonify({

            "success":
                False,

            "error":
                "Please enter pack size."

        }), 400


    if not batch_number:

        return jsonify({

            "success":
                False,

            "error":
                "Please enter batch / lot number."

        }), 400


    # --------------------------------------------------------
    # RULE ENGINE DATA
    # --------------------------------------------------------

    rule_engine_data = {

        "product":
            product,

        "category":
            category,

        "moisture":
            moisture,

        "oxygen":
            oxygen,

        "light":
            light,

        "perishability":
            perishability,

        "respiration":
            respiration,

        "old_material":
            old_material,

        "pack_size":
            pack_size,

        "old_packaging_cost":
            old_packaging_cost,

        "required_shelf_life":
            required_shelf_life

    }


    baseline = old_rule_engine(
        rule_engine_data
    )


    # --------------------------------------------------------
    # PRODUCT ID
    # --------------------------------------------------------

    product_id = str(
        uuid.uuid4()
    )


    generated_at = datetime.now().isoformat(
        timespec="seconds"
    )


    # --------------------------------------------------------
    # PRODUCT RECORD
    # --------------------------------------------------------

    product_record = {

        "product_id":
            product_id,

        "manufacturer_name":
            manufacturer_name,

        "brand_name":
            brand_name,

        "manufacturer_address":
            manufacturer_address,

        "product":
            product,

        "category":
            category,

        "pack_size":
            pack_size,

        "batch_number":
            batch_number,

        "manufacturing_date":
            manufacturing_date,

        "expiry_date":
            expiry_date,

        "required_shelf_life":
            required_shelf_life,

        "old_material":
            old_material,

        "old_packaging_cost":
            old_packaging_cost,

        "recommended_packaging":
            baseline["packaging"],

        "recommended_material":
            baseline["material"],

        "packaging_features":
            baseline["features"],

        "shelf_life_assessment":
            "Requires shelf-life validation.",

        "generated_at":
            generated_at

    }


    PRODUCT_DATABASE[
        product_id
    ] = product_record


    # --------------------------------------------------------
    # QR URL
    # --------------------------------------------------------

    qr_url = (
        BASE_URL
        + "/product/"
        + product_id
    )


    print()
    print(
        "Generated QR URL:"
    )
    print(qr_url)
    print()


    # --------------------------------------------------------
    # QR GENERATION
    # --------------------------------------------------------

    try:

        import qrcode


        qr_directory = os.path.join(

            app.static_folder,

            "qr_codes"

        )


        os.makedirs(

            qr_directory,

            exist_ok=True

        )


        qr = qrcode.QRCode(

            version=1,

            error_correction=
                qrcode.constants.ERROR_CORRECT_M,

            box_size=10,

            border=4

        )


        qr.add_data(
            qr_url
        )


        qr.make(
            fit=True
        )


        qr_image = qr.make_image(

            fill_color="black",

            back_color="white"

        )


        qr_filename = (

            "smartpack_"

            + product_id

            + ".png"

        )


        qr_path = os.path.join(

            qr_directory,

            qr_filename

        )


        qr_image.save(
            qr_path
        )


    except Exception as e:

        print(
            "QR generation error:"
        )

        print(
            str(e)
        )


        PRODUCT_DATABASE.pop(

            product_id,

            None

        )


        return jsonify({

            "success":
                False,

            "error":
                "Could not generate QR code."

        }), 500


    qr_image_url = (

        "/static/qr_codes/"

        + qr_filename

    )


    # --------------------------------------------------------
    # FRONTEND PRODUCT DATA
    # --------------------------------------------------------

    product_data = {

        "brand_name":
            brand_name,

        "product":
            product,

        "category":
            category,

        "pack_size":
            pack_size,

        "batch_number":
            batch_number,

        "manufacturing_date":
            manufacturing_date,

        "expiry_date":
            expiry_date

    }


    return jsonify({

        "success":
            True,

        "product_id":
            product_id,

        "generated_at":
            generated_at,

        "product_data":
            product_data,

        "recommendation": {

            "final_packaging":
                baseline["packaging"],

            "final_material":
                baseline["material"],

            "why_selected": [

                "The recommendation is based on "
                "the product category and entered "
                "packaging characteristics."

            ],

            "benefits":
                baseline["features"],

            "shelf_life": {

                "user_target":
                    required_shelf_life,

                "assessment":
                    "Requires shelf-life validation."

            }

        },

        "qr_code":
            qr_image_url,

        "qr_url":
            qr_url

    })


# ============================================================
# SMART PACK INSPECTOR
# ============================================================

@app.route(
    "/api/inspector/analyze",
    methods=["POST"]
)
def inspector_analyze():

    # --------------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------------

    if "image" not in request.files:

        return jsonify({

            "success":
                False,

            "error":
                "Please upload a packaging image."

        }), 400


    image_file = request.files[
        "image"
    ]


    if (
        not image_file
        or image_file.filename == ""
    ):

        return jsonify({

            "success":
                False,

            "error":
                "Please select an image."

        }), 400


    # --------------------------------------------------------
    # IMAGE TYPES
    # --------------------------------------------------------

    allowed_types = {

        "image/jpeg",

        "image/png",

        "image/webp"

    }


    if image_file.mimetype not in allowed_types:

        return jsonify({

            "success":
                False,

            "error":
                "Please upload JPG, PNG or WEBP image."

        }), 400


    try:

        # ----------------------------------------------------
        # READ IMAGE
        # ----------------------------------------------------

        image_bytes = image_file.read()


        # ----------------------------------------------------
        # SIZE LIMIT
        # ----------------------------------------------------

        if len(image_bytes) > (
            20 * 1024 * 1024
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "Image must be smaller than 20 MB."

            }), 400


        # ----------------------------------------------------
        # SMARTPACK AI INSPECTION PROMPT
        # ----------------------------------------------------

        prompt = """

You are SmartPack AI, an intelligent food
packaging inspection assistant.

Analyze the uploaded packaging/product image.

IMPORTANT:

- Only report things that can reasonably be
  observed from the image.

- Do not invent laboratory test results.

- Do not claim that the package is food-safe
  based only on an image.

- Do not guarantee shelf life.

- If something cannot be determined visually,
  say:

"Cannot be determined from image."

Inspect:

1. Packaging type
2. Visible packaging condition
3. Visible damage
4. Seal condition, if visible
5. Label readability
6. Visible product/packaging information
7. Possible packaging concerns
8. Recommended action

Return ONLY valid JSON.

Use exactly this structure:

{
    "overall_status": "",
    "packaging_type": "",
    "condition": "",
    "seal_condition": "",
    "label_readability": "",
    "visible_information": [],
    "possible_issues": [],
    "recommended_action": "",
    "confidence_note": ""
}

For overall_status use ONLY:

"GOOD"

"NEEDS ATTENTION"

"UNABLE TO DETERMINE"

Keep the answer short and practical.

"""


        # ----------------------------------------------------
        # IMAGE REQUEST
        # ----------------------------------------------------

        result = (
            run_smartpack_ai_image_request(

                image_bytes,

                image_file.mimetype,

                prompt

            )
        )


        # ----------------------------------------------------
        # AI UNAVAILABLE
        # ----------------------------------------------------

        if not result["success"]:

            return jsonify({

                "success":
                    False,

                "error":
                    result["error"],

                "error_type":
                    result.get(
                        "error_type",
                        "api"
                    )

            }), 200


        # ----------------------------------------------------
        # CLEAN RESPONSE
        # ----------------------------------------------------

        text = result[
            "text"
        ].strip()


        if text.startswith("```"):

            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()


        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        parsed = json.loads(
            text
        )


        # ----------------------------------------------------
        # RETURN INSPECTION
        # ----------------------------------------------------

        return jsonify({

            "success":
                True,

            "engine":
                "SmartPack AI",

            "inspection":
                parsed

        })


    except json.JSONDecodeError:

        return jsonify({

            "success":
                False,

            "error":
                "SmartPack AI returned an invalid inspection result.",

            "error_type":
                "invalid_response"

        }), 200


    except Exception as e:

        print()
        print(
            "Smart Pack Inspector error:"
        )
        print(
            str(e)
        )
        print()


        return jsonify({

            "success":
                False,

            "error":
                "SmartPack AI could not inspect this image right now.",

            "error_type":
                "server_error"

        }), 200



# ============================================================
# SMART LOGISTICS
# ============================================================

def smart_logistics_analysis(data):

    prompt_data = {
        "product_name": data.get("product_name", ""),
        "category": data.get("category", ""),
        "pack_size": data.get("pack_size", ""),
        "shelf_life": data.get("shelf_life", ""),
        "packaging_material": data.get("packaging_material", ""),
        "origin": data.get("origin", ""),
        "destination": data.get("destination", ""),
        "transport_mode": data.get("transport_mode", ""),
        "transport_duration": data.get("transport_duration", ""),
        "temperature_controlled": data.get("temperature_controlled", ""),
        "perishability": data.get("perishability", ""),
        "temperature_requirement": data.get("temperature_requirement", ""),
        "humidity_sensitivity": data.get("humidity_sensitivity", ""),
        "light_sensitivity": data.get("light_sensitivity", ""),
        "respiration": data.get("respiration", "")
    }

    system_instruction = """
You are SmartPack AI, the logistics analysis engine of a smart food packaging system.

Analyze the supplied product and transport information. The food/product name is important and must be used when making the logistics guidance more relevant.

Rules:
- Give practical logistics guidance based only on the supplied information.
- Do not invent exact temperature, humidity or shelf-life values when they are not supported by the input.
- Do not guarantee food safety or shelf life.
- If information is insufficient, say that validation or product-specific data is required.
- Keep the answer compact.
- Return ONLY valid JSON.

Use exactly this structure:
{
  "recommended_temperature": "",
  "humidity_requirement": "",
  "light_protection": "",
  "cold_chain": "",
  "transport_recommendation": "",
  "risk_level": "",
  "handling_instructions": "",
  "main_logistics_risks": [],
  "explanation": ""
}

For risk_level use only LOW, MEDIUM, HIGH, or UNABLE TO DETERMINE.
"""

    result = run_smartpack_ai_request(
        json.dumps(prompt_data, indent=2),
        system_instruction
    )

    if not result["success"]:
        return {
            "available": False,
            "error_type": result.get("error_type", "api"),
            "error": result["error"]
        }

    try:
        text = result["text"].strip()

        if text.startswith("```"):
            text = text.replace("```json", "", 1)
            text = text.replace("```", "")
            text = text.strip()

        parsed = json.loads(text)

        return {
            "available": True,
            "result": parsed
        }

    except json.JSONDecodeError:
        return {
            "available": False,
            "error_type": "invalid_response",
            "error": "SmartPack AI returned an invalid logistics result."
        }


@app.route("/logistics")
def logistics():
    return render_template("logistics.html")


@app.route("/api/logistics/analyze", methods=["POST"])
def logistics_analyze():

    data = request.get_json(silent=True) or {}

    product_name = str(data.get("product_name", "")).strip()

    if not product_name:
        return jsonify({
            "success": False,
            "error": "Please enter the food or product name."
        }), 400

    ai_result = smart_logistics_analysis(data)

    if not ai_result["available"]:
        return jsonify({
            "success": False,
            "error": ai_result.get("error", "SmartPack AI is temporarily unavailable."),
            "error_type": ai_result.get("error_type", "api")
        }), 200

    return jsonify({
        "success": True,
        "engine": "SmartPack AI",
        "product_name": product_name,
        "logistics": ai_result["result"]
    })



# ============================================================
# SERVER START
# ============================================================

if __name__ == "__main__":

    print()

    print(
        "=========================================="
    )

    print(
        " Smart Food Packaging System"
    )

    print(
        "=========================================="
    )

    print(
        f"SmartPack AI model: "
        f"{SMARTPACK_AI_MODEL}"
    )

    print(
        f"SmartPack AI keys loaded: "
        f"{len(SMARTPACK_AI_KEYS)}"
    )

    print(
        f"BASE URL: "
        f"{BASE_URL}"
    )

    print(
        "Rule Engine: ENABLED"
    )

    print(
        "SmartPack AI: ENABLED"
    )

    print(
        "Manufacturer Portal: ENABLED"
    )

    print(
        "QR Generation: ENABLED"
    )

    print(
        "Universal QR URL: ENABLED"
    )

    print(
        "Product Web Page: ENABLED"
    )

    print(
        "Smart Pack Inspector: ENABLED"
    )

    print(
        "429 Handling: ENABLED"
    )

    print(
        "Server starting..."
    )

    print(
        "=========================================="
    )

    print()


    app.run(
        debug=True
    )
