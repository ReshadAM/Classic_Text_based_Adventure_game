# Assignment4 dec 6
# Reshad Mohsini
# Best version


import socket
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors

# the port number and host name of the discovery server where all the rooms are mapped

DISCOVERY_PORT = 12000
DISCOVERY_HOST = 'localhost'

# tuple that contains the address info for discovery server
discovery_server = (DISCOVERY_HOST, DISCOVERY_PORT)

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address.

server = ('', '')

# User name for tagging sent messages.

name = ''

# server host

host = 'localhost'
server_name = ''

# Inventory of items.

inventory = []

# Directions that are possible.

connections = {
    "north": "",
    "south": "",
    "east": "",
    "west": "",
    "up": "",
    "down": ""
}

TIME_OUT_CONSTANT = 5


# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message = 'exit'
    client_socket.sendto(message.encode(), server)
    for item in inventory:
        message = f'drop {item}'
        client_socket.sendto(message.encode(), server)
    sys.exit(0)


# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)


# Function to join a room.


def join_room():
    message = f'join {name}'
    client_socket.settimeout(5)
    client_socket.sendto(message.encode(), server)
    try:
        response, addr = client_socket.recvfrom(1024)
    except OSError as msg:
        print('Something bad happened')
        sys.exit()
    # print(f'{response.decode()}')


# Function to handle commands from the user, checking them over and sending to the server as needed.

def process_command(command):
    global server

    # Parse command.

    words = command.split()

    # Check if we are dropping something.  Only let server know if it is in our inventory.

    if (words[0] == 'drop'):
        if (len(words) != 2):
            print("Invalid command")
            return
        elif (words[1] not in inventory):
            print(f'You are not holding {words[1]}')
            return

    # Send command to server, if it isn't a local only one.

    if (command != 'inventory'):
        message = f'{command}'
        client_socket.sendto(message.encode(), server)

    # Check for particular commands of interest from the user.

    # If we exit, we have to drop everything in our inventory into the room.

    if (command == 'exit'):
        for item in inventory:
            message = f'drop {item}'
            client_socket.sendto(message.encode(), server)
        sys.exit(0)

    # If we look, we will be getting the room description to display.

    elif (command == 'look'):
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())

    # If we inventory, we never really reached out to the room, so we just display what we have.

    elif (command == 'inventory'):
        print("You are holding:")
        if (len(inventory) == 0):
            print('  No items')
        else:
            for item in inventory:
                print(f'  {item}')

    # If we take an item, we let the server know and put it in our inventory, assuming we could take it.

    elif (words[0] == 'take'):
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())
        words = response.decode().split()
        if ((len(words) == 2) and (words[1] == 'taken')):
            inventory.append(words[0])

    # If we drop an item, we remove it from our inventory and give it back to the room.

    elif (words[0] == 'drop'):
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())
        inventory.remove(words[1])

    # If we're wanting to go in a direction, we check with the room and it will tell us if it's a valid
    # direction.  We can then join the new room as we know we've been dropped already from the other one.

    elif (words[0] in connections):
        response, addr = client_socket.recvfrom(1024)

        # if path does exist than update the port by calling look_up_server_name
        if (response.decode() != "NOPATH"):
            result = look_up_server_name(response.decode())
            if (result[0] == "OK"):
                port = result[1]
                server = (host, port)
                join_room()
            else:
                # this should not happen but if it does it handles it
                print(f'You cannot go {words[0]} from this room.')
        else:
            print(f'You cannot go {words[0]} from this room.')

    # The player wants to say something ... print the response.

    elif (words[0] == 'say'):
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())

    # Otherwise, it's an invalid command so we report it.

    else:
        response, addr = client_socket.recvfrom(1024)
        print(f'{response.decode()}')


# Function to handle incoming messages from room.  Also look for disconnect messages to shutdown.

def handle_message_from_server(sock, mask):
    response, addr = client_socket.recvfrom(1024)
    words = response.decode().split(' ')
    print()
    if len(words) == 1 and words[0] == 'disconnect':
        print('Disconnected from server ... exiting!')
        sys.exit(0)
    else:
        print(response.decode())
        do_prompt()


# Function to handle incoming messages from user.

def handle_keyboard_input(file, mask):
    line = sys.stdin.readline()[:-1]
    process_command(line)
    do_prompt()


# This function will connect client with the discovery server to look a server address by the name of the server

def look_up_server_name(room_name):
    global server
    # REGISTER room://host:port name
    message = f'LOOKUP {room_name}'
    # if the discovery server does not reply within 5 seconds, end the client, so it doesn't wait forever
    client_socket.settimeout(TIME_OUT_CONSTANT)
    client_socket.sendto(message.encode(), discovery_server)
    try:
        response, addr = client_socket.recvfrom(1024)

    except OSError as msg:
        print('Unable to connect to discovery server, shutting down')
        sys.exit()
    response = response.decode()
    words = response.split()
    # if the discovery server found the server and returned its porter than update port
    if (words[0] == "OK"):
        port = words[1]
        port = port[12:]
        port = int(port)
        reply = (words[0], port)
        return reply

    # if the discovery server did not find the server than end the clent
    elif (words[0] == "NOTOK"):
        print(f'{response[6:]}')  # we want to print everything except for the NOTOK
        print("Shutting down the server.")
        sys.exit()
        return None

    else:
        # this should not happen but if it does it handles the issue by ending the client
        print("something unexpected happened when looking for server name")
        print(f'{response}')
        print("Shutting down the server.")
        sys.exit()
        return None


# Our main function.

def main():
    global name
    global client_socket
    global server
    global server_name

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name for the player in the game")
    parser.add_argument("server", help="name of room player wants to spawn in")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    name = args.name

    server_name = args.server
    # connect to the server by first getting its port using the look_up_server_name
    result = look_up_server_name(server_name)

    # if the output of the look_up_server_name is anything but okay then end the client
    if (result[0] == "OK"):
        port = result[1]
        server = (host, port)
        join_room()
    else:
        # this should not happen but if it does it handles the issue by ending the client

        print("Something unexpected happened,shutting down the server.")
        sys.exit()

    # Set up our selector.

    sel.register(client_socket, selectors.EVENT_READ, handle_message_from_server)
    sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)

    # Prompt the user before beginning.

    do_prompt()

    # Now do the selection.

    while (True):
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


if __name__ == '__main__':
    main()
