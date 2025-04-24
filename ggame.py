import socket
import random

# Server setup
host = "127.0.0.1"  # IP Address for local testing
port = 7777  # Port number

banner = b"""
====GUESSING GAME====
Try to guess the number!
Enter your guess:"""

# Function to generate a random number based on difficulty level
def generate_random(difficulty):
    if difficulty == 1:
        return random.randint(1, 10)
    elif difficulty == 2:
        return random.randint(1, 50)
    return random.randint(1, 100)

# Function to get difficulty level with input validation
def get_difficulty(c):
    difficulty_prompt = """
    Difficulty
    ==========
    1) Easy
    2) Medium
    3) Hard
    Enter choice:"""
    while True:
        try:
            c.sendall(difficulty_prompt.encode())  # Send difficulty options
            data = c.recv(1024).decode().strip()  # Receive client's input
            difficulty = int(data)  # Convert input to integer
            if difficulty not in [1, 2, 3]:  # Validate input range
                raise ValueError("Invalid difficulty level.")
            return difficulty  # Return the validated difficulty level
        except ValueError:
            c.sendall(b"Invalid input! Please choose 1, 2, or 3.\n")  # Notify client of error

# Initialize the server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))  # Bind the socket to the host and port
s.listen(5)  # Listen for incoming connections (max backlog: 5)

print(f"Server is listening on {host}:{port}")

while True:
    conn = None
    guessme = 0
    attempts = 0  # Track the number of guesses for each session

    try:
        # Wait for a connection
        print("Waiting for connection...")
        conn, addr = s.accept()  # Accept a new client connection
        print(f"New client connected: {addr[0]}")
        
        # Difficulty selection and number generation
        difficulty = get_difficulty(conn)  # Get difficulty from client
        guessme = generate_random(difficulty)  # Generate random number
        conn.sendall(banner)  # Send game banner to the client

        while True:  # Start the guessing loop
            client_input = conn.recv(1024)  # Receive the client's guess
            try:
                guess = int(client_input.decode().strip())  # Convert input to integer
                attempts += 1  # Increment the attempts counter
                print(f"User guess: {guess}")

                if guess == guessme:  # Correct guess
                    conn.sendall(f"CORRECT! You guessed it in {attempts} attempts.\n".encode())
                    
                    # Offer replay option
                    conn.sendall(b"Would you like to play again? (yes/no): ")
                    replay = conn.recv(1024).decode().strip().lower()
                    
                    if replay == "yes":
                        # Reset for a new game
                        difficulty = get_difficulty(conn)  # Prompt for difficulty again
                        guessme = generate_random(difficulty)  # Generate new number
                        conn.sendall(banner)  # Send the game banner again
                        attempts = 0  # Reset attempts counter
                        continue
                    else:
                        conn.sendall(b"Thanks for playing! Goodbye.\n")
                        conn.close()  # Close connection after game
                        break

                elif guess > guessme:  # Guess is too high
                    conn.sendall(b"= Guess Lower\nTry again: ")
                else:  # Guess is too low
                    conn.sendall(b"= Guess Higher\nTry again: ")

            except ValueError:  # Handle non-numeric input
                conn.sendall(b"Invalid input! Please enter a valid number.\n")

    except ConnectionError:
        print("Connection lost.")
        if conn:
            conn.close()  # Close the connection if lost
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.close()  # Ensure connection is closed in case of errors
