import json
import struct

def send_msg(sock, msg_dict):
    """Encodes JSON message with a 4-byte length header."""
    json_data = json.dumps(msg_dict).encode('utf-8')
    length_prefix = struct.pack('!I', len(json_data))
    sock.sendall(length_prefix + json_data)

def recv_msg(sock):
    """Reads a 4-byte length header and returns the parsed JSON message."""
    raw_length = recv_all(sock, 4)
    if not raw_length:
        return None
    length = struct.unpack('!I', raw_length)[0]
    json_data = recv_all(sock, length)
    if not json_data:
        return None
    return json.loads(json_data.decode('utf-8'))

def recv_all(sock, count):
    """Helper function to receive exactly `count` bytes from socket."""
    buf = b''
    while len(buf) < count:
        newbuf = sock.recv(count - len(buf))
        if not newbuf:
            return None
        buf += newbuf
    return buf