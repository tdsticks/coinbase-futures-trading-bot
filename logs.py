

class Log:

    def __init__(self, flask_app):
        """
        Class to send messages to logging or console or both
        """
        self.flask_app = flask_app

    def log(self, log=True, level="I", subject=None, msg1=None, msg2=None):
        """
        Function to send messages to logging or console or both
        :param log: Send the messages to logging, enabled by default
        :param level: Set the logger level (D=DEBUG, I=INFO, W=WARNING, E=ERROR, C=CRITICAL)
        :param subject: Allows for a subject in the message
        :param msg1: First message
        :param msg2: Second message if we need it
        :return: None
        """

        # Function to ensure any type of msg is converted to string properly
        def to_string(msg):
            if isinstance(msg, str):
                return msg
            elif msg is None:
                return ''
            else:
                return str(msg)

        # Convert messages to string, safely handling non-string types
        msg1_str = to_string(msg1)
        msg2_str = to_string(msg2)

        # Combine messages
        entire_message = msg1_str
        if msg2_str:
            entire_message += " " + msg2_str

        # Prepend subject if it's provided
        if subject:
            entire_message = f"{subject}: {entire_message}"

        if log:
            if level == "D" and self.flask_app.config['DEBUG'] == 1:
                self.flask_app.logger.debug(entire_message)
            if level == "I":
                self.flask_app.logger.info(entire_message)
            if level == "W":
                self.flask_app.logger.warning(entire_message)
            if level == "E":
                self.flask_app.logger.error(entire_message)
            if level == "C":
                self.flask_app.logger.critical(entire_message)
