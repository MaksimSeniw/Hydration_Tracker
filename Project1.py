import time
import email
import imaplib
from email.header import decode_header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl

PASSWORD = 'oxvpftwlkwvejaud'
EMAIL = 'seniwprogramming@gmail.com'
RECIPIENT = input("What Email Address Would You Like to Use?\n")
SERVER = 'imap.gmail.com'
WATER = input("What is Your Hydration Goal?\n")
TIME = input("How Often Would You Like to be Emailed?(How many min. between each notifcation)\n")
X = 1

def email_alert():
    ctx = ssl.create_default_context()
    message = MIMEMultipart("mixed")
    message["Subject"] = "Hydration"
    message["From"] = EMAIL
    message["To"] = RECIPIENT
    message.attach(MIMEText("How much water do you think you've drank today? (In fluid ounces) Reply STOP to end emails.", "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, RECIPIENT, message.as_string())

def read_email_and_respond():
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')
    status, data = mail.search(None, 'ALL')
    mail_ids = []
    mail_content = ''
    for block in data:
        mail_ids += block.split()
    for i in mail_ids:
        status, data = mail.fetch(i, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])
                mail_from = message['from']
                mail_subject = message['subject']
                if message.is_multipart():
                    mail_content = ''
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    mail_content = message.get_payload()
                #print(f'From: {mail_from}')
                #print(f'Subject: {mail_subject}')
                #print(f'Content: {mail_content}')
    ounces_drank = [int(s) for s in mail_content.split() if s.isdigit()]
    ounces_drank.remove(2023)#For some reason have to to remove the current year from an incoming email to read the actual sent number.
    ounces_drank = [str(integer) for integer in ounces_drank]
    ounces_drank = "".join(ounces_drank)
    
    # if ("STOP" in ounces_drank):
    #     message.attach(MIMEText("EMAILS ENDED", "plain"))
    #     X = 0
    #     with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
    #         server.login(EMAIL, PASSWORD)
    #         server.sendmail(EMAIL, RECIPIENT, message.as_string())
    #     exit()

    ounces_drank = int(ounces_drank)
    #print(ounces_drank)
    ctx = ssl.create_default_context()
    message = MIMEMultipart("mixed")
    message["Subject"] = "Hydration"
    message["From"] = EMAIL
    message["To"] = RECIPIENT
    if (ounces_drank > 0 and ounces_drank < int(WATER)):
        message.attach(MIMEText("You have drank " + str(ounces_drank) + " ounces. You should drink " + str(int(WATER) - ounces_drank) + " more to hit recommended targets. Reply STOP to end emails.", "plain"))
        X = 1
    elif (ounces_drank >= int(WATER)):
        message.attach(MIMEText("You have hit recommended targets on how much you should drink per day! Reply STOP to end emails.", "plain"))
        X = 0
    elif (ounces_drank < 0):
        message.attach(MIMEText("Did someone steal your water? Please enter an actual number. Reply STOP to end emails.", "plain"))
        X = 1
    with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, RECIPIENT, message.as_string())

def delete_email():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL, PASSWORD)
    imap.select("INBOX")
    status, messages = imap.search(None, 'SUBJECT "Hydration"')
    messages = messages[0].split(b' ')
    for mail in messages:
        _, msg = imap.fetch(mail, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                print("Deleting", subject)
        imap.store(mail, "+FLAGS", "\\Deleted")
    imap.expunge()
    imap.close()
    imap.logout()

if (X == 1):
    while(True):
        email_alert()
        time.sleep(int(TIME)*60) #Time between each email 
        read_email_and_respond()
        delete_email()
        time.sleep(int(TIME)*60)
elif (X == 0):
    time.sleep(int(TIME)*60)
    X = 1