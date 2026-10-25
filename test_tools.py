
from src.support_tools import SupportSession

session = SupportSession()

result = session.escalate(
    summary=(
        "Customer reports a delayed order. Order status was not verified. "
        "Escalation requested for manual review."
    ),
    order_id="100001",
    reason="Delayed order requires manual review",
    intent="order_status",
)

print(result)
