1..Install the library: Open your terminal/command prompt and run:

pip install langchain-openai


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

HUBSPOT_TOKEN = "pat-na2-9341de2e-85bc-46f1-bca3-3d8769740827"


GEMINI_KEY = "AIzaSyAe0wym1MS3E0kFR4iqOmTG6KI6qxEQB9w"
HUBSPOT_TOKEN = "pat-na2-9341de2e-85bc-46f1-bca3-3d8769740827"




import os
import time
from google import genai
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException

# --- CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyAMnvrl4v97iE7FHntiKcAO0hD6OUK2HwI" 
HUBSPOT_TOKEN = "pat-na2-9341de2e-85bc-46f1-bca3-3d8769740827" 

def send_to_hubspot(name, email, company, grade):
    """Pushes the collected data into HubSpot."""
    try:
        api_client = HubSpot(access_token=HUBSPOT_TOKEN)
        properties = {
            "firstname": name,
            "email": email,
            "company": company,
            "description": f"Enquiry for Steel Grade: {grade}"
        }
        object_input = SimplePublicObjectInput(properties=properties)
        # Using the standard keyword argument for the latest HubSpot SDK
        api_client.crm.contacts.basic_api.create(simple_public_object_input=object_input)
        return "SUCCESS: Lead captured in HubSpot CRM!"
    except Exception as e:
        return f"HubSpot Error: {str(e)}"

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



Steel AI Bot: Hello! Ready to assist with your steel requirements. How can I help?
You:  I am looking for structural steel
Bot: Great! "Structural steel" is a broad category, and we offer a wide range of grades suitable for various structural applications.

To help me recommend the best option for you, could you tell me a little more about your project or what you're looking for? For example:

*   What will the steel be used for (e.g., buildings, bridges, machinery frames, general fabrication)?
*   Are there any specific strength requirements?
*   Do you need it to be easily weldable, or does it need particular corrosion resistance?
*   Are you working to a specific standard (e.g., ASTM, EN, JIS)?

Once I have a better understanding of your needs, I can suggest suitable grades like A36, A572 Gr. 50, S235JR, S355JR, and many others.
You: ASTM A36
Bot: Excellent choice! ASTM A36 is one of the most common and versatile structural steel grades, known for its good strength, formability, and excellent weldability. It's widely used for general structural applications, buildings, bridges, and various fabricated components.

Are you looking for more information about A36, or would you like a quote for it?
You: yes
Bot: Could you please clarify? Are you looking for:

1.  More information about ASTM A36?
2.  A quote for ASTM A36?
You: 2
Bot: Great! I can certainly get a quote started for ASTM A36 for you.

To proceed, please provide me with the following information:

*   **Your Name:**
*   **Your Email:**
*   **Your Company:**
You: name:vidhyaa,email:vidhyaa@gmail.com,company:tekriq
Bot: One moment, I am saving your inquiry...
Bot: HubSpot API Error: {"status":"error","message":"Property values were not valid: [{\"isValid\":false,\"message\":\"Property \\\"description\\\" does not exist\",\"error\":\"PROPERTY_DOESNT_EXIST\",\"name\":\"description\",\"localizedErrorMessage\":\"Property \\\"description\\\" does not exist\",\"portalId\":244764782}]","correlationId":"ffbce914-a7be-4a80-a701-2e8bad686524","errors":[{"message":"Property \"description\" does not exist","code":"PROPERTY_DOESNT_EXIST","context":{"propertyName":["description"]}}],"category":"VALIDATION_ERROR"}
You: 
