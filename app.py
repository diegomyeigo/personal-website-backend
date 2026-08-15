import os
import psycopg
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message


app = Flask(__name__)

CORS(app, origins=[
    "https://diegoperezanalytics.com",
    "http://127.0.0.1:5500"
])

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)

DATABASE_URL = os.environ.get("DATABASE_URL")



def get_db_connection():
    return psycopg.connect(DATABASE_URL)

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

    database_record["email"] = str(form_data["email"])
    database_record["age"] = str(form_data["age"])
    database_record["household"] = str(form_data["household"])

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


connection = get_db_connection()


@app.route('/api/test')
def test():
    return {"message": "Successful NEW test"}

@app.route('/api/survey', methods=["POST"])
def submit_survey():

    form_data = request.get_json(silent=True)

    print(form_data)

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

    user_email = database_record["email"]
    message = Message(
        subject="Thank you for taking my survey!",
        recipients=[user_email],
        sender="jdiegoperez001@gmail.com"
    )

    message.html = """
    <html>
        <body>
            <p><b>**This is an automated message. Please do not respond**</b></p>
            <br>
            <h1>Thank you!</h1>
            <br><br>
            <p>Thanks for taking the time to complete my survey</p>
            <p>You're alright ;)</p>
            <br>
            <img src="cid:rigby" alt="Rigby the cat" width="300" height="300">
        </body>
    </html>
    """

    with app.open_resource("email_assets/rigby.jpg") as img:
        message.attach(
            filename="email_assets/rigby.jpg",
            content_type="image/jpeg",
            data=img.read(),
            disposition="inline",
            headers=[("Content-ID", "<rigby>")]
        )

    try:
        mail.send(message)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Email error: {e}"
        }), 500

    return jsonify(database_record), 200

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