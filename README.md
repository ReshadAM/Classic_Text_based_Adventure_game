# Dungeon Adventure Game – A Classic Revival

Welcome to **Dungeon Adventure**, a fun and simplified version of the classic text-based dungeon games like *Zork* from 1977! This was a project I worked on during my second year at Western University, where I set out to bring back the magic of these old-school adventure games. My goal was to create a simple client-server game, using Python, that captures the spirit of exploration and interaction in a single room.

## About the Project

Dungeon Adventure is a networked game that uses a **client-server model** where the game server represents a single room in the adventure, and the client is the player who explores it. Think of this like stepping into a mysterious room filled with items, where you can pick up, drop, and check what you’re carrying. The game may be simple for now, but it’s built to be extensible—who knows what future updates will bring?

### Features
- **Single Room Adventure**: You start in a single room where you can explore, take items, and drop them.
- **Text-Based Interaction**: Just like the classic *Zork*, all commands are entered as text. It’s simple but nostalgic!
- **Inventory Management**: Take and drop items as you explore the room, and check what you’re holding at any time.
- **Exit the Room**: When you’re done exploring, leave the room and drop off any items you no longer need.
- **UDP Communication**: The client and server communicate over a network using UDP, just like a dungeon master giving and receiving commands from the player.

## How It Works

1. **Game Server (`room.py`)**: The server represents a room in the game. It keeps track of items in the room and responds to player actions. It waits for messages from the client to process commands like `look`, `take`, `drop`, `inventory`, and `exit`.
   
2. **Game Client (`player.py`)**: The client acts as the player, sending commands to the server to interact with the room. You can join the room, explore, and interact with the environment, just like the text-based adventurers of the past!

## Commands
Once you’re in the room, here are some commands you can use to interact with the game:

- **look**: Displays the room’s name, description, and any items you can interact with.
- **take [item]**: Picks up an item from the room and adds it to your inventory.
- **drop [item]**: Drops an item from your inventory and leaves it in the room.
- **inventory**: Displays the items you're carrying.
- **exit**: Leaves the game, dropping all items in the room before you go.

## Example

### Starting the Server:
```bash
python3 room.py 7777 "Cavern of Secrets" "A dark and echoey cave with hidden treasures." "torch sword shield"


Starting the Client:
python3 player.py Alice room://localhost:7777


Interaction Example:
> look
You are in Cavern of Secrets. A dark and echoey cave with hidden treasures.
You see: torch, sword, shield.

> take torch
You pick up the torch.

> inventory
You are carrying: torch.

> drop torch
You dropped the torch.

> exit
You have left the game.


Technology Behind the Game
Python & Socket Programming: The game is built using Python’s socket library for networking, where the client and server communicate over UDP. This allows for real-time interaction between the player and the game environment.
Argparse for Command-Line Options: Command-line arguments are used to set up the game server and the player client, letting you specify room details and player names.
What’s Next?
This project was built as a starting point, just like the first rooms of a much larger dungeon. In future iterations, I plan to add multiple rooms, more players, and perhaps even some creatures lurking in the dark! But for now, enjoy this first step into the adventure.


That’s the Dungeon Adventure! It’s a simple throwback to the classic days of text-based games, but with modern code and network communication. I hope you enjoy exploring this mini-adventure as much as I did making it!


