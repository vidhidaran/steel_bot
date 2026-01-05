import os
import time
from google import genai
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException

# --- CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyAe0wym1MS3E0kFR4iqOmTG6KI6qxEQB9w" # Your key
HUBSPOT_TOKEN = "pat-na2-9341de2e-85bc-46f1-bca3-3d8769740827" # Your HubSpot token

def send_to_hubspot(name, email, company, grade):
    """Sends lead info to HubSpot CRM."""
    try:
        api_client = HubSpot(access_token=HUBSPOT_TOKEN)
        properties = {
            "firstname": name,
            "email": email,
            "company": company,
            "description": f"Interested in Steel Grade: {grade}"
        }
        simple_public_object_input = SimplePublicObjectInput(properties=properties)
        api_client.crm.contacts.basic_api.create(simple_public_object_input=simple_public_object_input)
        return "SUCCESS"
    except Exception as e:
        return str(e)

def run_steel_bot():
    # Initialize the client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    system_instruction = """
    You are a Sales Expert for a Steel company.
    GOAL: Collect Name, Email, Company Name, and Steel Grade.
    RULES:
    1. If the user provides info, remember it.
    2. Once you have Name, Email, Company, and Grade, you MUST output this line:
    INITIATING_HUB_SYNC|Name|Email|Company|Grade
    3. Be professional and helpful.
    """

    # Using gemini-2.0-flash because gemini-1.5-flash was not found for this key
    try:
        chat = client.chats.create(
            model="gemini-2.0-flash", 
            config={'system_instruction': system_instruction}
        )
    except Exception as e:
        print(f"Failed to start chat: {e}")
        return

    print("Steel AI Bot: Hello! How can I help you today?")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']: break
            
        retry_count = 0
        max_retries = 5
        base_delay = 2
        
        while retry_count <= max_retries:
            try:
                response = chat.send_message(user_input)
                bot_text = response.text
                
                if "INITIATING_HUB_SYNC" in bot_text:
                    # Parse the sync line
                    sync_line = [line for line in bot_text.split('\n') if "INITIATING_HUB_SYNC" in line][0]
                    parts = sync_line.split("|")
                    
                    print("Bot: Processing your request...")
                    status = send_to_hubspot(parts[1], parts[2], parts[3], parts[4])
                    
                    if status == "SUCCESS":
                        print("Bot: Success! I've sent your request to our sales team.")
                    else:
                        print(f"Bot: Sync Error: {status}")
                else:
                    print(f"Bot: {bot_text}")
                break # Success, exit retry loop
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    retry_count += 1
                    if retry_count > max_retries:
                        print("Bot Error: Rate limit persistent. Please try again in 1 minute.")
                        break
                    
                    delay = base_delay * (2 ** (retry_count - 1))
                    print(f"Bot Error: Rate limit reached. Retrying in {delay} seconds (Attempt {retry_count}/{max_retries})...")
                    time.sleep(delay)
                else:
                    print(f"Bot Error: {e}")
                    break

if __name__ == "__main__":
    run_steel_bot()
