
from src.agent import VoiceOpsAgent

agent = VoiceOpsAgent()

questions = [
    "Can I return an electronic product?",
    "Where is my order 100001?",
]

for question in questions:
    print("\nCustomer:", question)
    print("Agent:", agent.respond(question))
