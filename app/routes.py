from flask import request, jsonify, Blueprint
from .validation import validate_form, FormIntegrityError
from .database import insert_to_database, DuplicateError, DatabaseError
from .emailer import send_email, EmailError
from email_validator import EmailNotValidError

routes = Blueprint("routes", __name__)

def survey_submission_service(form):
    validated = validate_form(form)
    email = validated["email"]
    insert_to_database(validated)
    if email:
        send_email(email)

def create_json(success, message, code):
    return jsonify({
        "success": success,
        "message": message
        }), int(code)

@routes.route('/api/test')
def test():
    return {"message": "Successful NEW test"}


@routes.route('/api/survey', methods=["POST"])
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
