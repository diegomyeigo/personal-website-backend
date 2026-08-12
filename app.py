from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "https://diegoperezanalytics.com",
    "http://127.0.0.1:5500"
])


def convert_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def validate_range(number):
    if number is None:
        return None
    
    if (number < 0) or (number > 1_000_000_000):
        return None

    return number

def prepare_for_database(form_data):
    database_record = {}

    database_record["age"] = form_data["age"]
    database_record["household"] = form_data["household"]

    typed_fields = ["income", "rent", "savings", "emergency"]

    for field in typed_fields:
        raw_value = form_data[field]

        number_value = convert_number(raw_value)

        if number_value is None:
            raise ValueError(f"{field} must be a valid number")

        validated_number = validate_range(number_value)

        if validated_number is None:
            raise ValueError(f"{field} is outside of allowed range")

        database_record[field] = validated_number

    return database_record


@app.route('/api/test')
def test():
    return {"message": "Successful NEW test"}

@app.route('/api/survey', methods=["POST"])
def submit_survey():

    form_data = request.get_json(silent=True)

    if not form_data:
        return jsonify({
            "success": False,
            "message": "Invalid or missing JSON data"
        }), 400

    if form_data.get("granny", "").strip() != "":
        return jsonify({
            "success": False,
            "message": "Bot detected!"
        }), 403

    required_fields = [
        "age",
        "household",
        "income",
        "rent",
        "savings",
        "emergency"
    ]

    for field in required_fields:
        if field not in form_data:
            return jsonify({
                "success": False,
                "message": f"Missing field: {field}"
            }), 422

    try:
        database_record = prepare_for_database(form_data)

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 422


    return jsonify({
        "success": True,
        "message": "Looks good!"
    }), 200

@app.route("/api/routes")
def routes():
    return {
        "routes": [
            str(rule)
            for rule in app.url_map.iter_rules()
        ]
    }

if __name__ == '__main__':
    app.run(debug=True)