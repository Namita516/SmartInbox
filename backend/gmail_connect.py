import os
import base64
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/contacts.readonly',
    'https://www.googleapis.com/auth/gmail.readonly'
]
def connect_gmail():
    creds = None
    # Load existing tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no tokens, log in
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def main():
    service = connect_gmail()
    
    # 1. Fetch the list of the 5 most recent messages
    print("Fetching emails from Gmail...")
    result = service.users().messages().list(userId='me', maxResults=20).execute()
    messages = result.get('messages', [])

    if not messages:
        print("No emails found.")
        return

    for msg in messages:
        # 2. Get full email content
        full_msg = service.users().messages().get(userId='me', id=msg['id']).execute()
        
        payload = full_msg.get('payload', {})
        headers = payload.get('headers', [])

        # 3. Extract Subject and Sender
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")

        # 4. Extract and Decode the Body
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            data = payload.get('body', {}).get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        # 5. POST data to your Flask Backend
        try:
            email_payload = {
                "sender": sender,
                "subject": subject,
                "body": body
            }
            
            # Since everything is on YOUR laptop, we use 127.0.0.1
            response = requests.post("http://127.0.0.1:5000/process-gmail", json=email_payload)
            
            if response.status_code == 200:
                print(f"✅ Successfully sent: {subject[:30]}...")
            else:
                print(f"❌ Backend error for {subject[:30]}: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Connection Error: Is your Flask server running on port 5000? {e}")

if __name__ == "__main__":
    main()