
from src.voice import process_audio

result = process_audio("outputs/customer.wav")

print("Transcript:", result["transcript"])
print("Agent reply:", result["reply"])
print("Reply audio:", result["reply_audio"])
