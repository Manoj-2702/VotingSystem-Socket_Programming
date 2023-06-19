import socket
import threading
import random
import pymongo
from pymongo import MongoClient

# initialize MongoDB client and database
client = MongoClient('mongodb://localhost:27017/')
db = client['voting_system']
votes = db.votes

# define parties available for voting
parties = ['Party A', 'Party B', 'Party C']

# function to handle client connections


def handle_client(conn, addr):
    print(f"New connection from {addr}")

    # send parties available for voting to client
    conn.send(f"Parties: {', '.join(parties)}\n".encode())

    # get user ID from client
    user_id = conn.recv(1024).decode().strip()

    # generate OTP and send to client
    otp = str(random.randint(100000, 999999))
    conn.send(f"OTP: {otp}\n".encode())

    # get OTP from client and verify
    client_otp = conn.recv(1024).decode().strip()
    if client_otp != otp:
        conn.send("OTP verification failed\n".encode())
        conn.close()
        return

    # check if user has already voted
    if votes.find_one({'user_id': user_id}):
        conn.send("You have already voted\n".encode())
        conn.close()
        return

    # get vote from client and store in database
    vote = conn.recv(1024).decode().strip()
    if vote not in parties:
        conn.send("Invalid party\n".encode())
        conn.close()
        return

    votes.insert_one({'user_id': user_id, 'vote': vote})
    conn.send("Vote recorded\n".encode())
    conn.close()

# function to start server


def start_server():
    # create socket and bind to port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 1234))
    s.listen(5)

    print("Server started")

    # listen for incoming connections
    while True:
        conn, addr = s.accept()
        # handle each client in a separate thread
        threading.Thread(target=handle_client, args=(conn, addr)).start()

# function to calculate winner


def calculate_winner():
    # get total votes for each party from database
    party_votes = {party: votes.count_documents(
        {'vote': party}) for party in parties}

    # find party with highest vote count
    winner = max(party_votes, key=party_votes.get)

    print(f"Winner: {winner} ({party_votes[winner]} votes)")


if __name__ == '__main__':
    # start server in separate thread
    threading.Thread(target=start_server).start()

    # wait for some time for clients to connect and vote
    input("Press Enter to calculate winner...\n")

    # calculate and announce winner
    calculate_winner()
