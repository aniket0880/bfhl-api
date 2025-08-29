import os
import re
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load .env file if present (for local development)
load_dotenv()

app = Flask(__name__)

# ---------- Helpers ----------
def build_user_id():
    """
    Builds a user_id from FULL_NAME and DOB in .env
    Example: aniket_baravkar_29082005
    """
    full_name = (os.getenv("FULL_NAME", "John Doe")
                 .strip()
                 .lower()
                 .replace(" ", "_"))
    dob = re.sub(r"\D", "", os.getenv("DOB_DDMMYYYY", "17091999"))
    return f"{full_name}_{dob}"

def is_integer_string(s):
    return isinstance(s, str) and re.fullmatch(r"[+-]?\d+", s)

def is_alphabetic(s):
    return isinstance(s, str) and re.fullmatch(r"[A-Za-z]+", s)

def classify(data):
    """
    Classify the input data list into numbers, alphabets, and special chars.
    Also computes sum and alternating-caps reversed concat string.
    """
    odd_numbers, even_numbers, alphabets, special_characters = [], [], [], []
    alpha_chars = []
    total = 0

    for item in data:
        item = str(item)

        # collect alphabet characters from ALL tokens
        for ch in item:
            if ch.isalpha():
                alpha_chars.append(ch)

        # classification rules
        if is_integer_string(item):
            num = int(item)
            total += num
            (even_numbers if num % 2 == 0 else odd_numbers).append(item)

        elif is_alphabetic(item):
            alphabets.append(item.upper())

        elif re.fullmatch(r"[^A-Za-z0-9]+", item):
            special_characters.append(item)

    # build concat_string
    reversed_chars = alpha_chars[::-1]
    concat_string = "".join(
        ch.upper() if i % 2 == 0 else ch.lower()
        for i, ch in enumerate(reversed_chars)
    )

    return {
        "odd_numbers": odd_numbers,
        "even_numbers": even_numbers,
        "alphabets": alphabets,
        "special_characters": special_characters,
        "sum": str(total),
        "concat_string": concat_string
    }

# ---------- Routes ----------
@app.route("/bfhl", methods=["POST"])
def bfhl():
    try:
        req_data = request.get_json(force=True)
        data = req_data.get("data")

        base = {
            "user_id": build_user_id(),
            "email": os.getenv("EMAIL", "john@xyz.com"),
            "roll_number": os.getenv("ROLL_NUMBER", "ABCD123")
        }

        # Validate input
        if not isinstance(data, list):
            return jsonify({
                "is_success": False,
                **base,
                "odd_numbers": [],
                "even_numbers": [],
                "alphabets": [],
                "special_characters": [],
                "sum": "0",
                "concat_string": "",
                "message": 'Invalid payload: "data" should be an array'
            }), 200

        # Process and return
        result = classify(data)
        return jsonify({
            "is_success": True,
            **base,
            **result
        }), 200

    except Exception as e:
        return jsonify({
            "is_success": False,
            "user_id": build_user_id(),
            "email": os.getenv("EMAIL", "john@xyz.com"),
            "roll_number": os.getenv("ROLL_NUMBER", "ABCD123"),
            "odd_numbers": [],
            "even_numbers": [],
            "alphabets": [],
            "special_characters": [],
            "sum": "0",
            "concat_string": "",
            "message": "Unexpected error",
            "error": str(e)
        }), 200

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "route": "/bfhl"})

# Only needed for local run
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
