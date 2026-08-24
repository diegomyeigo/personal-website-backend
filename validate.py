from email_validator import validate_email, EmailNotValidError
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import os

def validate_form(form_data):
    valid, message, code = check_form_validity(form_data)

    if not valid:
        return valid, message, code, {}

    email = form_data["email"]
    
    valid, message, code = check_email(email)

    if not valid:
        return valid, message, code, {}

    try:
        database_record = prepare_for_database(form_data)
    except ValueError as err:
        return False, err, 422, {}
    except Exception as err:
        return False, err, 400, {}

    return True, "Form data successfully validated and prepared for database", 200, database_record


def check_form_validity(form_data):
    if not form_data:
        return False, "Invalid or missing JSON data", 400

    if form_data.get("granny", "").strip() != "":
        return False, "Bot detected!", 403

    required_fields = [
    "email",
    "age",
    "household",
    "income",
    "rent",
    "savings",
    "emergency"
    ]

    for field in required_fields:
        if field not in form_data:
            return False, f"Missing field: {field}", 422

    typed_fields = ["email", "income", "rent", "savings", "emergency"]

    for field in typed_fields:
        response = str(form_data[field])

        if response.strip() == "":
            return False, f"Missing input for {field}", 400

    return True, "Survey form valid", 200

def check_email(email):
    try:
        validate_email(email)
    except EmailNotValidError:
        return False, "Invalid email", 400

    DATABASE_URL = os.environ.get("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    try:
        database_emails = pd.read_sql("SELECT email FROM survey_responses", engine)
    except SQLAlchemyError as err:
        return False, f"Error fetching emails from database:\n{err}", 400
    except Exception as err:
        return False, f"Unexpected exception while fetching emails from database:\n{err}", 400

    if email in database_emails["email"].to_list():
        return False, "Duplicate Email", 409

    return True, "Valid email", 200

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

    age = str(form_data["age"])
    if age not in ["18-24", "25-34", "35-44", "45-54", "55+"]:
        raise ValueError(f"'{age}' is not a valid age option")

    database_record["age"] = age

    household = str(form_data["household"])
    if household not in ["alone", "1", "2", "3", "4+"]:
        raise ValueError(f"'{household}' is not a valid household option")
    
    database_record["household"] = household

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