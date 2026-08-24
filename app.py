import os
import psycopg
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from validate import validate_form


app = Flask(__name__)

ORIGIN = os.environ.get("CORS_ORIGIN")
CORS(app, origins=[ORIGIN])

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    return psycopg.connect(DATABASE_URL)

def generate_email_message(user_email):
    message = Message(
        subject="Successful survey submission!",
        # body="Thanks for taking the time to complete my survey!\nYou're alright ;)\n\n",
        recipients=[user_email],
        sender="jdiegoperez001@gmail.com"
    )

    message.html = """
    <html>
        <body>
            <p><b>**This is an automated message. Please do not respond**</b></p>
            <h2>Thanks for taking some time to complete my survey</h2>
            <p>I don't care what everyone else says about you..</p>
            <p>You're alright ;)</p>
            <img src="cid:rigby" alt="Rigby the cat" width="300" height="300">
        </body>
    </html>
    """         

    with app.open_resource("email_assets/rigby.jpg") as img:
        message.attach(
            "rigby.jpg",
            "image/jpeg",
            data=img.read(),
            disposition="inline",
            headers={"Content-ID": "<rigby>"}
        )

    return message


@app.route('/api/test')
def test():
    return {"message": "Successful NEW test"}


@app.route('/api/survey', methods=["POST"])
def submit_survey():

    form_data = request.get_json(silent=True)
    print(form_data)

    valid, message, code, record = validate_form(form_data)

#   add email_duplicate_validation, move email sending after database insertion (perhaps createa module first)
    print(message)
    if not valid:
        return jsonify({
            "message": message
        }), code

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO survey_responses (
            email,
            age,
            household,
            income,
            rent,
            savings,
            emergency_funds
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            record["email"],
            record["age"],
            record["household"],
            record["income"],
            record["rent"],
            record["savings"],
            record["emergency"]
        ))

        connection.commit()

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "success": False,
            "message": "Duplicate Email"
        }), 409

    except Exception as e:
        connection.rollback()
        print(e)

        return jsonify({
            "success": False,
            "error": "Database error"
        }), 500

    finally:
        connection.close()

    email = form_data["email"]
    message = generate_email_message(email)

    try:
        mail.send(message)
    except Exception as e:
        print(f"Email error: {e}")
        return jsonify({
            "message": f"Email error: {e}"
        }), 500

    return jsonify({
        "success": True,
        "message": "Record added to database and confirmation email sent"
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