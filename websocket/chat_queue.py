from datetime import datetime
from itertools import cycle
import socket
import threading
from message_handler import MessageHandler, ChatMessage

from utils import mesg_index

class ChatQueue(object):
    """
        Maintains a queue of chat messages and exposes read and write operations to the queue.
    """
    def __init__(self, room_id: str, max_len: int, message_handler: MessageHandler, max_index: int = 100):
        self.cyclic_count = cycle(range(max_index))
        self.current_idx = -1
        self.max_idx = max_index
        self.room_id = room_id
        self.messages = []
        self.max_len = max_len

        # fetch # max_len most recent messages for this room from the database
        self.message_handler = message_handler
        self.messages = self.message_handler.get_most_recent_messages(room_id, max_len, self.cyclic_count)
        
        # test - should print (max_len) => test passed
        # self.current_idx = next(self.cyclic_count)
        # print(f'current_idx: {self.current_idx}')

        self.read_cnt = 0
        self.write_cnt = 0
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
            # print(f'IDX TO READ FROM: {idx_to_read_from}')
            response = self.messages[idx_to_read_from:]

        self.read_cnt_mtx.acquire()
        self.read_cnt -= 1
        if (self.read_cnt == 0):
            # if this is the last reader, release the write mutex so that writer is able to write now
            self.write_mtx.release()
        self.read_cnt_mtx.release()

        return response

    def writer(self, data: dict) -> None:
        # no other readers allowed to read and no other writers allowed to write
        # enter critical section~!
        self.write_mtx.acquire()

        # bulk insert messages to the database if the chat queue has completed one full cycle of its length
        if (self.write_cnt >= self.max_len):
            self.message_handler.write_to_db(self.messages)
            self.write_cnt = 0

        self.current_idx = next(self.cyclic_count)
        self.messages.append(ChatMessage(self.current_idx, datetime.utcnow(), data["content"], data["sender"], self.room_id))
        self.write_cnt += 1

        if (len(self.messages) > self.max_len):
            del self.messages[0]
        # leave critical section~!
        self.write_mtx.release()


if __name__ == "__main__":
    # test code
    message_handler = MessageHandler()
    cq = ChatQueue("Room 1", 10, message_handler)