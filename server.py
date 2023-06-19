import socket
import hashlib
import os
import threading
import smtplib
from email.mime.text import MIMEText

HOST = '127.0.0.1'  # IP address of server
PORT = 32007  # Port number

# Define functions for two-factor authentication


def generate_challenge():
    # Generate random string for challenge
    return os.urandom(32)


def generate_response(challenge, password):
    # Combine challenge and password
    combo = challenge + password.encode('utf-8')

    # Hash the combination and return as hex digest
    return hashlib.sha256(combo).hexdigest()

# Define a function to send email for second factor authentication


def send_email(to, subject, body):
    # Email details
    sender = 'pes1202102711@pesu.pes.edu'
    password = 'Manoj@2003'

    # Create MIME message
    message = MIMEText(body)
    message['From'] = sender
    message['To'] = to
    message['Subject'] = subject

    # Send email using SMTP server
    with smtplib.SMTP_SSL('smtp.example.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(message)

# Define a function to handle client connections


def handle_client(conn, addr):
    print(f'Client connected from {addr}')

    # Get email address for second factor authentication
    conn.send(b'Enter your email address: ')
    email = conn.recv(1024).decode('utf-8').strip()

    # Send challenge to client
    challenge = generate_challenge()
    conn.send(challenge)

    # Receive response from client
    response = conn.recv(1024).decode('utf-8')

    # Verify response
    expected_response = generate_response(challenge, 'secret_password')
    if response != expected_response:
        conn.send(b'Authentication failed')
        conn.close()
        return

    # Authentication successful, send email for second factor authentication
    subject = 'Voting System Authentication'
    body = 'Please enter this code to authenticate: ' + challenge.hex()
    send_email(email, subject, body)
    conn.send(b'Authentication code sent to email')

    # Receive second factor authentication code from client
    code = conn.recv(1024).decode('utf-8')
    if code != challenge.hex():
        conn.send(b'Authentication failed')
        conn.close()
        return

    # Second factor authentication successful
    conn.send(b'Second factor authentication successful')

    # Receive vote from client
    vote = conn.recv(1024).decode('utf-8')

    # Process vote (e.g. store in database)
    # ...

    # Send confirmation to client
    conn.send(b'Vote successfully submitted')

    conn.close()

# Define a function to start the server and listen for incoming connections


def start_server():
    # Create socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind socket to host and port
        s.bind((HOST, PORT))

        # Listen for incoming connections
        s.listen()
        print(f'Server listening on {HOST}:{PORT}')

        while True:
            # Accept incoming connection
            conn, addr = s.accept()

            # Handle client connection in separate thread
            threading.Thread(target=handle_client, args=(conn, addr)).start()


# Start the server
start_server()
