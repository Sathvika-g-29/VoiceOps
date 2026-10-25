
import re
from tools.tools import lookup_order, create_ticket


def extract_order_id(text):
    match = re.search(r"\b\d{6,}\b", text)
    return match.group(0) if match else None


class SupportSession:
    def __init__(self):
        self.pending_order_id = None
        self.verification_attempts = 0
        self.verified_order = None

    def handle_order_request(self, message):
        # First message: identify the order and request verification.
        if self.pending_order_id is None:
            order_id = extract_order_id(message)

            if not order_id:
                return {
                    "type": "clarification",
                    "message": "Please provide your order ID so I can help."
                }

            result = lookup_order(order_id)
            self.pending_order_id = order_id
            self.verification_attempts = 0

            return {
                "type": "verification_required",
                "message": (
                    "For security, please provide either the last 4 digits "
                    "of your registered phone number or your 6-digit "
                    "delivery pincode."
                )
            }

        # Do not allow more than one verification attempt.
        if self.verification_attempts >= 1:
            self.pending_order_id = None
            self.verified_order = None
            return {
                "type": "verification_failed",
                "message": (
                    "I couldn't verify your details. For your security, "
                    "please contact customer support for further assistance."
                )
            }

        digits = "".join(ch for ch in message if ch.isascii() and ch.isdigit())

        if len(digits) not in (4, 6):
            self.verification_attempts += 1
            return {
                "type": "verification_failed",
                "message": (
                    "Please provide either exactly 4 phone digits or "
                    "a 6-digit delivery pincode. This is your final attempt."
                )
            }

        self.verification_attempts += 1
        result = lookup_order(self.pending_order_id, digits)

        if result.get("verified") is True and result.get("found") is True:
            self.verified_order = result
            self.pending_order_id = None
            return {
                "type": "order_found",
                "order": result,
                "message": "Verification successful."
            }

        self.pending_order_id = None
        return {
            "type": "verification_failed",
            "message": (
                "I couldn't verify those details. Please contact customer "
                "support for further assistance."
            )
        }

    def escalate(self, summary, order_id=None, reason=None, intent=None):
        result = create_ticket(
            summary=summary,
            order_id=order_id,
            reason=reason,
            intent=intent,
        )

        if result.get("created") is True:
            return {
                "success": True,
                "message": f"Your support ticket has been created: {result['ticket_id']}"
            }

        return {
            "success": False,
            "message": "I couldn't create the support ticket. Please try again."
        }
