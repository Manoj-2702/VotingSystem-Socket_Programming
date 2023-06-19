import socket
import ssl

HOST = "127.0.0.1"
PORT = 60002

# create socket and connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client = ssl.wrap_socket(
    client, keyfile="private-key.pem", certfile="public-cert.pem")

client.bind((HOST, PORT))
client.connect(("127.0.0.1", 60000))
# receive parties available for voting
parties = client.recv(1024).decode().split(",")
print("Parties available for voting:")
for i, party in enumerate(parties):
    print(f"{i+1}. {party}")

# receive user ID and email, and send to server
user_id = input("Enter your user ID: ")
email = input("Enter your email: ")
client.send(user_id.encode())
client.send(email.encode())

msg = client.recv(1024).decode()
if msg != "Registered and Voted":
    user_otp = input(f"Enter the OTP sent to {email}: ")
    client.send(user_otp.encode())
    otp_verification_result = client.recv(1024).decode().strip()

    if otp_verification_result == "OTP verified":
        # OTP verified, prompt user to vote
        while True:
            print("Parties available for voting:")
            for i, party in enumerate(parties):
                print(f"{i+1}. {party}")
            vote = input("Enter the party you want to vote for: ")
            if vote not in parties:
                print("Invalid party. Please select a valid party.")
            else:
                # send vote to server and receive result
                client.send(vote.encode())
                vote_result = client.recv(1024).decode().strip()
                print(vote_result)
                break
    else:
        # OTP verification failed
        print("OTP verification failed")
else:
    print("Registered Buddy!")
    client.close()
# email_verification_result = s.recv(1024).decode().strip()
# if email_verification_result == "Email Already there":
#     while True:
#         print("Email is already registered.\n So please get lost")
#         s.close()
#         exit()

# receive OTP and verify with user input
# otp = s.recv(1024).decode().strip()
# user_otp = input(f"Enter the OTP sent to {email}: ")
# s.send(user_otp.encode())
# otp_verification_result = s.recv(1024).decode().strip()

# if otp_verification_result == "OTP verified":
#     # OTP verified, prompt user to vote
#     while True:
#         vote = input("Enter the party you want to vote for: ")
#         if vote not in parties:
#             print("Invalid party. Please select a valid party.")
#         else:
#             # send vote to server and receive result
#             s.send(vote.encode())
#             vote_result = s.recv(1024).decode().strip()
#             print(vote_result)
#             break
# else:
#     # OTP verification failed
#     print("OTP verification failed")

# close connection to server
client.close()
