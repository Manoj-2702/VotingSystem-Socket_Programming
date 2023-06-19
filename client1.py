import socket

# create socket and connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 1234))

# receive parties available for voting from server
parties_str = s.recv(1024).decode().strip()
parties = parties_str.split(",")
print("Parties available for voting: ")
for i, party in enumerate(parties):
    print(f"{i+1}. {party}")

# get user ID from user
user_id = input("Enter your user ID: ")
s.send(user_id.encode())

# receive OTP from server and send back to verify
otp = input("Enter OTP received: ")
s.send(otp.encode())

# receive verification status from server
verification_status = s.recv(1024).decode().strip()
if verification_status != "OTP verified":
    print("OTP verification failed. Please try again.")
    s.close()
    exit()

# get vote from user
vote = input(
    "Enter your vote (enter the number of the party you wish to vote for): ")
try:
    vote_index = int(vote) - 1
    if vote_index < 0 or vote_index >= len(parties):
        raise ValueError()
    else:
        vote = parties[vote_index]
        s.send(vote.encode())
except ValueError:
    print("Invalid vote. Please try again.")
    s.close()
    exit()

# receive vote confirmation from server
vote_confirmation = s.recv(1024).decode().strip()
print(vote_confirmation)

# close connection
s.close()
