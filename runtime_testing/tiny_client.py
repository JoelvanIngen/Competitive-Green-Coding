"""
Simple client to test server with
"""

import socket
import struct

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    user_input = input('> ')
    s.send(struct.pack('<I', len(user_input)) + user_input.encode())
    data = s.recv(1024)
    print(data.decode())
