from flask_mail import Message
import os


class EmailManager:

    def __init__(self, app):
        # print(":Initializing EmailManager:")
        self.log = app.custom_log.log
        self.log(True, "D", None, ":Initializing TradeManager:")

        self.app = app
        self.mail = app.mail

    def send_email(self, subject='Test Email', body="Test Body"):
        self.log(True, "D", None, ":send_email:")
        self.log(True, "I", None, "Attempting to send email", subject)

        with self.app.app_context():  # Push an application context
            try:
                msg_obj = Message(
                    subject=subject,
                    sender=os.getenv('MAIL_USERNAME'),  # Ensure this matches MAIL_USERNAME
                    recipients=[os.getenv('MAIL_USERNAME')]  # Replace with actual recipient's email
                )
                msg_obj.body = body
                self.mail.send(msg_obj)
                self.app.custom_log.log(True, "I", None, "Email successfully sent.")
                # return "Message sent!"
            except Exception as e:
                self.log(True, "E", None, "Failed to send email", str(e))
                # return f"Failed to send message: {str(e)}"
