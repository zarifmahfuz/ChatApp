import socket
import threading
import time
import sys
from chat_queue import ChatQueue
from message_handler import MessageHandler
from utils import get_date_repr
from room_manager import RoomManager


def send_all(sd: socket.socket, last_read: int, room_id: str) -> int:
    """
        Sends the latest messages in a given room to a client socket.
    """
    reading = chat_rooms[room_id].reader(last_read)
    if reading is None:
        return last_read
    for chat_message in reading:
        last_idx = chat_message.msg_idx
        send_msg = chat_message.gata_data_for_pres()
        print(f'DEBUG: send_msg = {send_msg}')
        sd.send(bytes(send_msg, "utf-8"))
    return last_idx


def client_exit(user_id: str, room_id: str):
    """
        Sends a message to the writer when a client disconnects to notify other users in the room.
    """
    msg = "disconnected\r\n"
    chat_rooms[room_id].writer({"content": msg, "sender": user_id})


def handle_client(client_socket: socket.socket):
    """
        Client thread callback. Serves a client.
    """
    class HandshakeProtocol:
        """
            Serves needs some metadata from the client before progressing further. This class defines a protocol
            of information exchange when a client first connects to the server.
        """
        AskForUserId, AwaitUserId, AskForRoomId, AwaitRoomId, Done = range(0, 5)
    hp_state = HandshakeProtocol.AskForUserId
    user_id = ""
    room_id = ""
    while True:
        if (hp_state == HandshakeProtocol.AskForUserId):
            client_socket.send(bytes("U", "utf-8"))
            hp_state = HandshakeProtocol.AwaitUserId
            print("Last State: AskForUserId")

        elif (hp_state == HandshakeProtocol.AwaitUserId):
            try:
                data_received = client_socket.recv(MAX_BUF)
                user_id = data_received.decode("utf-8")
                if (len(user_id) > 0):
                    hp_state = HandshakeProtocol.AskForRoomId
                print("Last State: AwaitUserId")
            except (socket.timeout):
                continue

        elif (hp_state == HandshakeProtocol.AskForRoomId):
            client_socket.send(bytes("R", "utf-8"))
            hp_state = HandshakeProtocol.AwaitRoomId
            print("Last State: AskForRoomId")

        elif (hp_state == HandshakeProtocol.AwaitRoomId):
            try:
                data_received = client_socket.recv(MAX_BUF)
                room_id = data_received.decode("utf-8")
                if (len(room_id) > 0):
                    hp_state = HandshakeProtocol.Done
                print("Last State: AwaitRoomId")
            except socket.timeout:
                continue

        elif (hp_state == HandshakeProtocol.Done):
            print(f'Handshake Protocol Complete. user_id={user_id}, room_id={room_id}')
            client_socket.send(bytes("ACK", "utf-8"))
            break

        else:
            hp_state = HandshakeProtocol.AskForUserId

         
    last_read = -1
    msg = "has connected!\r\n"
    chat_rooms[room_id].writer({"content": msg, "sender": user_id})
    while True:
        last_read = send_all(client_socket, last_read, room_id)
        try:
            data = client_socket.recv(MAX_BUF)
        except socket.timeout:
            # remember that we set a timer on system calls, so that .recv does not infinitely block the thread
            continue
        except socket.error:
            # raised by the main thread when socket.close is called
            return
        except:
            # some other error
            client_exit(user_id, room_id)
            break
        
        if not len(data):
            # size of data is zero => client has disconnected
            client_exit(user_id, room_id)
            break

        msg = data.decode("utf-8") + "\r\n"
        chat_rooms[room_id].writer({"content": msg, "sender": user_id})
    
    # thread is about to exit - close client socket
    client_socket.close()


def main(host: str, port: int):
    """
        Parent thread. Listens for new connections and starts a child thread to serve each new connection.
    """
    max_pending_connections = 10
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(max_pending_connections)

    client_sockets = []
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
            # set a timeout so it won't block forever on socket.recv().
            client_socket.settimeout(1)
            
        except KeyboardInterrupt:
            server_socket.close()
            for cs in client_sockets:
                cs.close()
            break

        client_sockets.append(client_socket)
        client_thread = threading.Thread(target = handle_client, args = [client_socket], daemon = True)
        client_thread.start()

if (__name__ == "__main__"):
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Must provide a valid port number.")
        sys.exit(1)

    host = socket.gethostbyname("websocket")
    print(f'Websocker server started running at address: {host}')
    MAX_BUF = 4096
    max_chat_queue = 10

    # start the server with 4 chat rooms
    room_manager = RoomManager()
    room_ids = ["Room 1", "Room 2", "Room 3", "Room 4"]
    chat_rooms = {}
    message_handler = MessageHandler()
    for room_id in room_ids:
        id = room_manager.create_room(room_id)
        chat_rooms[id] = ChatQueue(id, max_chat_queue, message_handler)

    main(host, port)
