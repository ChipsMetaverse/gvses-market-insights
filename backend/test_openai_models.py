import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment")
    exit(1)

print(f"Using API key: {api_key[:20]}...")

# Make request to OpenAI models endpoint
url = "https://api.openai.com/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal models: {len(data.get('data', []))}")
        print("\nAvailable models:")
        
        # Sort models by ID
        models = data.get('data', [])
        models_sorted = sorted(models, key=lambda x: x['id'])
        
        # Group by model family
        gpt4_models = []
        gpt3_models = []
        other_models = []
        
        for model in models_sorted:
            model_id = model['id']
            if 'gpt-4' in model_id:
                gpt4_models.append(model_id)
            elif 'gpt-3' in model_id:
                gpt3_models.append(model_id)
            else:
                other_models.append(model_id)
        
        if gpt4_models:
            print("\nGPT-4 Models:")
            for m in gpt4_models[:10]:  # Show first 10
                print(f"  - {m}")
        
        if gpt3_models:
            print("\nGPT-3.5 Models:")
            for m in gpt3_models[:10]:
                print(f"  - {m}")
        
        if other_models:
            print("\nOther Models:")
            for m in other_models[:20]:  # Show first 20
                print(f"  - {m}")
                
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error making request: {e}")
