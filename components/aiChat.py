import os
import json
from datetime import datetime
import time

from dotenv import load_dotenv
from openai import OpenAI
import prompt
from components.util import extract_emotion

from tts import stream_tts
from util import clean_for_tts, split_text

# Load environment variables
load_dotenv()

# Initialize client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_LLM_API_KEY")
)

CHAT_FILE = "chat.json"
MAX_HISTORY = 200


def load_chat():
    if not os.path.exists(CHAT_FILE):
        return []
    try:
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_chat(messages):
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f, indent=2)


def clear_chat():
    if os.path.exists(CHAT_FILE):
        os.remove(CHAT_FILE)
    print("🧹 Chat cleared!")


def ensure_system_prompt(messages):
    # Ensure system prompt is always first
    SYSTEM_PROMPT = {
        "role": "system",
        "content": prompt.SYSTEM_PROMPT
    }
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, SYSTEM_PROMPT)


def chat_with_ai(messages):
    ensure_system_prompt(messages)

    user_input = input("You: ").strip()

    # Commands
    if user_input.lower() == "/exit":
        print("👋 Exiting...")
        exit()

    if user_input.lower() == "/clear":
        clear_chat()
        messages.clear()
        return

    if not user_input:
        return

    messages.append({
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Limit history but KEEP system prompt
    system = messages[0]
    history = messages[1:]
    history = history[-MAX_HISTORY:]
    messages[:] = [system] + history

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.6,
        top_p=0.95,
        max_tokens=2048,
        stream=True
    )

    full_response = ""

    print("AI: ", end="", flush=True)

    tts_buffer = ""

    for chunk in completion:
        choices = getattr(chunk, "choices", None)
        if not choices:
            continue

        delta = getattr(choices[0], "delta", None)
        if not delta:
            continue

        content = getattr(delta, "content", None)
        if content:
            print(content, end="", flush=True)
            full_response += content

            tts_buffer += content
    emotion, cleaned = extract_emotion(tts_buffer)
    clean_text = clean_for_tts(cleaned)
    if clean_text and clean_text.strip() and any(c.isalnum() for c in clean_text):
        chunks = split_text(clean_text)

        for chunk in chunks:
            stream_tts(chunk, emotion)
            time.sleep(0.4)  # avoid rate limit

    print()

    messages.append({
        "role": "assistant",
        "content": full_response,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_chat(messages)


if __name__ == "__main__":
    print("💬 AI Chat (type /exit to quit, /clear to reset)\n")

    messages = load_chat()

    while True:
        chat_with_ai(messages)