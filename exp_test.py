from chunking_experiment import ChunkingExperiment
from utils import rough_similarty
from rdflib import Graph
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import requests


def chunk_sim_test():
    c_1 = Graph()
    c_2 = Graph()
    c_1.parse(data="""
    @prefix : <http://edas#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    :AcceptedPaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :ActivePaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :MealMenu a owl:Class ;
        rdfs:subClassOf :Document .

    :PendingPaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Programme a owl:Class ;
        rdfs:subClassOf :Document .

    :PublishedPaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :RejectedPaper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Review a owl:Class ;
        rdfs:subClassOf :Document .

    :Slideset a owl:class ;
        rdfs:subClassOf :Document .

    :WithdrawnPaper a owl:class ;
        rdfs:subClassOf :Paper .

    :Document a owl:Class .

    :Paper a owl:Class ;
        rdfs:subClassOf :Document.
    """, format="turtle")
    c_2.parse(data="""
    @prefix : <http://ekaw#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    :Camera_Ready_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Conference_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Demo_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Industrial_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Poster_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Regular_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Submitted_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Workshop_Paper a owl:Class ;
        rdfs:subClassOf :Paper .

    :Document a owl:Class .

    :Paper a owl:Class;
        rdfs:subClassOf :Document .
    """, format="turtle")

    print(rough_similarty(
        c_1, c_2, SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"))["score"])


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


def noti_test():
    notifier = PushoverNotifier()
    notifier.send_high_priority(
        "This is a test"
    )


# chunk_sim_test()
noti_test()
