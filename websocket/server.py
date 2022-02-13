import socket
import threading
import time
from datetime import datetime
from itertools import cycle
import sys

from utils import get_date_repr
from database_manager import messages_collection

def mesg_index(old, last, new, max_index):
    """
    Reference: http://faculty.salina.k-state.edu/tim/NPstudy_guide/servers/Project5_chat_Server.html#project5-chat-server
    :param old: integer index of oldest (first) message in queue
    :param last: integer index of last message read by the client thread
    :param new: integer index of newest (last) message in the queue

    This computes the index value of the message queue from where the reader
    should return messages.  It accounts for having a cyclic counter.
    This code is a little tricky because it has to catch all possible
    combinations.
    """
    if new >= old:
        # normal case
        if last >= old and last < new:
            return (last - old + 1)
        else:
            return 0
    else:
        # cyclic roll over (new < old)
        if last >= old:
            return (last - old + 1)
        elif last < new:
            return (max_index - old + last)
        else:
            return 0


class ChatMessage(object):
    """
        Object that holds the chat message.
    """
    def __init__(self, msg_idx: int, timestamp: datetime, data: str):
        self.msg_idx = msg_idx
        self.timestamp = timestamp
        self.data = data

class ChatQueue(object):
    """
        Maintains a queue of chat messages and exposes read and write operations to the queue.
    """
    def __init__(self, room: str, max_len: int, max_index: int = 100):
        self.cyclic_count = cycle(range(max_index))
        self.current_idx = -1
        self.max_idx = max_index
        self.room = room
        self.messages = []
        self.max_len = max_len
        self.read_cnt = 0
        self.write_mtx = threading.Lock()
        self.read_cnt_mtx = threading.Lock()


    def reader(self, last_read: int) -> list:
        # only one thread is allowed to change the read count at a time
        self.read_cnt_mtx.acquire()
        self.read_cnt += 1
        if (self.read_cnt == 1):
            # if this is the first reader, make sure that no writer is writing to the queue
            self.write_mtx.acquire()
        self.read_cnt_mtx.release()

        # perform read
        if (last_read == self.current_idx):
            response = None
        else:
            idx_to_read_from = mesg_index(self.messages[0].msg_idx, last_read, self.current_idx, self.max_idx)
            response = self.messages[idx_to_read_from:]

        self.read_cnt_mtx.acquire()
        self.read_cnt -= 1
        if (self.read_cnt == 0):
            # if this is the last reader, release the write mutex so that writer is able to write now
            self.write_mtx.release()
        self.read_cnt_mtx.release()

        return response

    def writer(self, data: str):
        # no other readers allowed to read and no other writers allowed to write
        # enter critical section~!
        self.write_mtx.acquire()
        self.current_idx = next(self.cyclic_count)
        self.messages.append(ChatMessage(self.current_idx, datetime.utcnow(), data))
        if (len(self.messages) > self.max_len):
            del self.messages[0]
        # leave critical section~!
        self.write_mtx.release()



def send_all(sd: socket.socket, last_read: int) -> int:
    reading = chat_queue.reader(last_read)
    if reading is None:
        return last_read
    for chat_message in reading:
        last_idx = chat_message.msg_idx
        timestamp = chat_message.timestamp
        msg = chat_message.data
        send_msg = get_date_repr(timestamp) + ", " + msg
        print(f'DEBUG: send_msg = {send_msg}')
        sd.send(bytes(send_msg, "utf-8"))
    return last_idx


def client_exit(client_socket: socket.socket, peer: str):
    msg = peer + " disconnected\r\n"
    chat_queue.writer(msg)


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
    msg = f'{user_id} has connected!\r\n'
    chat_queue.writer(msg)
    while True:
        last_read = send_all(client_socket, last_read)
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
            client_exit(client_socket, user_id)
            break
        
        if not len(data):
            # size of data is zero => client has disconnected
            client_exit(client_socket, user_id)
            break

        msg = f'{user_id}: '
        msg += data.decode("utf-8") + "\r\n"
        chat_queue.writer(msg)
    
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
    print(f'host address: {host}')
    MAX_BUF = 4096
    chat_queue = ChatQueue(1, 10, 100)
    main(host, port)
