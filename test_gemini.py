import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

MODELS = ["gemini-3.8-flash"]  # add another model name from AI Studio's list here as a backup

def ask(prompt):
    for model in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                return response.text
            except Exception as e:
                print(f"{model} attempt {attempt + 1} failed: {str(e)[:80]}")
                time.sleep(2 * (attempt + 1))
    return None

print(ask("Reply with exactly: ClearBrand test OK"))