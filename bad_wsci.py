from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""


context = ""

# Read every .txt file in knowledge/ — this is the "bad" approach
for file in Path("knowledge").glob("*.txt"):
    context += file.read_text()
    context += "\n\n"

# Ask Qwen
response = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "user",
            "content": (
                f"Student question:\n{question}\n\n"
                f"Context:\n{context}"
            )
        }
    ]
)

# See how large the context is
print("Context characters:", len(context))

# Print the answer
print(response.message.content)