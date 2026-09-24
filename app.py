from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

from datetime import datetime
import uuid
import os
import json
import threading
import re
from urllib.parse import urlparse

from recommendation_db import (
    get_database_recommendation,
    get_authoritative_sources,
)

# ============================================================
# APP SETUP
# ============================================================

app = Flask(__name__)
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000").strip().rstrip("/")

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
SMARTPACK_AI_KEYS = [k.strip() for k in SMARTPACK_AI_KEYS if k and k.strip()]
current_key_index = 0

# ============================================================
# TEMPORARY PRODUCT DATABASE
# ============================================================

PRODUCT_DATABASE = {}
RECOMMENDATION_JOBS = {}
RECOMMENDATION_JOBS_LOCK = threading.Lock()

# ============================================================
# SMARTPACK AI HELPERS
# ============================================================

def get_smartpack_ai_client():
    if not SMARTPACK_AI_KEYS:
        return None
    return genai.Client(api_key=SMARTPACK_AI_KEYS[current_key_index])


def move_to_next_key():
    global current_key_index
    if SMARTPACK_AI_KEYS:
        current_key_index = (current_key_index + 1) % len(SMARTPACK_AI_KEYS)


def is_quota_error(error_text):
    text = str(error_text).lower()
    return any(word in text for word in [
        "resource_exhausted",
        "quota exceeded",
        "quota_exceeded",
        "generate_requests_per_day",
        "generaterequestsperday",
        "429",
    ])


def is_temporary_rate_limit(error_text):
    text = str(error_text).lower()
    return any(word in text for word in [
        "rate_limit_exceeded",
        "too many requests",
        "retryinfo",
        "requests per minute",
        "requests per second",
    ])


def get_user_friendly_ai_error(error_text):
    if is_quota_error(error_text):
        return (
            "SmartPack AI is temporarily unavailable because the current "
            "AI usage limit has been reached. Please try again later."
        )
    if is_temporary_rate_limit(error_text):
        return "SmartPack AI is temporarily busy. Please wait a moment and try again."
    return "SmartPack AI could not process the request right now. Please try again."


def run_smartpack_ai_request(prompt, system_instruction):
    if not SMARTPACK_AI_KEYS:
        return {
            "success": False,
            "error_type": "configuration",
            "error": "SmartPack AI is not configured.",
        }

    last_error = "Unknown SmartPack AI error."

    for _ in range(len(SMARTPACK_AI_KEYS)):
        try:
            client = get_smartpack_ai_client()
            response = client.interactions.create(
                model=SMARTPACK_AI_MODEL,
                input=prompt,
                system_instruction=system_instruction,
            )
            return {"success": True, "text": response.output_text}

        except Exception as exc:
            last_error = str(exc)
            print("\nSmartPack AI request error:\n", last_error, "\n")

            if is_quota_error(last_error):
                return {
                    "success": False,
                    "error_type": "quota",
                    "error": get_user_friendly_ai_error(last_error),
                }

            move_to_next_key()

    return {
        "success": False,
        "error_type": "api",
        "error": get_user_friendly_ai_error(last_error),
    }


def run_smartpack_ai_image_request(image_bytes, mime_type, prompt):
    if not SMARTPACK_AI_KEYS:
        return {
            "success": False,
            "error_type": "configuration",
            "error": "SmartPack AI is not configured.",
        }

    last_error = "Unknown SmartPack AI error."

    for _ in range(len(SMARTPACK_AI_KEYS)):
        try:
            client = get_smartpack_ai_client()
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            )

            response = client.models.generate_content(
                model=SMARTPACK_AI_MODEL,
                contents=[image_part, prompt],
            )

            return {"success": True, "text": response.text}

        except Exception as exc:
            last_error = str(exc)
            print("\nSmartPack AI image request error:\n", last_error, "\n")

            if is_quota_error(last_error):
                return {
                    "success": False,
                    "error_type": "quota",
                    "error": get_user_friendly_ai_error(last_error),
                }

            move_to_next_key()

    return {
        "success": False,
        "error_type": "api",
        "error": get_user_friendly_ai_error(last_error),
    }


def clean_json_text(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.replace("```json", "", 1)
        text = text.replace("```", "")
    return text.strip()

# ============================================================
# API ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def handle_not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "error": "API endpoint not found: " + request.path,
        }), 404
    return error


@app.errorhandler(500)
def handle_server_error(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "error": "SmartPack server error while processing the request.",
        }), 500
    return error

# ============================================================
# BASIC PAGES
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommendation")
def recommendation():
    return render_template("recommendation.html")


@app.route("/manufacturer")
def manufacturer():
    return render_template("manufacturer.html")


@app.route("/inspector")
def inspector():
    return render_template("inspector.html")


@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/logistics")
def logistics():
    return render_template("logistics.html")

# ============================================================
# PRODUCT QR PAGE
# ============================================================

@app.route("/product/<product_id>")
def product_page(product_id):
    product = PRODUCT_DATABASE.get(product_id)

    if not product:
        return render_template(
            "product.html",
            product=None,
            error="This product information is not available on the server.",
        ), 404

    return render_template(
        "product.html",
        product=product,
        error=None,
    )

# ============================================================
# RECOMMENDATION AI
# ============================================================

def smartpack_ai_analysis(data, baseline):
    prompt_data = {
        "product": data.get("product"),
        "category": data.get("category"),
        "moisture": data.get("moisture"),
        "oxygen": data.get("oxygen"),
        "light": data.get("light"),
        "perishability": data.get("perishability"),
        "respiration": data.get("respiration"),
        "old_material": data.get("old_material"),
        "pack_size": data.get("pack_size"),
        "old_packaging_cost": data.get("old_packaging_cost"),
        "required_shelf_life": data.get("required_shelf_life"),
        "baseline_recommendation": baseline,
        "official_reference_sources": get_authoritative_sources(),
    }

    system_instruction = """
You are SmartPack AI, the intelligent analysis engine of an intelligent
food packaging recommendation system.

Improve and explain the existing rule-based packaging recommendation.

Rules:
1. Never blindly replace the existing recommendation.
2. Use the existing recommendation as the baseline.
3. Improve it only when product characteristics justify the improvement.
4. Do not invent packaging prices, market prices, laboratory results or
   guaranteed shelf life.
5. Required shelf life is a target.
6. If shelf life cannot be confidently assessed, say "Requires shelf-life validation."
7. Show cost comparison only when reliable cost information exists.
8. If cost information is missing, use "Not available".
9. Clearly identify the old material before comparing it.
10. If the old material is suitable and there is no meaningful improvement,
    do not force a new recommendation.
11. Sustainable packaging is optional and must not automatically be called better.
12. Mention relevant trade-offs.
13. Keep final information compact. Prefer short bullets.
14. Clearly explain WHY the material was selected.
15. Evidence must be separated from the recommendation.
16. Do not claim a source was checked unless it is supplied.
17. Use supplied official sources only as reference context.
18. Do not claim any regulator approved the specific SmartPack recommendation.
19. This is prototype guidance, not certified food-safety or packaging approval.

Return ONLY valid JSON:
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

    result = run_smartpack_ai_request(
        json.dumps(prompt_data, indent=2),
        system_instruction,
    )

    if not result["success"]:
        return {
            "available": False,
            "error_type": result.get("error_type", "api"),
            "error": result["error"],
        }

    try:
        parsed = json.loads(clean_json_text(result["text"]))
        parsed["evidence"] = get_authoritative_sources()

        return {
            "available": True,
            "result": parsed,
        }

    except json.JSONDecodeError:
        return {
            "available": False,
            "error_type": "invalid_response",
            "error": "SmartPack AI returned an invalid result.",
        }


def _run_recommendation_ai_job(job_id, data, baseline):
    try:
        with RECOMMENDATION_JOBS_LOCK:
            job = RECOMMENDATION_JOBS.get(job_id)
            if not job:
                return
            job["status"] = "running"
            job["started_at"] = datetime.now().isoformat(timespec="seconds")

        ai_result = smartpack_ai_analysis(data, baseline)

        with RECOMMENDATION_JOBS_LOCK:
            job = RECOMMENDATION_JOBS.get(job_id)
            if not job:
                return

            if ai_result.get("available"):
                job["status"] = "completed"
                job["recommendation"] = ai_result["result"]
                job["completed_at"] = datetime.now().isoformat(timespec="seconds")
            else:
                job["status"] = "failed"
                job["error_type"] = ai_result.get("error_type", "api")
                job["error"] = ai_result.get(
                    "error",
                    "SmartPack AI could not complete the analysis.",
                )
                job["completed_at"] = datetime.now().isoformat(timespec="seconds")

    except Exception as exc:
        print("Background SmartPack AI recommendation error:", str(exc))
        with RECOMMENDATION_JOBS_LOCK:
            job = RECOMMENDATION_JOBS.get(job_id)
            if job:
                job["status"] = "failed"
                job["error_type"] = "server_error"
                job["error"] = "SmartPack AI could not complete the analysis."
                job["completed_at"] = datetime.now().isoformat(timespec="seconds")


def _start_recommendation_job(data, baseline):
    job_id = str(uuid.uuid4())

    with RECOMMENDATION_JOBS_LOCK:
        RECOMMENDATION_JOBS[job_id] = {
            "status": "queued",
            "recommendation": None,
            "error": None,
            "error_type": None,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }

    threading.Thread(
        target=_run_recommendation_ai_job,
        args=(job_id, data, baseline),
        daemon=True,
        name=f"smartpack-ai-{job_id[:8]}",
    ).start()

    return job_id


@app.route("/api/recommend/start", methods=["POST"])
def recommend_start():
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({
            "success": False,
            "error": "No product information received.",
        }), 400

    product = str(data.get("product", "")).strip()
    category = str(data.get("category", "")).strip()
    shelf = str(data.get("required_shelf_life", "")).strip()

    if not product:
        return jsonify({"success": False, "error": "Please enter a product name."}), 400

    if not category:
        return jsonify({"success": False, "error": "Please select the product category."}), 400

    if not shelf:
        return jsonify({"success": False, "error": "Please enter the required shelf life."}), 400

    baseline = get_database_recommendation(data)
    job_id = _start_recommendation_job(data, baseline)

    return jsonify({
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "engine": "SmartPack Database",
        "product": product,
        "baseline": baseline,
    })


@app.route("/api/recommend", methods=["POST"])
@app.route("/api/recommendation", methods=["POST"])
def recommend_legacy():
    return recommend_start()


@app.route("/api/recommend/status/<job_id>", methods=["GET"])
def recommendation_status(job_id):
    with RECOMMENDATION_JOBS_LOCK:
        job = RECOMMENDATION_JOBS.get(job_id)

        if not job:
            return jsonify({
                "success": False,
                "status": "not_found",
                "error": "Recommendation job was not found.",
            }), 404

        response = {
            "success": True,
            "status": job.get("status", "queued"),
        }

        if job.get("status") == "completed":
            response["recommendation"] = job.get("recommendation")

        elif job.get("status") == "failed":
            response["error"] = job.get(
                "error",
                "SmartPack AI could not complete the analysis.",
            )
            response["error_type"] = job.get("error_type", "api")

        return jsonify(response)

# ============================================================
# CHATBOT
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({
            "success": False,
            "error": "No message received.",
        }), 400

    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({
            "success": False,
            "error": "Please enter a question.",
        }), 400

    system_instruction = """
You are SmartPack AI, the conversational assistant inside a smart food
packaging system.

Answer reasonable questions about:
- food packaging
- packaging materials
- Indian food packaging
- moisture, oxygen and light protection
- shelf-life concepts
- storage and cold chain
- food logistics
- sustainable packaging
- packaging cost and comparison
- packaging inspection
- QR/product information
- SmartPack system

Use simple English, short practical answers and bullets where useful.

Do not invent scientific facts, prices, regulations or laboratory results.
Do not guarantee shelf life or food safety.
If information is insufficient, say so.
If unrelated to food packaging, politely explain the scope.
"""

    result = run_smartpack_ai_request(
        message,
        system_instruction,
    )

    if not result["success"]:
        return jsonify({
            "success": False,
            "error": result["error"],
            "error_type": result.get("error_type", "api"),
        }), 200

    return jsonify({
        "success": True,
        "reply": result["text"],
    })

# ============================================================
# MANUFACTURER PORTAL + QR GENERATION
# ============================================================

@app.route("/api/manufacturer/create", methods=["POST"])
def manufacturer_create():
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({
            "success": False,
            "error": "No manufacturer information received.",
        }), 400

    fields = [
        "manufacturer_name",
        "brand_name",
        "manufacturer_address",
        "product",
        "category",
        "pack_size",
        "batch_number",
        "manufacturing_date",
        "expiry_date",
        "required_shelf_life",
        "old_material",
        "old_packaging_cost",
        "moisture",
        "oxygen",
        "light",
        "perishability",
        "respiration",
    ]

    values = {
        field: str(data.get(field, "")).strip()
        for field in fields
    }

    for required in [
        "manufacturer_name",
        "brand_name",
        "product",
        "category",
        "pack_size",
        "batch_number",
    ]:
        if not values[required]:
            labels = {
                "manufacturer_name": "manufacturer",
                "brand_name": "brand",
                "product": "product",
                "category": "category",
                "pack_size": "pack size",
                "batch_number": "batch / lot number",
            }
            return jsonify({
                "success": False,
                "error": f"Please enter {labels[required]}.",
            }), 400

    baseline = get_database_recommendation({
        "product": values["product"],
        "category": values["category"],
        "moisture": values["moisture"],
        "oxygen": values["oxygen"],
        "light": values["light"],
        "perishability": values["perishability"],
        "respiration": values["respiration"],
        "old_material": values["old_material"],
        "pack_size": values["pack_size"],
        "old_packaging_cost": values["old_packaging_cost"],
        "required_shelf_life": values["required_shelf_life"],
    })

    product_id = str(uuid.uuid4())
    generated_at = datetime.now().isoformat(timespec="seconds")

    product_record = {
        "product_id": product_id,
        "manufacturer_name": values["manufacturer_name"],
        "brand_name": values["brand_name"],
        "manufacturer_address": values["manufacturer_address"],
        "product": values["product"],
        "category": values["category"],
        "pack_size": values["pack_size"],
        "batch_number": values["batch_number"],
        "manufacturing_date": values["manufacturing_date"],
        "expiry_date": values["expiry_date"],
        "required_shelf_life": values["required_shelf_life"],
        "old_material": values["old_material"],
        "old_packaging_cost": values["old_packaging_cost"],
        "recommended_packaging": baseline["final_packaging"],
        "recommended_material": baseline["final_material"],
        "packaging_features": baseline["benefits"],
        "shelf_life_assessment": "Requires shelf-life validation.",
        "generated_at": generated_at,
    }

    PRODUCT_DATABASE[product_id] = product_record

    qr_url = f"{BASE_URL}/product/{product_id}"

    try:
        import qrcode

        qr_directory = os.path.join(
            app.static_folder,
            "qr_codes",
        )
        os.makedirs(qr_directory, exist_ok=True)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        qr_filename = f"smartpack_{product_id}.png"
        qr_path = os.path.join(
            qr_directory,
            qr_filename,
        )
        qr_image.save(qr_path)

    except Exception as exc:
        print("QR generation error:", str(exc))
        PRODUCT_DATABASE.pop(product_id, None)

        return jsonify({
            "success": False,
            "error": "Could not generate QR code.",
        }), 500

    qr_image_url = f"/static/qr_codes/{qr_filename}"

    product_data = {
        "brand_name": values["brand_name"],
        "product": values["product"],
        "category": values["category"],
        "pack_size": values["pack_size"],
        "batch_number": values["batch_number"],
        "manufacturing_date": values["manufacturing_date"],
        "expiry_date": values["expiry_date"],
    }

    return jsonify({
        "success": True,
        "product_id": product_id,
        "generated_at": generated_at,
        "product_data": product_data,
        "recommendation": {
            "final_packaging": baseline["final_packaging"],
            "final_material": baseline["final_material"],
            "why_selected": [
                "The recommendation is based on the product category and entered packaging characteristics."
            ],
            "benefits": baseline["benefits"],
            "shelf_life": {
                "user_target": values["required_shelf_life"],
                "assessment": "Requires shelf-life validation.",
            },
        },
        "qr_code": qr_image_url,
        "qr_url": qr_url,
    })

# ============================================================
# QR DECODER FOR INSPECTOR
# ============================================================

def decode_qr_from_image(image_bytes):
    """
    Attempts to decode a QR from a captured/uploaded image.

    OpenCV is the primary decoder. pyzbar/Pillow is a fallback.
    """

    try:
        import cv2
        import numpy as np

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )

        if image is not None:
            detector = cv2.QRCodeDetector()

            decoded_text, points, _ = detector.detectAndDecode(image)

            if decoded_text:
                return {
                    "success": True,
                    "data": decoded_text.strip(),
                    "method": "OpenCV QR detector",
                }

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY,
            )

            for variant in [
                gray,
                cv2.equalizeHist(gray),
            ]:
                decoded_text, points, _ = detector.detectAndDecode(variant)

                if decoded_text:
                    return {
                        "success": True,
                        "data": decoded_text.strip(),
                        "method": "OpenCV QR detector",
                    }

    except Exception as exc:
        print("OpenCV QR decoder unavailable:", str(exc))

    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(image_bytes))
        results = decode(image)

        for result in results:
            try:
                decoded_data = result.data.decode(
                    "utf-8",
                    errors="replace",
                ).strip()
            except Exception:
                decoded_data = str(result.data).strip()

            if decoded_data:
                return {
                    "success": True,
                    "data": decoded_data,
                    "method": "pyzbar",
                }

    except Exception as exc:
        print("pyzbar QR decoder unavailable:", str(exc))

    return {
        "success": False,
        "data": "",
        "error": "No readable QR code was found in the image.",
    }


def extract_smartpack_product_id(qr_data):
    if not qr_data:
        return None

    value = qr_data.strip()

    try:
        parsed = urlparse(value)

        match = re.search(
            r"/product/([A-Za-z0-9-]+)",
            parsed.path or "",
        )

        if match:
            return match.group(1)

    except Exception:
        pass

    match = re.search(
        r"/product/([A-Za-z0-9-]+)",
        value,
    )

    if match:
        return match.group(1)

    return None


def build_qr_result(qr_data, decode_method):
    product_id = extract_smartpack_product_id(qr_data)

    result = {
        "decoded": True,
        "data": qr_data,
        "decode_method": decode_method,
        "source_type": "External QR",
        "product_found": False,
        "product": None,
        "message": "QR code decoded successfully.",
    }

    if product_id:
        result["source_type"] = "SmartPack Product QR"
        result["product_id"] = product_id

        product = PRODUCT_DATABASE.get(product_id)

        if product:
            result["product_found"] = True

            result["product"] = {
                "product_id": product.get("product_id"),
                "manufacturer_name": product.get("manufacturer_name"),
                "brand_name": product.get("brand_name"),
                "manufacturer_address": product.get("manufacturer_address"),
                "product": product.get("product"),
                "category": product.get("category"),
                "pack_size": product.get("pack_size"),
                "batch_number": product.get("batch_number"),
                "manufacturing_date": product.get("manufacturing_date"),
                "expiry_date": product.get("expiry_date"),
                "required_shelf_life": product.get("required_shelf_life"),
                "recommended_packaging": product.get("recommended_packaging"),
                "recommended_material": product.get("recommended_material"),
                "packaging_features": product.get("packaging_features"),
                "shelf_life_assessment": product.get("shelf_life_assessment"),
                "generated_at": product.get("generated_at"),
            }

            result["message"] = "SmartPack product record found."

        else:
            result["message"] = (
                "This QR looks like a SmartPack product QR, but its "
                "product record is not available on this server."
            )

    return result


@app.route("/api/inspector/qr", methods=["POST"])
def inspector_qr():
    if "qr_image" not in request.files:
        return jsonify({
            "success": False,
            "error": "Please upload or capture a QR image.",
        }), 400

    qr_file = request.files["qr_image"]

    if not qr_file or qr_file.filename == "":
        return jsonify({
            "success": False,
            "error": "Please select a QR image.",
        }), 400

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if qr_file.mimetype not in allowed_types:
        return jsonify({
            "success": False,
            "error": "Please use JPG, PNG or WEBP.",
        }), 400

    try:
        image_bytes = qr_file.read()

        if len(image_bytes) > 20 * 1024 * 1024:
            return jsonify({
                "success": False,
                "error": "Image must be smaller than 20 MB.",
            }), 400

        decoded = decode_qr_from_image(image_bytes)

        if not decoded.get("success"):
            return jsonify({
                "success": False,
                "error": decoded.get(
                    "error",
                    "No readable QR code was found.",
                ),
            }), 200

        qr_result = build_qr_result(
            decoded["data"],
            decoded.get("method", "QR detector"),
        )

        return jsonify({
            "success": True,
            "qr": qr_result,
        })

    except Exception as exc:
        print("Inspector QR error:", str(exc))

        return jsonify({
            "success": False,
            "error": "SmartPack could not read this QR image.",
            "error_type": "server_error",
        }), 200

# ============================================================
# SMART PACK INSPECTOR - EXISTING IMAGE ANALYSIS
# ============================================================

@app.route("/api/inspector/analyze", methods=["POST"])
def inspector_analyze():
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "Please upload a packaging image.",
        }), 400

    image_file = request.files["image"]

    if not image_file or image_file.filename == "":
        return jsonify({
            "success": False,
            "error": "Please select an image.",
        }), 400

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if image_file.mimetype not in allowed_types:
        return jsonify({
            "success": False,
            "error": "Please upload JPG, PNG or WEBP image.",
        }), 400

    try:
        image_bytes = image_file.read()

        if len(image_bytes) > 20 * 1024 * 1024:
            return jsonify({
                "success": False,
                "error": "Image must be smaller than 20 MB.",
            }), 400

        # Optional QR detection from the same packaging image.
        # This DOES NOT replace image analysis.
        qr_result = None

        try:
            qr_decoded = decode_qr_from_image(image_bytes)

            if qr_decoded.get("success"):
                qr_result = build_qr_result(
                    qr_decoded["data"],
                    qr_decoded.get("method", "QR detector"),
                )

        except Exception as exc:
            print("Optional QR detection error:", str(exc))

        prompt = """
You are SmartPack AI, an intelligent food packaging inspection assistant.

Analyze the uploaded packaging/product image.

IMPORTANT:
- Only report things that can reasonably be observed from the image.
- Do not invent laboratory test results.
- Do not claim that the package is food-safe based only on an image.
- Do not guarantee shelf life.
- If something cannot be determined visually, say:
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

        result = run_smartpack_ai_image_request(
            image_bytes,
            image_file.mimetype,
            prompt,
        )

        if not result["success"]:
            return jsonify({
                "success": False,
                "error": result["error"],
                "error_type": result.get("error_type", "api"),
            }), 200

        parsed = json.loads(clean_json_text(result["text"]))

        return jsonify({
            "success": True,
            "engine": "SmartPack AI",
            "inspection": parsed,
            "qr": qr_result,
        })

    except json.JSONDecodeError:
        return jsonify({
            "success": False,
            "error": "SmartPack AI returned an invalid inspection result.",
            "error_type": "invalid_response",
        }), 200

    except Exception as exc:
        print("\nSmart Pack Inspector error:\n", str(exc), "\n")

        return jsonify({
            "success": False,
            "error": "SmartPack AI could not inspect this image right now.",
            "error_type": "server_error",
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
        "respiration": data.get("respiration", ""),
    }

    system_instruction = """
You are SmartPack AI, the logistics analysis engine of a smart food packaging system.

Analyze the supplied product and transport information. The food/product name
is important and must be used when making logistics guidance more relevant.

Rules:
- Give practical logistics guidance based only on supplied information.
- Do not invent exact temperature, humidity or shelf-life values.
- Do not guarantee food safety or shelf life.
- If information is insufficient, say validation or product-specific data is required.
- Keep the answer compact.
- Return ONLY valid JSON.

Use exactly:
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
        system_instruction,
    )

    if not result["success"]:
        return {
            "available": False,
            "error_type": result.get("error_type", "api"),
            "error": result["error"],
        }

    try:
        parsed = json.loads(clean_json_text(result["text"]))
        return {
            "available": True,
            "result": parsed,
        }
    except json.JSONDecodeError:
        return {
            "available": False,
            "error_type": "invalid_response",
            "error": "SmartPack AI returned an invalid logistics result.",
        }


@app.route("/api/logistics/analyze", methods=["POST"])
def logistics_analyze():
    data = request.get_json(silent=True) or {}
    product_name = str(data.get("product_name", "")).strip()

    if not product_name:
        return jsonify({
            "success": False,
            "error": "Please enter the food or product name.",
        }), 400

    ai_result = smart_logistics_analysis(data)

    if not ai_result["available"]:
        return jsonify({
            "success": False,
            "error": ai_result.get(
                "error",
                "SmartPack AI is temporarily unavailable.",
            ),
            "error_type": ai_result.get("error_type", "api"),
        }), 200

    return jsonify({
        "success": True,
        "engine": "SmartPack AI",
        "product_name": product_name,
        "logistics": ai_result["result"],
    })

# ============================================================
# SERVER START
# ============================================================

if __name__ == "__main__":
    print()
    print("==========================================")
    print(" Smart Food Packaging System")
    print("==========================================")
    print(f"SmartPack AI model: {SMARTPACK_AI_MODEL}")
    print(f"SmartPack AI keys loaded: {len(SMARTPACK_AI_KEYS)}")
    print(f"BASE URL: {BASE_URL}")
    print("Rule Engine: ENABLED")
    print("SmartPack AI: ENABLED")
    print("Manufacturer Portal: ENABLED")
    print("QR Generation: ENABLED")
    print("QR Image Upload: ENABLED")
    print("QR Camera Support: ENABLED")
    print("SmartPack QR Product Lookup: ENABLED")
    print("Universal QR Decode API: ENABLED")
    print("Product Web Page: ENABLED")
    print("Smart Pack Inspector: ENABLED")
    print("Inspector Image Analysis: ENABLED")
    print("429 Handling: ENABLED")
    print("==========================================")
    print()

    app.run(debug=True)
