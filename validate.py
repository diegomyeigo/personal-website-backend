from email_validator import validate_email, EmailNotValidError

def validate_form(form_data):
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

    user_email = form_data["email"]

    try:
        validate_email(user_email)
    except EmailNotValidError:
        return False, "Invalid email", 400

    return True, "Survey form valid", 200