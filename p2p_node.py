import os
import uuid
import socket
import threading
from protocol import send_msg, recv_msg, recv_all

class P2PNode:
    def __init__(self, name, port, ui_callback):
        self.name = name
        self.port = int(port)
        self.peer_id = str(uuid.uuid4())[:8]
        self.ui_callback = ui_callback
        
        self.server_socket = None
        self.is_running = False
        self.peers = {}  # {peer_id: {'name': name, 'socket': socket, 'address': addr, 'port': port}}
        self.lock = threading.Lock()
        
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

    def log(self, text):
        self.ui_callback("log", text)

    def update_peer_list_ui(self):
        peer_list = [f"{info['name']} [{pid}] ({info['address'][0]}:{info['port']})" 
                     for pid, info in self.peers.items()]
        self.ui_callback("peers", peer_list)

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            self.log(f"[SYSTEM] Peer started: {self.name} [{self.peer_id}] on port {self.port}")
            threading.Thread(target=self._accept_connections, daemon=True).start()
        except Exception as e:
            self.log(f"[ERROR] Failed to start server: {e}")

    def stop_server(self):
        self.is_running = False
        with self.lock:
            for pid, info in list(self.peers.items()):
                try:
                    info['socket'].close()
                except:
                    pass
            self.peers.clear()
            
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.update_peer_list_ui()
        self.log("[SYSTEM] Peer stopped.")

    def _accept_connections(self):
        while self.is_running:
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_peer, args=(conn, addr), daemon=True).start()
            except:
                break

    def connect_to_peer(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, int(port)))
            
            hello_data = {
                "type": "hello",
                "peer_id": self.peer_id,
                "peer_name": self.name,
                "port": self.port
            }
            send_msg(sock, hello_data)
            threading.Thread(target=self._handle_peer, args=(sock, (ip, int(port))), daemon=True).start()
        except Exception as e:
            self.log(f"[ERROR] Connection failed: {e}")

    def _handle_peer(self, sock, addr):
        remote_id = None
        try:
            while self.is_running:
                msg = recv_msg(sock)
                if not msg:
                    break
                
                msg_type = msg.get("type")
                
                if msg_type in ("hello", "hello_ack"):
                    remote_id = msg["peer_id"]
                    with self.lock:
                        self.peers[remote_id] = {
                            "name": msg["peer_name"],
                            "socket": sock,
                            "address": addr,
                            "port": msg["port"]
                        }
                    self.log(f"[SYSTEM] Connected to {msg['peer_name']}")
                    self.update_peer_list_ui()
                    
                    if msg_type == "hello":
                        ack_msg = {
                            "type": "hello_ack",
                            "peer_id": self.peer_id,
                            "peer_name": self.name,
                            "port": self.port
                        }
                        send_msg(sock, ack_msg)

                elif msg_type == "text":
                    sender = msg.get("sender_name", "Unknown")
                    self.log(f"{sender} -> You: {msg['message']}")

                elif msg_type == "file":
                    filename = os.path.basename(msg["filename"])
                    filesize = msg["filesize"]
                    sender = msg.get("sender_name", "Unknown")
                    filepath = os.path.join("downloads", filename)
                    
                    received_bytes = 0
                    with open(filepath, "wb") as f:
                        while received_bytes < filesize:
                            chunk_size = min(64 * 1024, filesize - received_bytes)
                            chunk = recv_all(sock, chunk_size)
                            if not chunk:
                                raise Exception("Connection lost during file transfer.")
                            f.write(chunk)
                            received_bytes += len(chunk)
                            
                    self.log(f"{sender} -> You: File received: {filename}")
        except Exception as e:
            if self.is_running:
                self.log(f"[ERROR] Socket error: {e}")
        finally:
            with self.lock:
                if remote_id and remote_id in self.peers:
                    p_name = self.peers[remote_id]['name']
                    del self.peers[remote_id]
                    self.log(f"[SYSTEM] Disconnected from {p_name}")
                    self.update_peer_list_ui()
            try:
                sock.close()
            except:
                pass

    def send_text(self, peer_id, text):
        with self.lock:
            info = self.peers.get(peer_id)
        if info:
            msg = {
                "type": "text",
                "sender_id": self.peer_id,
                "sender_name": self.name,
                "message": text
            }
            try:
                send_msg(info['socket'], msg)
                self.log(f"You -> {info['name']}: {text}")
            except Exception as e:
                self.log(f"[ERROR] Failed to send message: {e}")

    def send_file(self, peer_id, filepath):
        with self.lock:
            info = self.peers.get(peer_id)
        if info and os.path.exists(filepath):
            sock = info['socket']
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            meta = {
                "type": "file",
                "sender_id": self.peer_id,
                "sender_name": self.name,
                "filename": filename,
                "filesize": filesize
            }
            try:
                # 1. Send JSON Metadata Header
                send_msg(sock, meta)
                
                # 2. Send Raw Bytes Stream (Chunked)
                with open(filepath, "rb") as f:
                    while True:
                        chunk = f.read(64 * 1024)
                        if not chunk:
                            break
                        sock.sendall(chunk)
                self.log(f"You -> {info['name']}: File sent: {filename}")
            except Exception as e:
                self.log(f"[ERROR] Failed to send file: {e}")