import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = 'ppaulv322@gmail.com'
sender_password = 'jkda zwhn yioo qpof'

receiver_email = 'ppaulv322@hotmail.com'
subject = 'Top 5 obras en Ica'
body = 'Adjunto lo solicitado'

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

with open('./data/top_5/ICA_top_obras.xlsx', 'rb') as file:
    attachment = MIMEApplication(file.read(), _subtype='xlsx')
    attachment.add_header('Content-Disposition', 'attachment', filename='ICA_top_obras.xlsx')
    msg.attach(attachment)

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print('Correo enviado exitosamente')