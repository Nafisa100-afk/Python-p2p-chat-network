import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from p2p_node import P2PNode

class P2PGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UAP P2P Network")
        self.root.geometry("750x550")
        
        self.node = None
        
        # Upper Section - Local Peer Setup
        f_my = ttk.LabelFrame(root, text="My Peer")
        f_my.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_my, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_name = ttk.Entry(f_my, width=15)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(f_my, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_port = ttk.Entry(f_my, width=10)
        self.ent_port.grid(row=0, column=3, padx=5, pady=5)
        
        self.btn_start = ttk.Button(f_my, text="Start Peer", command=self.start_peer)
        self.btn_start.grid(row=0, column=4, padx=5, pady=5)
        
        self.btn_stop = ttk.Button(f_my, text="Stop", command=self.stop_peer, state="disabled")
        self.btn_stop.grid(row=0, column=5, padx=5, pady=5)
        
        # Connect Section - Remote Peer
        f_conn = ttk.LabelFrame(root, text="Connect to Another Peer")
        f_conn.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_conn, text="IP:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_ip = ttk.Entry(f_conn, width=15)
        self.ent_ip.insert(0, "127.0.0.1")
        self.ent_ip.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(f_conn, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_conn_port = ttk.Entry(f_conn, width=10)
        self.ent_conn_port.grid(row=0, column=3, padx=5, pady=5)
        
        self.btn_connect = ttk.Button(f_conn, text="Connect", command=self.connect_peer, state="disabled")
        self.btn_connect.grid(row=0, column=4, padx=5, pady=5)
        
        # Middle Section - Active Peers & Messages Log
        f_mid = ttk.Frame(root)
        f_mid.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Peer Listbox
        f_peers = ttk.LabelFrame(f_mid, text="Connected Peers")
        f_peers.pack(side="left", fill="both", padx=(0, 5))
        
        self.lst_peers = tk.Listbox(f_peers, width=30)
        self.lst_peers.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Text Console / Log Area
        f_logs = ttk.LabelFrame(f_mid, text="Messages / Events")
        f_logs.pack(side="right", fill="both", expand=True)
        
        self.txt_logs = tk.Text(f_logs, state="disabled", wrap="word")
        self.txt_logs.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bottom Section - Send Text & Files
        f_send = ttk.LabelFrame(root, text="Send Text")
        f_send.pack(fill="x", padx=10, pady=2)
        
        self.ent_msg = ttk.Entry(f_send)
        self.ent_msg.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        self.btn_send_txt = ttk.Button(f_send, text="Send", command=self.send_text, state="disabled")
        self.btn_send_txt.pack(side="right", padx=5, pady=5)
        
        f_file = ttk.LabelFrame(root, text="Send File")
        f_file.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_file, text="Text, image, audio, video, PDF, ZIP, etc.").pack(side="left", padx=5)
        self.btn_send_file = ttk.Button(f_file, text="Choose File & Send", command=self.send_file, state="disabled")
        self.btn_send_file.pack(side="right", padx=5, pady=5)

    def ui_callback(self, event_type, data):
        """Thread-safe UI updater callback."""
        if event_type == "log":
            self.root.after(0, self._append_log, data)
        elif event_type == "peers":
            self.root.after(0, self._update_peers, data)

    def _append_log(self, text):
        """Appends log text to the messages panel."""
        self.txt_logs.config(state="normal")
        self.txt_logs.insert("end", text + "\n")
        self.txt_logs.see("end")
        self.txt_logs.config(state="disabled")

    def _update_peers(self, peer_list):
        """Refreshes the GUI connected peer listbox."""
        self.lst_peers.delete(0, "end")
        for p in peer_list:
            self.lst_peers.insert("end", p)

    def start_peer(self):
        """Starts local server peer instance."""
        name = self.ent_name.get().strip()
        port = self.ent_port.get().strip()
        if not name or not port.isdigit():
            messagebox.showerror("Error", "Valid Name and Port required!")
            return
        
        self.node = P2PNode(name, int(port), self.ui_callback)
        self.node.start_server()
        
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_connect.config(state="normal")
        self.btn_send_txt.config(state="normal")
        self.btn_send_file.config(state="normal")

    def stop_peer(self):
        """Stops local peer instance."""
        if self.node:
            self.node.stop_server()
            self.node = None
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.btn_connect.config(state="disabled")
        self.btn_send_txt.config(state="disabled")
        self.btn_send_file.config(state="disabled")

    def get_selected_peer_id(self):
        """Extracts target peer ID from listbox selection."""
        try:
            sel = self.lst_peers.get(self.lst_peers.curselection())
            # Format: Name [peer_id] (IP:Port)
            peer_id = sel.split('[')[1].split(']')[0]
            return peer_id
        except:
            messagebox.showwarning("Warning", "Select a peer from Connected Peers list first!")
            return None

    def connect_peer(self):
        """Connects to a remote peer."""
        ip = self.ent_ip.get().strip()
        port = self.ent_conn_port.get().strip()
        if ip and port.isdigit() and self.node:
            self.node.connect_to_peer(ip, int(port))

    def send_text(self):
        """Sends text message to selected peer."""
        peer_id = self.get_selected_peer_id()
        msg = self.ent_msg.get().strip()
        if peer_id and msg and self.node:
            self.node.send_text(peer_id, msg)
            self.ent_msg.delete(0, "end")

    def send_file(self):
        """Opens file dialog and sends selected file to target peer."""
        peer_id = self.get_selected_peer_id()
        if not peer_id or not self.node:
            return
        filepath = filedialog.askopenfilename()
        if filepath:
            self.node.send_file(peer_id, filepath)

if __name__ == "__main__":
    root = tk.Tk()
    app = P2PGUI(root)
    root.mainloop()