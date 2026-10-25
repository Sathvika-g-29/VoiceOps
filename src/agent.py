
from src.retrieval import Retriever
from src.answer import generate_answer
from src.support_tools import SupportSession


class VoiceOpsAgent:
    def __init__(self):
        self.retriever = Retriever()
        self.session = SupportSession()
        self.last_chunks = []

    def respond(self, message):
        text = message.lower()
        self.last_chunks = []

        # Continue a pending order verification.
        if self.session.pending_order_id:
            result = self.session.handle_order_request(message)

            if result["type"] == "order_found":
                order = result["order"]
                status = order.get("status", "not available")
                return (
                    f"Verification successful. Your order status is "
                    f"{status}. How else can I help?"
                )

            return result["message"]

        # Order requests require customer verification.
        if any(term in text for term in (
            "my order", "order status", "track my order",
            "where is my order", "my delivery"
        )):
            result = self.session.handle_order_request(message)
            return result["message"]

        # Retrieve chunks for general policy questions.
        self.last_chunks = self.retriever.search(message, top_k=4)
        return generate_answer(message, self.last_chunks)
