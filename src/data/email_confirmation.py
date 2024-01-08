from email.message import EmailMessage
import smtplib
import ssl
import json

with open("/home/msnow/config.json", "r") as fp:
    secrets = json.load(fp)

ctx = ssl.create_default_context()
password = secrets["bgg_email"]["password"]  # Your app password goes here
sender = secrets["bgg_email"]["sender"]  # Your e-mail address
receiver = secrets["bgg_email"]["receiver"]  # Recipient's address


msg = EmailMessage()
msg.set_content("success")
# me == the sender's email address
# you == the recipient's email address
msg["Subject"] = "Kaggle update successful"
msg["From"] = sender
msg["To"] = receiver

with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
    server.login(sender, password)
    # server.sendmail(sender, receiver, msg)
    server.send_message(msg)
