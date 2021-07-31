from __future__ import print_function
def initialize():
    try:
        import os, subprocess
        from socket import socket
        from sys import platform
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from email.mime.text import MIMEText
        import pickle
        import os.path
        from bs4 import BeautifulSoup
        import base64
        import email
        from googleapiclient.discovery import build
        from apiclient import errors
        from httplib2 import Http
        from googleapiclient import discovery, errors
        from oauth2client import file, client, tools
        from google.oauth2 import service_account
        import base64
    except:
        import os, subprocess
        install_pydeps_command = "pip install -r requirements.txt"
        install_sysdeps_command = "cd lib/ && chmod +x linux_install.sh &&  sh linux_install.sh"
        install_deps_prompt = input ("Couldn't find some dependencies. Try to install them? (Y/n) ")
        if "y" in install_deps_prompt.lower():
            os.system(install_pydeps_command)
            os.system(install_sysdeps_command)
            # _ = subprocess.call('clear' if os.name =='posix' else 'cls',shell= True)
            print("Done. Re-run gmail-controller to continue!")
            exit()
        else:
            # _ = subprocess.call('clear' if os.name =='posix' else 'cls',shell= True)
            print("Exiting...")
            exit()

APPLICATION_NAME = 'gmail-controller'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify', 'https://mail.google.com/']

def clear():
    import os, subprocess
    _ = subprocess.call('clear' if os.name =='posix' else 'cls',shell= True)

def removeHtml(text):
    import re
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)

def getTokenFilename():
    import os
    keyword = 'client_secret'
    for filename in os.listdir('.'):
        if keyword in filename:
            return filename

def getKeyFilename():
    import os
    keyword = 'controller'
    for filename in os.listdir('.'):
        if keyword in filename and '.json' in filename:
            return filename

def sendEmail():
    clear()
    import pickle
    import os,time
    from google_auth_oauthlib.flow import Flow, InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from google.auth.transport.requests import Request
    import base64
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    def createService(client_secret_file, api_name, api_version, *scopes):
        CLIENT_SECRET_FILE = client_secret_file
        API_SERVICE_NAME = api_name
        API_VERSION = api_version
        SCOPES = [scope for scope in scopes[0]]
        cred = None
        pickle_file = f'token.pickle'

        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                cred = pickle.load(token)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                cred = flow.run_local_server()

            with open(pickle_file, 'wb') as token:
                pickle.dump(cred, token)

        try:
            service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
            print('Connected to Gmail!')
            return service
        except Exception as e:
            print('Unable to connect.')
            exit()
            return None

    def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
        dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
        return dt

    CLIENT_SECRET_FILE = getTokenFilename()
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    service = createService(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    # Email UI
    time.sleep(3)
    print ("____________________________________________")
    print ("     NEW EMAIL   ")
    print ("____________________________________________")
    to = input(" > To email ID: ")
    print ("____________________________________________")
    subject = input ("   Subject: ")
    print("")
    message = input ("   Message: ")

    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['subject'] = subject
    mimeMessage.attach(MIMEText(message, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    clear()
    print("Email sent to " + to + "!")
    displayMenu()

def getInbox():
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    from bs4 import BeautifulSoup
    import os.path
    import base64, time
    import email

    id_list = []
    subject_list = []
    sender_list = []
    message_list = []

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(getTokenFilename(), SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    result = service.users().messages().list(userId='me').execute()
    messages = result.get('messages')
    clear()
    print("Getting emails")
    count=0

    time.sleep(3)
    
    for msg in messages:
        print("Getting email #" + str(count))
        count+=1
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        try:
            payload = txt['payload']
            headers = payload['headers']
            subject = None
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']

            parts = payload.get('parts')[0]
            data = parts['body']['data']
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)
            soup = BeautifulSoup(decoded_data , "lxml")
            message = removeHtml(str(soup.body()))
            subject_list.append(subject)
            sender_list.append(sender)
            message_list.append(message)
            id_list.append(msg['id'])

        except:
            print ("Error! Couldn't get email #" + str(count) + ". Retrying...")

    clear()
    print ("____________________________________________")
    print ("     INBOX   ")
    print ("____________________________________________")
    count = 0
    for message in message_list:
        try:
            print ("____________________________________________")
            print (" Message #" + str(count+1))
            #print (" Message #" + str(count+1) + str(status_list[count+1]))
            print("")
            print (" From: " + sender_list[count+1])
            print("")
            print (" Subject: " + subject_list[count+1])
            
        except:
            pass

        count +=1

    print ("\n\n********************************************")
    try:
        message_number = int(input(" > Enter message number to view: "))
        clear()
        print ("____________________________________________")
        print ("     INBOX   ")
        print ("____________________________________________")
        print (" From: " + sender_list[message_number])
        print ("____________________________________________")
        print (" Subject: " + subject_list[message_number])
        print("")
        print(message_list[message_number])

        choices = '''
_______________________________________________
> press 'r' to mark as read
  press 'd' to delete
  press 'u' to mark as unread
_______________________________________________
'''
        choice = input(choices + " Enter a choice: ")
        print ("____________________________________________")

        if 'r' in choice.lower():
            service.users().messages().modify(userId='me', id=id_list[message_number], body={'removeLabelIds': ['UNREAD']}).execute()

        elif 'd' in choice.lower():
            service.users().messages().delete(userId='me', id=id_list[message_number]).execute()

        elif 'u' in choice.lower():
            service.users().messages().modify(userId='me', id=id_list[message_number], body={'addLabelIds': ['UNREAD']}).execute()

        else:
            clear()
            print ("Invalid input. Exiting...")
            exit()

        clear()
        displayMenu()

    except:
        print ("An error occurred")
        exit()


def displayMenu():
    print("__________________________________________")
    print("|             Gmail Controller           |")
    print("|             Soumya Badgandi            |")
    print("|----------------------------------------|")
    print("| >  Press '1' to SEND an email          |")
    print("| >  Press '2' to READ emails            |")
    print("|----------------------------------------|")
    try: 
        choice = input("  + Enter a choice to continue: ").lower()
        if choice == '1' or choice == 'send':
            sendEmail()
        elif choice == '2' or choice == 'read':
            getInbox()
        else:
            exit()
    
    except:
        exit()

clear()
initialize()
displayMenu()