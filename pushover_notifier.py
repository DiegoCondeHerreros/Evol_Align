from dotenv import load_dotenv
import os
import requests


class PushoverNotifier:
    """Simple wrapper around the Pushover API."""

    API_URL = "https://api.pushover.net/1/messages.json"

    def __init__(self, env_file="notification_api.env"):
        load_dotenv(env_file)

        self.user_key = os.getenv("PUSHOVER_USER_KEY")
        self.api_token = os.getenv("PUSHOVER_API_TOKEN")
        self.device = os.getenv("PUSHOVER_DEVICE") or None
        self.default_priority = int(os.getenv("PUSHOVER_PRIORITY", "0"))

        if not self.user_key:
            raise ValueError(
                "PUSHOVER_USER_KEY is missing from the .env file.")

        if not self.api_token:
            raise ValueError(
                "PUSHOVER_API_TOKEN is missing from the .env file.")

    def send(self, message, title="Notification", priority=None):
        """Send a standard notification."""

        payload = {
            "token": self.api_token,
            "user": self.user_key,
            "title": title,
            "message": message,
            "priority": self.default_priority if priority is None else priority,
        }

        if self.device:
            payload["device"] = self.device

        response = requests.post(self.API_URL, data=payload, timeout=15)
        response.raise_for_status()
        return response.json()

    def send_high_priority(self, message, title="High Priority"):
        """Send a high-priority notification."""
        return self.send(message, title, priority=1)

    def send_emergency(
        self,
        message,
        title="Emergency",
        retry=30,
        expire=600,
    ):
        """
        Send an emergency notification.

        retry  = Seconds between repeated alerts (minimum 30)
        expire = Stop retrying after this many seconds (maximum 10800)
        """

        payload = {
            "token": self.api_token,
            "user": self.user_key,
            "title": title,
            "message": message,
            "priority": 2,
            "retry": retry,
            "expire": expire,
        }

        if self.device:
            payload["device"] = self.device

        response = requests.post(self.API_URL, data=payload, timeout=15)
        response.raise_for_status()
        return response.json()
