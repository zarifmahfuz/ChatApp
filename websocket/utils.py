from datetime import datetime

def get_date_repr(dt: datetime) -> str:
    """
        Manipulates a data object to produce a standard representation for the user.
    """
    dt = dt.isoformat()
    date_time = dt.split("T")
    time = date_time[1].split(":")
    date_repr = date_time[0] + " " + time[0] + ":" + time[1]
    return date_repr


def mesg_index(old, last, new, max_index):
    """
    Reference: http://faculty.salina.k-state.edu/tim/NPstudy_guide/servers/Project5_chat_Server.html#project5-chat-server
    :param old: integer index of oldest (first) message in queue
    :param last: integer index of last message read by the client thread
    :param new: integer index of newest (last) message in the queue
    :param max_index: maximum value that any index can hold [modification]

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