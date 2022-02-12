from concurrent.futures import thread
import socket
import sys
import threading

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
            print("Network connection with the server was lost.")
            print(e)
            break
        # print the received data
        print(data.decode("utf-8"))
        


def simple_client(host: str, port: int):
    client_socket = socket.socket()
    client_socket.settimeout(1)
    client_socket.connect((host, port))
    receiver = threading.Thread(target = listen_from_server, args = [client_socket], daemon = True)
    receiver.start()
    while True:
        try:
            msg = input("Send something: ")
            # socket_wrt_mtx.acquire()
            bytes_sent = client_socket.send(bytes(msg, "utf-8"))
            # socket_wrt_mtx.release()
        except Exception as e:
            print("Client stopped.")
            print(e)
            break
    
    client_socket.close()
    return


if __name__ == "__main__":
    try:
        server_address = sys.argv[1]
        port = int(sys.argv[2])
    except ValueError:
        print("Invalid arguments.")
        sys.exit(1)

    server_address = socket.gethostbyname("websocket")
    print(f'server_address: {server_address}')

    # only one thread can perform socket io at a time
    socket_wrt_mtx = threading.Lock()
    MAX_BUF = 4096

    simple_client(server_address, port)
