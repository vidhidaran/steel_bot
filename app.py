import os
import time
from google import genai
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException

# --- CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyAMnvrl4v97iE7FHntiKcAO0hD6OUK2HwI" 
HUBSPOT_TOKEN = "pat-na2-651a972b-8653-40f6-961e-6b2233058fa9" 

def send_to_hubspot(name, email, company, grade):
    """Sends lead to HubSpot using the exact argument the SDK is asking for."""
    try:
        # Re-initialize client inside function to ensure it's fresh
        api_client = HubSpot(access_token=HUBSPOT_TOKEN)
        
        properties = {
            "firstname": name,
            "email": email,
            "company": company,
            "description": f"Enquiry for Steel Grade: {grade}"
        }
        
        # Create the input object
        object_input = SimplePublicObjectInput(properties=properties)
        
        # FIX: We use the EXACT keyword from your error message
        api_client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=object_input
        )
        return "SUCCESS: Lead captured in HubSpot!"
        
    except ApiException as e:
        # This will tell us if there is a problem with the email (e.g. already exists)
        return f"HubSpot API Error: {e.body}"
    except Exception as e:
        return f"Technical Error: {str(e)}"
def run_steel_bot():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # IMPROVED SYSTEM PROMPT: Forces the AI to stay organized
    system_instruction = """
    You are a Sales Manager for a Steel company. 
    1. Help customers with their steel grade questions.
    2. If they want a quote, you MUST collect: Name, Email, Company, and Grade.
    3. IMPORTANT: Once you have all 4 pieces of info, you must end your response 
       with this EXACT format on a new line:
       SYNC_DATA|Name|Email|Company|Grade
    """

    try:
        # Using 1.5-flash for higher free-tier limits
        chat = client.chats.create(
            model="gemini-2.5-flash", 
            config={'system_instruction': system_instruction}
        )
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    print("Steel AI Bot: Hello! Ready to assist with your steel requirements. How can I help?")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']: break
            
        try:
            response = chat.send_message(user_input)
            bot_text = response.text
            
            # This looks for the secret sync command in the bot's response
            if "SYNC_DATA|" in bot_text:
                # Extract the data parts
                parts = bot_text.split("SYNC_DATA|")[-1].strip().split("|")
                
                # Check if we have all parts (Name, Email, Company, Grade)
                if len(parts) >= 4:
                    print("Bot: One moment, I am saving your inquiry...")
                    status = send_to_hubspot(parts[0], parts[1], parts[2], parts[3])
                    print(f"Bot: {status}")
                else:
                    # If the AI messed up the format, show the text anyway
                    print(f"Bot: {bot_text}")
            else:
                print(f"Bot: {bot_text}")
                
        except Exception as e:
            if "429" in str(e):
                print("Bot: Rate limit reached. Waiting 30 seconds...")
                time.sleep(30)
            else:
                print(f"Bot Error: {e}")

if __name__ == "__main__":
    run_steel_bot()
