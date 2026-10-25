
from src.retrieval import Retriever
from src.answer import generate_answer

retriever = Retriever()

question = "Can I return an electronic product?"

chunks = retriever.search(question, top_k=4)
answer = generate_answer(question, chunks)

print("\nCUSTOMER QUESTION:", question)
print("\nAGENT ANSWER:", answer)
