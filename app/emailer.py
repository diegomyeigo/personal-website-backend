from flask import current_app
from flask_mail import Message
from . import mail

class EmailError(Exception):
    pass

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
        sender=current_app.config["MAIL_USERNAME"]
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

    with current_app.open_resource("email_assets/rigby.jpg") as img:
        message.attach(
            "rigby.jpg",
            "image/jpeg",
            data=img.read(),
            disposition="inline",
            headers={"Content-ID": "<rigby>"}
        )

    return message
