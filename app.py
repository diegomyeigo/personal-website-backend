import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from validate import validate_form
from database import insert_to_database


app = Flask(__name__)

ORIGIN = os.environ.get("CORS_ORIGIN")
CORS(app, origins=[ORIGIN])

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)

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

def create_json(message, code):
    return jsonify({"message": message}), int(code)

@app.route('/api/test')
def test():
    return {"message": "Successful NEW test"}


@app.route('/api/survey', methods=["POST"])
def submit_survey():

    form_data = request.get_json(silent=True)
    print(form_data)

    valid, message, code, record = validate_form(form_data)

    print(message)
    if not valid:
        return create_json(message, code)

    valid, message, code = insert_to_database(record)

    print(message)
    if not valid:
        return create_json(message, code)

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