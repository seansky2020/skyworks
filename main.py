import os
from dotenv import load_dotenv

from groq import Groq
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import threading
import time

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Groq API setup using environment variable
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Google Sheets setup using environment variable
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
SPREADSHEET_ID = '1TzEMCPgvZnVs05ERyakO37BsAiOjomIvHeSdPZoczOc'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=creds)

# Simulated knowledgebase
knowledgebase = {
    "trading platforms": "We offer MetaTrader 4 and MetaTrader 5.",
    "leverage ratios": "We provide leverage up to 1:500 for professional clients.",
    "open account": "You can open an account through our website by clicking on 'Open Account' and following the steps."
}

messages = []
last_activity_time = time.time()
conversation_ended = False

def get_ai_response(messages):
    completion = groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    return completion.choices[0].message.content

def record_to_sheet(date, time, agent_name, transcript, assessment):
    sheet = sheets_service.spreadsheets()
    values = [[date, time, agent_name, transcript, assessment]]
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID, range='Sheet1',
        valueInputOption='USER_ENTERED', body=body).execute()

def check_timeout():
    global conversation_ended
    while not conversation_ended:
        if time.time() - last_activity_time > 600:  # 10 minutes
            end_conversation("Timeout")
            break
        time.sleep(10)  # Check every 10 seconds

def end_conversation(reason):
    global conversation_ended
    if not conversation_ended:
        conversation_ended = True
        transcript = "\n".join([f"{m['role']}: {m['content']}" for m in messages[1:]])
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        record_to_sheet(date, time_str, "AI Agent", transcript, f"Conversation ended due to {reason}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global last_activity_time, messages
    last_activity_time = time.time()
    
    if not messages:
        system_message = """You are a potential customer interacting with RCG Markets' forex brokerage customer service. Your task is to test their knowledge and service quality using provided FAQs.

        Instructions:
        1. Use natural, conversational language
        2. Alternate between novice and experienced trader personas
        3. Ask follow-up questions based on responses
        4. Note any incorrect/incomplete information
        5. End conversations politely

        Begin the conversation when ready. Respond as the customer, awaiting the support agent's (user's) replies."""
        messages.append({"role": "system", "content": system_message})

    user_message = request.json['message']
    messages.append({"role": "user", "content": user_message})
    
    ai_response = get_ai_response(messages)
    messages.append({"role": "assistant", "content": ai_response})
    
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    timeout_thread = threading.Thread(target=check_timeout)
    timeout_thread.start()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))