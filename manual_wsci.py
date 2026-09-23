from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

# Manually pick the files relevant to the question
selected_files = [
    "knowledge/password_changes.txt",
    "knowledge/wifi_setup.txt",
    "knowledge/service_status.txt",
]

context = ""

# Loop through the selected files and read them into context
for filepath in selected_files:
    path = Path(filepath)
    if path.exists():
        context += f"\n--- {path.name} ---\n"
        context += path.read_text()
        context += "\n"

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

print("Context characters:", len(context))
print(response.message.content)