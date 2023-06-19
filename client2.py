import socket

# create socket and connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5000))

# receive parties available for voting
parties = s.recv(1024).decode().split(",")
print("Parties available for voting:")
for i, party in enumerate(parties):
    print(f"{i+1}. {party}")

# receive user ID and email, and send to server
user_id = input("Enter your user ID: ")
email = input("Enter your email: ")
s.send(user_id.encode())
s.send(email.encode())

# email_verification_result = s.recv(1024).decode().strip()
# if email_verification_result == "Email Already there":
#     while True:
#         print("Email is already registered.\n So please get lost")
#         s.close()
#         exit()

# receive OTP and verify with user input
# otp = s.recv(1024).decode().strip()
user_otp = input(f"Enter the OTP sent to {email}: ")
s.send(user_otp.encode())
otp_verification_result = s.recv(1024).decode().strip()

if otp_verification_result == "OTP verified":
    # OTP verified, prompt user to vote
    while True:
        vote = input("Enter the party you want to vote for: ")
        if vote not in parties:
            print("Invalid party. Please select a valid party.")
        else:
            # send vote to server and receive result
            s.send(vote.encode())
            vote_result = s.recv(1024).decode().strip()
            print(vote_result)
            break
else:
    # OTP verification failed
    print("OTP verification failed")

# close connection to server
s.close()
