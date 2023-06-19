import socket
import threading
import random
import string
import pymongo
import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
from email.message import EmailMessage
import ssl

HOST = ""
PORT = 9999


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["voting_system"]
votes_col = db["votes"]

parties = ["BJP", "Congress", "AAP", "JDS",
           "NOTA", "Others"]


def generate_otp(length=6):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def send_otp_email(email, otp):
    try:
        # define email message and credentials
        subject = "One-time Password for Voting System"
        body = f"Your one-time password (OTP) for voting is: {otp}"

        email_sender = '270203manoj@gmail.com'
        email_password = 'rjtqrxpfflnxtvgg'
        em = EmailMessage()
        # message = MIMEMultipart()
        # message = MIMEText(body)
        em['From'] = email_sender
        em['To'] = email
        em['Subject'] = subject
        em.set_content(body)
        # message.attach(MIMEText(body, 'plain'))

        # # send email
        # server = smtplib.SMTP('smtp.gmail.com', 465)
        # # server.starttls()
        # server.ssl()
        # server.login('270203manoj@gmail.com', 'Manoj@8618540070')
        # text = message.as_string()
        # server.sendmail('270203manoj@gmail.com', email, text)
        # server.quit()
        # Send email using SMTP server

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email, em.as_string())

        print(f"OTP sent to {email}")
    except Exception as e:
        print(f"Error sending OTP to {email}: {e}")


def handle_client(conn, addr):
    try:
        # send parties available for voting
        conn.send(",".join(parties).encode())
        # receive user ID and check if email is already registered
        user_id = conn.recv(1024).decode().strip()
        email = conn.recv(1024).decode().strip()
        if votes_col.count_documents({"email": email}) > 0:
            # email is already registered, send list of parties
            # conn.send(",".join(votes_col).encode())
            conn.send("Registered and Voted".encode())
            print("manoj")
            print(f"User {user_id} connected from {addr}. Already registered.")
            conn.close()
            return
        else:
            conn.send("Please Vote".encode())

        otp = generate_otp()
        print(f"User {user_id} connected from {addr}. OTP: {otp}")
        send_otp_email(email, otp)

        # verify OTP
        client_otp = conn.recv(1024).decode().strip()
        if client_otp != otp:
            conn.send("OTP verification failed".encode())
            print(f"User {user_id} failed OTP verification")
            conn.close()
            return

        # OTP verified, send confirmation to client
        conn.send("OTP verified".encode())
        print(f"User {user_id} verified")

        # receive vote from client and store in database
        vote = conn.recv(1024).decode().strip()
        if vote not in parties:
            conn.send("Invalid party".encode())
            print(f"User {user_id} voted for an invalid party")
            conn.close()
            return
        else:
            votes_col.insert_one(
                {"user_id": user_id, "vote": vote, "email": email})
            conn.send("Vote counted".encode())
            print(f"User {user_id} voted for {vote}")
    except:
        print(f"Error handling request from {addr}")
    finally:
        conn.close()

        # determine winner and display result
        votes = [doc["vote"] for doc in votes_col.find()]
        if len(votes) == 0:
            print("No votes cast")
        else:
            vote_counts = [votes.count(party) for party in parties]
            max_count = max(vote_counts)
            if vote_counts.count(max_count) > 1:
                winners = [parties[i] for i in range(
                    len(parties)) if vote_counts[i] == max_count]
                print("Tie between: " + ", ".join(winners))
            else:
                winner = parties[vote_counts.index(max_count)]
                print(f"Winner: {winner}")


# create socket and start listening for connections
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s = ssl.wrap_socket(s, server_side=True,
                    keyfile="private-key.pem", certfile="public-cert.pem")

if __name__ == "__main__":
    s.bind((HOST, PORT))
    s.listen(0)

    print("Server started. Listening for connections...")

    # handle incoming connections with threads
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()
