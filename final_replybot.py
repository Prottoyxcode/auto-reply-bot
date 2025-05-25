import pyautogui
import time
import pyperclip
import requests
import subprocess
import platform

# --- Step 1: Select and Copy Text from UI ---
print("📋 Selecting chat text...")

pyautogui.click(1130, 1066)
time.sleep(0.5)

pyautogui.moveTo(480, 405)
time.sleep(0.2)
pyautogui.mouseDown()
pyautogui.dragTo(660, 930, duration=1.0)
pyautogui.mouseUp()
time.sleep(0.5)

pyautogui.hotkey('ctrl', 'c')
time.sleep(0.5)

pyautogui.moveTo(1200, 900)
pyautogui.click()
time.sleep(0.5)

pyautogui.moveTo(1180, 1050)
pyautogui.click()

# --- Step 2: Grab Clipboard Text ---
text_history = pyperclip.paste().strip()
if not text_history:
    raise RuntimeError("Clipboard is empty. Make sure the text is selected and copied correctly.")

def start_ollama():
    def is_ollama_ready():
        try:
            r = requests.get("http://localhost:11434")
            return r.status_code == 200
        except:
            return False

    if is_ollama_ready():
        print("🟢 Ollama is already running.")
        return

    print("🚀 Starting Ollama...")
    if platform.system() == "Windows":
        subprocess.Popen("start cmd /k ollama run llama3", shell=True)
    else:
        subprocess.Popen(["ollama", "run", "llama3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("⏳ Waiting for Ollama to be ready...")
    for _ in range(30):
        time.sleep(1)
        if is_ollama_ready():
            print("✅ Ollama is ready.")
            return

    raise RuntimeError("❌ Ollama failed to start within 30 seconds.")

start_ollama()

# --- Step 3: Style Mimic ---
def mimic_user_style(chat_history_text, retries=3, wait=5):
    lines = [line.strip() for line in chat_history_text.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        raise ValueError("Chat history needs at least two messages (style + prompt).")

    style_messages = "\n".join(lines[:-1])
    new_prompt = lines[-1]

    prompt = f"""
Analyze the user's writing style based on the following messages. Then reply to the final message using that style. Do not ask questions. Just give a confident, natural response.

User's style examples:
{style_messages}

New message to respond to:
{new_prompt}
"""

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False},
                timeout=60
            )
            data = response.json()

            if "response" in data:
                return data["response"].strip()
            elif "error" in data:
                print("❌ Ollama error:", data["error"])
                return "[ERROR: Model or prompt issue.]"
            else:
                print("❌ Unexpected response:", data)
                return "[ERROR: Unexpected JSON structure.]"

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection attempt {attempt} failed: {e}")
            if attempt < retries:
                print(f"⏳ Retrying in {wait} seconds...")
                time.sleep(wait)
            else:
                print("❌ All retry attempts failed.")
                raise SystemExit(e)

# --- Step 4: Run, Clean, Copy ---
if __name__ == "__main__":
    print("🤖 Mimic Bot: Responding based on clipboard chat...")
    result = mimic_user_style(text_history)

    # Remove common boilerplate lines and keep only actual user-style reply
    lines = [line.strip() for line in result.splitlines() if line.strip()]
    # Remove lines like "Here's the response...", etc.
    filtered = [
        line for line in lines
        if not any(
            line.lower().startswith(prefix)
            for prefix in ("here's", "response:", "in the same style", "sure thing", "okay", "done")
        )
    ]

    result = filtered[0] if filtered else result
    print("\n--- Bot Response ---\n")
    print(result)

    pyperclip.copy(result)
    print("\n✅ Response copied to clipboard.")

# --- Step 5: Paste into Chat ---
pyautogui.click(1130, 1066)
time.sleep(0.5)

pyautogui.click(790, 965)
time.sleep(0.2)

pyautogui.hotkey('ctrl', 'v')
time.sleep(0.2)

pyautogui.press('enter')

print("✅ Response pasted and sent.")
