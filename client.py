import socket
import hashlib

HOST = '127.0.0.1'  # IP address of server
PORT = 8000  # Port number

# Define functions for two-factor authentication


def generate_response(challenge, password):
    # Combine challenge and password
    combo = challenge + password.encode('utf-8')
    # Hash the combination and return as hex digest
    return hashlib.sha256(combo).hexdigest()


# Create socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connect to server
    s.connect((HOST, PORT))

    # Receive challenge from server
    challenge = s.recv(1024)

    # Prompt user for password and generate response
    password = input('Enter password: ')
    response = generate_response(challenge, password)

    # Send response to server
    s.send(response.encode('utf-8'))

    # Receive authentication code sent to email
    message = s.recv(1024).decode('utf-8')
    print(message)

    # Prompt user for authentication code and send to server
    code = input('Enter authentication code: ')
    s.send(code.encode('utf-8'))

    # Receive result of second factor authentication
    message = s.recv(1024).decode('utf-8')
    print(message)

    # Get list of parties from server
    parties = s.recv(1024).decode('utf-8').split(',')
    print('Available parties:')
    for i, party in enumerate(parties):
        print(f'{i+1}. {party}')

    # Prompt user for votes
    vote_count = len(parties)
    votes = [0] * vote_count
    while True:
        vote_str = input(f'Enter vote (1-{vote_count}) or "done" to finish: ')
        if vote_str == 'done':
            break
        try:
            vote = int(vote_str) - 1
            if vote < 0 or vote >= vote_count:
                raise ValueError
            votes[vote] += 1
        except ValueError:
            print(f'Invalid vote "{vote_str}"')

    # Send votes to server
    vote_str = ','.join(map(str, votes))
    s.send(vote_str.encode('utf-8'))

    # Receive winner from server
    winner = s.recv(1024).decode('utf-8')
    print(f'The winner is {winner}!')
