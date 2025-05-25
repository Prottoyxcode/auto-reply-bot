import pyautogui
import time
import pyperclip
import requests
import subprocess
import platform


# --- Step 1: Select and Copy Text from UI ---
print("📋 Selecting chat text...")

# Click the chat app icon (adjust coords as needed)
pyautogui.click(1130, 1066)
time.sleep(0.5)

# Move to start of selection area
pyautogui.moveTo(480, 405)
time.sleep(0.2)

# Click and drag to select text
pyautogui.mouseDown()
pyautogui.dragTo(660, 930, duration=1.0)
pyautogui.mouseUp()
time.sleep(0.5)

# Copy selected text
pyautogui.hotkey('ctrl', 'c')
time.sleep(0.5)

# Optional: click away
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
    for _ in range(30):  # up to 30 seconds
        time.sleep(1)
        if is_ollama_ready():
            print("✅ Ollama is ready.")
            return

    raise RuntimeError("❌ Ollama failed to start within 30 seconds.")

start_ollama()

# --- Step 3: Analyze Style and Respond ---
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
                timeout=60  # longer timeout
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

# --- Step 4: Run and Display ---
if __name__ == "__main__":
    print("🤖 Mimic Bot: Responding based on clipboard chat...")
    result = mimic_user_style(text_history)

    # Strip unnecessary first line if present
    lines = result.splitlines()
    if lines and lines[0].lower().startswith("here's my response"):
        result = "\n".join(lines[1:]).strip()

    print("\n--- Bot Response ---\n")
    print(result)

    pyperclip.copy(result)
    print("\n✅ Response copied to clipboard.")


pyautogui.click(1130, 1066)
time.sleep(0.5)


# --- Step 5: Paste the Response ---
pyautogui.click(790,965)
time.sleep(0.2)

# Paste the response
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.2)

# Press Enter to send
pyautogui.press('enter')

print("✅ Response pasted and sent.")
