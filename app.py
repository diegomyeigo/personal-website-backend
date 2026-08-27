import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from validate import validate_form, FormIntegrityError
from database import insert_to_database, DuplicateError, DatabaseError
from email_validator import EmailNotValidError


app = Flask(__name__)

ORIGIN = os.environ.get("CORS_ORIGIN")
CORS(app, origins=[ORIGIN])

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)

class EmailError(Exception):
    pass

def survey_submission_service(form):
    validated = validate_form(form)
    email = validated["email"]
    insert_to_database(validated)
    send_email(email)

def send_email(email):
    message = generate_email_message(email)

    try:
        mail.send(message)
    except Exception as e:
        raise EmailError(f"Unexpected error occurred while sending email\n{e}")

def generate_email_message(email):
    message = Message(
        subject="Successful survey submission!",
        recipients=[email],
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

def create_json(success, message, code):
    return jsonify({
        "success": success,
        "message": message
        }), int(code)

@app.route('/api/test')
def test():
    return {"message": "Successful NEW test"}


@app.route('/api/survey', methods=["POST"])
def submit_survey():

    form = request.get_json(silent=True)
    print(form)

    try:
        survey_submission_service(form)

    except FormIntegrityError as e:
        print(e)
        return create_json(False, "FormIntegrityError", 400)
    except EmailNotValidError:
        print("Invalid email")
        return create_json(False, "InvalidEmail", 400)
    except DuplicateError as e:
        print(e)
        return create_json(False, "DuplicateError", 409)
    except DatabaseError as e:
        print(e)
        return create_json(False, "DatabaseError", 503)
    except EmailError as e:
        print(e)
        return create_json(False, "EmailError", 500)
    except Exception as e:
        print(e)
        return create_json(False, "UnexpectedError", 500)

    print("Submission successful!")
    return create_json(True, "Survey Submission Service Successful", 200)

if __name__ == '__main__':
    app.run(debug=True)