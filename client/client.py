from concurrent.futures import thread
import socket
import sys
import threading
from login import LoginHandler
from room_handler import RoomHandler

def listen_from_server(sd: socket.socket):
    """
        Thread callback that listens for new messages sent from the chat server.
    """
    while True:
        try:
            data = sd.recv(MAX_BUF)
        except socket.timeout:
            continue
        except Exception as e:
            print("Disconnected from websocket server.")
            break
        # print the received data
        print("\r\n" + data.decode("utf-8"))
        

def start_chat(user_id: str, room_id: str):
    client_socket = socket.socket()
    client_socket.settimeout(1)
    
    class HandshakeProtocol:
        """
            Serves needs some metadata from the client before progressing further. This class defines a protocol
            of information exchange when a client first connects to the server.
        """
        Listen, SendUserId, SendRoomId, Done = range(0, 4)

    hp_state = HandshakeProtocol.Listen
    client_socket.connect((server_address, port))
    while True:
        if (hp_state == HandshakeProtocol.Listen):
            try:
                data_received = client_socket.recv(MAX_BUF).decode("utf-8")
                if (data_received == "U"):
                    hp_state = HandshakeProtocol.SendUserId
                elif (data_received == "R"):
                    hp_state = HandshakeProtocol.SendRoomId
                elif ("ACK" in data_received):
                    hp_state = HandshakeProtocol.Done
            except (socket.timeout):
                continue

        elif (hp_state == HandshakeProtocol.SendUserId):
            client_socket.send(bytes(user_id, "utf-8"))
            hp_state = HandshakeProtocol.Listen
            # print("Last State: SendUserId")

        elif (hp_state == HandshakeProtocol.SendRoomId):
            client_socket.send(bytes(room_id, "utf-8"))
            hp_state = HandshakeProtocol.Listen
            # print("Last State: SendRoomId")

        elif (hp_state == HandshakeProtocol.Done):
            print("Successfully connected to server!")
            break

    # at this point, websocket server will let us into our requested room
    # launch a thread for listening for incoming chat messages from the server
    receiver = threading.Thread(target = listen_from_server, args = [client_socket], daemon = True)
    receiver.start()

    # this thread will be used to send messages to the server
    while True:
        try:
            msg = input()
            if (msg.startswith("/exitRoom")):
                break
            bytes_sent = client_socket.send(bytes(msg, "utf-8"))
        except Exception as e:
            print("Client stopped.")
            print(e)
            break
    
    client_socket.close()
    receiver.join()
    print("Child thread ended")
    return

def cli_after_login(user_id: str):
    class FSM2:
        """
            Defines the states for a CLI state machine after the user has logged in.
        """
        Idle, Commands, Logout, ViewRooms, JoinRoom, Quit = range(0, 6)

    curr_state = FSM2.Commands
    room_handler = RoomHandler()
    while True:
        if (curr_state == FSM2.Commands):
            print("\r\nCommands:")
            print("/quit -- to quit the application")
            print("/rooms -- to see the list of available rooms")
            print("/join -- to join a room")
            print("/logout -- to go back/log out")
            print("/commands -- to see the list of commands")
            curr_state = FSM2.Idle

        elif (curr_state == FSM2.Idle):
            cmd = input("Enter a command: ")

            if (cmd.startswith("/join")):
                curr_state = FSM2.JoinRoom
            elif (cmd.startswith("/rooms")):
                curr_state = FSM2.ViewRooms
            elif (cmd.startswith("/logout")):
                curr_state = FSM2.Logout
            elif (cmd.startswith("/commands")):
                curr_state = FSM2.Commands
            elif (cmd.startswith("/quit")):
                curr_state = FSM2.Quit
            else:
                print("Invalid command...")
        
        elif (curr_state == FSM2.Logout):
            return

        elif (curr_state == FSM2.Quit):
            sys.exit(0)

        elif (curr_state == FSM2.ViewRooms):
            # display the list of rooms
            rooms = room_handler.get_rooms()
            print("Rooms IDs: ")
            for room in rooms:
                print(room)
            curr_state = FSM2.Idle

        elif (curr_state == FSM2.JoinRoom):
            room_id = input("Enter a valid room id: ")
            if (room_handler.join_room(room_id, user_id) is True):
                print(f'You joined room {room_id}')
                print("Commands:")
                print("/exitRoom --- to exit room")
                start_chat(user_id, room_id)
                curr_state = FSM2.Idle
            else:
                curr_state = FSM2.Idle


def cli_before_login():
    class FSM1:
        """
            Defines the states for a CLI state machine prior to a user's login.
        """
        Idle, Commands, Login, Register, Quit = range(0, 5)

    curr_state = FSM1.Commands
    login_handler = LoginHandler()
    while True:
        if (curr_state == FSM1.Idle):
            cmd = input("Enter a command: ")

            if (cmd.startswith("/login")):
                curr_state = FSM1.Login
            elif (cmd.startswith("/register")):
                curr_state = FSM1.Register
            elif (cmd.startswith("/commands")):
                curr_state = FSM1.Commands
            elif (cmd.startswith("/quit")):
                curr_state = FSM1.Quit
            else:
                print("Invalid command...")
        
        elif (curr_state == FSM1.Commands):
            print("\r\nCommands:")
            print("/login")
            print("/register")
            print("/quit -- to quit the application")
            print("/commands -- to see the full list of commands")
            curr_state = FSM1.Idle

        elif (curr_state == FSM1.Quit):
            sys.exit(0)

        elif (curr_state == FSM1.Login):
            user_id = input("Enter userid: ")
            password = input("Enter password: ")
            if login_handler.verify_user(user_id, password) is True:
                print("Login successful")
                cli_after_login(user_id)
                curr_state = FSM1.Commands
            else:
                print("Please try again...")
                curr_state = FSM1.Idle

        elif (curr_state == FSM1.Register):
            user_id = input("Enter userid: ")
            password = input("Enter password: ")
            name = input("Enter your name: ")
            email = input("Enter your email: ")
            if (login_handler.register_user(user_id, password, name, email) is True):
                print("Registration successful")
                cli_after_login(user_id)
                curr_state = FSM1.Commands
            else:
                print("Please try again...")
                curr_state = FSM1.Idle


if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid arguments.")
        sys.exit(1)

    server_address = socket.gethostbyname("websocket")
    print(f'server_address: {server_address}')

    MAX_BUF = 4096
    cli_before_login()
