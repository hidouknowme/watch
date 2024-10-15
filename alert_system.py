import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def alert_with_attachments(video_filename, audio_filename):
    sender_email = "lalithaditya3429@gmail.com"
    receiver_email = "logsstealth@gmail.com"
    password = "hrva pjdb anpx mnay "

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Alert: Captured Video and Audio"

    # Attach the video file
    attach_file(msg, video_filename)
    # Attach the audio file
    attach_file(msg, audio_filename)

    try:
        # Set up the server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable security
            server.login(sender_email, password)  # Log in to your email account
            server.send_message(msg)  # Send the message
        print("Alert sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def attach_file(msg, filename):
    try:
        # Check if the file exists
        if os.path.exists(filename):
            with open(filename, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filename)}')
                msg.attach(part)
        else:
            print(f"File not found: {filename}")  # Log if file does not exist
    except Exception as e:
        print(f"Error attaching file {filename}: {e}")
