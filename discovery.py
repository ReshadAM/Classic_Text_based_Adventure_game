# Assignment4 dec 6
# Reshad Mohsini
# Best version

# Discovery server stores and keeps track of all the servers that come and go #

import argparse
import signal
import socket
import sys
from urllib.parse import urlparse

# Saved information on the room.

# the port number and host name of the discovery server where all the rooms are mapped
DISCOVERY_PORT = 12000
DISCOVERY_HOST = 'localhost'

# The room's socket.

room_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# List of clients currently in the room.

server_list = []  # ( servername, port)


# Signal handler for graceful exiting.  We let clients know in the process so they can disconnect too.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)


# Search the server list for a particular server and return the server name if server found

def server_search(server):
    for reg in server_list:
        if reg[0] == server[0] or reg[1] == server[1]:
            return reg[0]
    return None


# Search the server list for a particular name and return the server name if server found

def server_search_by_name(server_name):
    for reg in server_list:
        if reg[0] == server_name:
            return reg[0]
    return None


# Search the server list for a particular name and return the server address if server is found

def get_server_address(server_name):
    for reg in server_list:
        if reg[0] == server_name:
            return reg[1]
    return None


# Add a server to the server list.

def server_add(server):
    server_list.append(server)


# Remove a server from server list.

def server_remove(server_name):
    for reg in server_list:
        if reg[0] == server_name:
            server_list.remove(reg)
            break


# Process incoming message.

def process_message(message, addr, room_socket):

    # Parse the message.

    words = message.split()

    # If a server wants to register with the discovery than register them if a server with the same name and port doesn't already exist

    if (words[0] == 'REGISTER'):
        if (len(words) == 3 and words[1].startswith("room://")):
            message = ''
            port = words[1]
            port = port[12:]
            server = (words[2], port)
            if server_search(server) == words[2]:
                error = "server name or address already exists!"
                message = "NOTOK" + " " + error
                room_socket.sendto(message.encode(), addr)
                return message
            # if the server is not already registered than register it
            elif server_search(server) is None:
                print(f'REGISTERING {words[2]} {port}')
                server_add(server)
                message = "OK"
                room_socket.sendto(message.encode(), addr)
                return message
            # in the off chance that something goes completely unexpected than let the client know
            else:
                message = "Something went wrong"
                print(message)
                return message
        return "Invalid command"

    # if a server disconnects, then deregister them from the discovery list

    elif (words[0] == 'DEREGISTER'):
        if (len(words) == 2):
            message = ''

            if (server_search_by_name(words[1]) == words[1]):
                server_remove(words[1])
                print(f'DEREGISTERING {words[1]}')
                message = "OK"
                room_socket.sendto(message.encode(), addr)
                return message
            else:
                error = "Server name not found in discovery"
                message = "NOTOK" + " " + error
                room_socket.sendto(message.encode(), addr)
                return message
        else:
            return "Invalid command"

    # if a client or a server calls lookup server, then provide them with the requested data
    elif (words[0] == 'LOOKUP'):
        if (len(words) == 2):
            message = ''
            print(f'LOOKING up  {words[1]}')
            if (server_search_by_name(words[1]) == words[1]):
                server_address = get_server_address(words[1])
                message = "OK" + " " + f'room://host:{server_address}'
                room_socket.sendto(message.encode(), addr)
                return message
            else:
                error = "Server name not found in discovery"
                message = "NOTOK" + " " + error
                room_socket.sendto(message.encode(), addr)
                return message
        else:
            return "Invalid command"

    else:
        return "Invalid command"


# Our main function.

def main():
    global room_socket

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Create the socket.  We will ask this to work on any interface and to use
    # the port given at the command line.  We'll print this out for clients to use.

    room_socket.bind((DISCOVERY_HOST, DISCOVERY_PORT))

    print(f'The discovery server will wait for servers at port: {DISCOVERY_PORT}')

    # Loop forever waiting for messages from clients.

    while True:
        # Receive a packet from a client and process it.

        message, addr = room_socket.recvfrom(1024)

        # Process the message and retrieve a response.

        response = process_message(message.decode(), addr, room_socket)

        # Send the response message back to the client.

        room_socket.sendto(response.encode(), addr)


if __name__ == '__main__':
    main()
