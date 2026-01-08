from google import genai
import os
from dotenv import load_dotenv

def test_genai():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("No API Key found")
        return

    client = genai.Client(api_key=api_key)
    
    models_to_try = [
        "gemini-2.5-flash",
        "models/gemini-2.5-flash",
        "gemini-2.0-flash-exp",
        "gemini-2.5-pro"
    ]

    for m in models_to_try:
        print(f"Attempting model: '{m}'")
        try:
            response = client.models.generate_content(
                model=m,
                contents='Hello, world!'
            )
            print(f"Success with {m}!")
            print(response.text)
            break
        except Exception as e:
            print(f"Failed {m}: {e}")

    print("\nAttempting to list models (if supported)...")
    try:
        # Note: list_models might be under client.models.list() or similar?
        pass # Skipping unless we know the API
    except Exception as e:
        print(f"List error: {e}")

if __name__ == "__main__":
    test_genai()
