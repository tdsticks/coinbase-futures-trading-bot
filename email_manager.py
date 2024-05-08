from flask_mail import Message
import logs
import os


class EmailManager:

    def __init__(self, flask_app, mail_cls):
        print(":Initializing EmailManager:")
        self.flask_app = flask_app
        self.log = logs.Log(flask_app)  # Send to Log or Console or both
        self.mail = mail_cls
        self.log.log(True, "D", None, ":Initializing TradeManager:")

    def send_email(self, subject='Test Email', body="Test Body"):
        self.log.log(True, "D", None, ":send_email:")
        self.log.log(True, "I", None, "Attempting to send email", subject)

        with self.flask_app.app_context():  # Push an application context
            try:
                msg_obj = Message(
                    subject=subject,
                    sender=os.getenv('MAIL_USERNAME'),  # Ensure this matches MAIL_USERNAME
                    recipients=[os.getenv('MAIL_USERNAME')]  # Replace with actual recipient's email
                )
                msg_obj.body = body
                self.mail.send(msg_obj)
                self.log.log(True, "I", None, "Email successfully sent.")
                # return "Message sent!"
            except Exception as e:
                self.log.log(True, "E", None, "Failed to send email", str(e))
                # return f"Failed to send message: {str(e)}"
