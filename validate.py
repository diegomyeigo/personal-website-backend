from email_validator import validate_email, EmailNotValidError

class FormIntegrityError(ValueError):
    pass

def validate_form(form_data):
    check_form_validity(form_data)

    email = str(form_data["email"]).strip()
    validate_email(email)
    
    try:
        database_record = prepare_for_database(form_data, email)
    except ValueError as e:
        raise FormIntegrityError("Invalid data") from e

    return database_record

def check_form_validity(form_data):
    if not form_data:
        raise FormIntegrityError("Empty json request")

    if form_data.get("granny", "").strip() != "":
        raise FormIntegrityError("Honeypot capture")

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
            raise FormIntegrityError(f"Missing field: {field}")

    typed_fields = ["email", "income", "rent", "savings", "emergency"]

    for field in typed_fields:
        response = str(form_data[field])

        if response.strip() == "":
            raise FormIntegrityError(f"Empty field: {field}")

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

def prepare_for_database(form_data, email):
    database_record = {}

    database_record["email"] = email

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