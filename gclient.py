import socket

host = "127.0.0.1"  # Server IP Address
port = 7777  # Server Port

# Set up the client socket
s = socket.socket()
s.connect((host, port))

# Game loop
while True:
    data = s.recv(1024)  # Receive server message
    print(data.decode().strip())
    
    # Check if the server says goodbye, then exit
    if "Goodbye" in data.decode():
        break

    # Send user input to the server
    user_input = input().strip()
    s.sendall(user_input.encode())

# Close the socket when done
s.close()
