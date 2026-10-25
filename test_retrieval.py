
from src.retrieval import Retriever

retriever = Retriever()

results = retriever.search(
    "Can I return an electronic product and get a refund?",
    top_k=4,
)

for item in results:
    print("-" * 60)
    print("Source:", item["source"])
    print("Section:", item["section_id"])
    print("Score:", round(item["score"], 3))
    print(item["text"][:500])
