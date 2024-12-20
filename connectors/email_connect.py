import os.path
import pprint
import base64
import json
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
USER_EMAIL = 'moonwakecuppings@gmail.com'
WHITELISTED_EMAILS = [
    'mingliwood@gmail.com'
]


class Gmail(object):
    creds = None
    def auth(self):
        current_file_path = os.path.abspath(__file__)
        current_folder = os.path.dirname(current_file_path)
        token_path = "{}/token.json".format(current_folder)
        creds_path = "{}/credentials.json".format(current_folder)

        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)

    def fetch_emails(self):
        self.auth()
        try:
            service = build("gmail", "v1", credentials=self.creds)
            results = service.users().messages().list(userId=USER_EMAIL, maxResults=100).execute()
            messages = results.get('messages', [])

            parsed_messages = []
            if messages:
                for message in reversed(messages): # read oldest messages first
                    email_whitelisted = False
                    parsed_message = {
                        'message-id': None,
                        'date-sent': None,
                        'from': None,
                        'subject': None,
                        'body': None
                    }
                    msg = service.users().messages().get(userId=USER_EMAIL, id=message['id']).execute()
                    payload = msg['payload']
                    headers = payload['headers']

                    subject = None
                    snippet = None
                    for header in headers:
                        if header['name'] == 'Subject':
                            parsed_message['subject'] = header['value']
                        elif header['name'] == 'Message-ID' or header['name'] == 'Message-Id':
                            parsed_message['message-id'] = header['value']
                        elif header['name'] == 'Date':
                            parsed_message['date-sent'] = header['value']
                        elif header['name'] == 'From':
                            email_pattern = r'<([^>]+)>'
                            match = re.search(email_pattern, header['value'])
                            if match:
                                email = match.group(1)  # Extract the email
                            else:
                                print("No email found.")
                            if email in WHITELISTED_EMAILS:
                                email_whitelisted = True
                            parsed_message['from'] = email
                        
                    body = ''
                    print("Email from: {} at: {} with subject: {}".format(
                        parsed_message['from'],
                        parsed_message['date-sent'],
                        parsed_message['subject']))
                    if 'parts' in payload:
                        parts = payload['parts']
                        for part in parts:
                            if part['mimeType'] == 'text/plain':  # Get plain text part
                                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                break
                    elif 'body' in payload:
                        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                    parsed_message['body'] = body
                    if email_whitelisted:
                        parsed_messages.append(parsed_message)
                return parsed_messages
            else:
                print('No emails found.')
                return

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

        
if __name__ == "__main__":
  gmail = Gmail()
  msgs = gmail.fetch_emails()
  pprint.pprint(msgs)