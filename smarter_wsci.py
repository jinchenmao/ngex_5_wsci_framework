from pathlib import Path
from ollama import chat
import json


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## ---------- Initialize the state artifact ----------
state = {
    "problem": question,
    "wi_fi_status": "operational",
    "wi-fi_check": True
}

with open("state.json", "w") as file:
    json.dump(state, file, indent=2)

with open("state.json", "r") as file:
    state = json.load(file)

print(state)


## ---------- Automatically select relevant files ----------
def select_context(question):
    """
    Pick relevant files from knowledge/ based on keywords in the question.
    Returns a list of file paths.
    """
    question_lower = question.lower()

    keyword_map = {
        "printer": "knowledge/printing.txt",
        "print": "knowledge/printing.txt",
        "printing": "knowledge/printing.txt",
        "wifi": "knowledge/wifi_setup.txt",
        "wi-fi": "knowledge/wifi_setup.txt",
        "wireless": "knowledge/wifi_setup.txt",
        "password": "knowledge/password_changes.txt",
        "passwd": "knowledge/password_changes.txt",
        "email": "knowledge/email_setup.txt",
        "mail": "knowledge/email_setup.txt",
        "vpn": "knowledge/vpn.txt",
        "projector": "knowledge/classroom_projectors.txt",
        "projectors": "knowledge/classroom_projectors.txt",
        "classroom": "knowledge/classroom_projectors.txt",
        "service": "knowledge/service_status.txt",
        "status": "knowledge/service_status.txt",
        "outage": "knowledge/service_status.txt",
    }

    selected = set()
    for keyword, filepath in keyword_map.items():
        if keyword in question_lower:
            selected.add(filepath)

    # Always include service status as a troubleshooting baseline
    selected.add("knowledge/service_status.txt")

    return sorted(selected)


selected_files = select_context(question)
print("Selected files:", selected_files)


## ---------- Read the selected files ----------
context = ""

for filepath in selected_files:
    path = Path(filepath)
    if path.exists():
        context += f"\n--- {path.name} ---\n"
        context += path.read_text()
        context += "\n"


## ---------- Compress the context ----------
def compress_context(context, question):
    """
    Use Qwen to extract only the parts of the context
    relevant to the student's question.
    """
    prompt = f"""You are a helpful assistant that compresses technical documentation.

Given the following context and a student's question, extract ONLY the sentences and facts
from the context that are relevant to answering the question. Remove all irrelevant information.
Be concise but complete - keep all information that could help answer the question.

Question:
{question}

Context:
{context}

Return only the compressed context. Do not add commentary or explanations."""

    response = chat(
        model="qwen2.5:7b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.message.content


compressed_context = compress_context(context, question)

print("Compressed context characters:", len(compressed_context))


## ---------- Produce a structured answer using compressed context + relevant state ----------
response = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a university IT helpdesk assistant. "
                "Answer the student's question using ONLY the provided context. "
                "If the context does not contain enough information, say so. "
                "Respond with a JSON object with these fields: "
                '"diagnosis" (string), "steps" (list of strings), '
                '"escalate" (boolean), and "notes" (string).'
            )
        },
        {
            "role": "user",
            "content": (
                f"Student question:\n{question}\n\n"
                f"Relevant context:\n{compressed_context}\n\n"
                f"Current state (only use relevant parts):\n"
                f"- Wi-Fi service status: {state.get('wi_fi_status', 'unknown')}\n"
                f"- Wi-Fi check passed: {state.get('wi-fi_check', False)}\n"
            )
        }
    ],
    format="json",                      # structured output
    options={"temperature": 0.1}
)

print(response.message.content)


## ---------- Write the answer back into the state artifact ----------
try:
    llm_output = json.loads(response.message.content)
except json.JSONDecodeError:
    llm_output = {"raw_response": response.message.content}

state["llm_response"] = llm_output

with open("state.json", "w") as file:
    json.dump(state, file, indent=2)

print("State artifact updated:", state)