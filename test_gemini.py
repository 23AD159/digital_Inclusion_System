import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment
load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY')

print(f"Testing API Key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    response = model.generate_content("Hello! Are you ready to be a mentor for DigiGuide?")
    print("\nGemini Response:")
    print(response.text)
    print("\nSUCCESS: API is responsive.")
except Exception as e:
    print(f"\nFAILURE: {str(e)}")
