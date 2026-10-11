# P2P Chat and Binary File Transfer Application

A lightweight, decentralized Peer-to-Peer (P2P) desktop network application for real-time text messaging and file sharing built using Python, TCP Sockets, and Tkinter GUI.

---

##  Tech Stack & Dependencies

- **Programming Language:** Python 3.x
- **Networking Protocol:** TCP Sockets (`socket` module) - Ensures reliable, ordered delivery of data streams.
- **Concurrency Model:** Multi-threading (`threading` module) - Keeps the GUI responsive while handling background network listening and file I/O.
- **Data Serialization & Framing:** `json` & `struct` - Uses a custom 4-byte length-prefix framing protocol to safely buffer and reconstruct messages/files without data corruption.
- **User Interface:** Tkinter & TTK (`tkinter` module) - Simple desktop GUI for node setup and peer management.
- **IDE:** Visual Studio Code

---

##  How It Works 

1. **Decentralized Architecture:**
   - Unlike client-server applications, there is no central server. Every running instance of the application acts simultaneously as both a **Server** (listening for incoming connections) and a **Client** (connecting to other nodes).

2. **Network Listening & Threading:**
   - When a user clicks **Start Peer**, a background daemon thread starts a TCP socket server listening on the specified port.
   - Separate threads are spawned dynamically to handle incoming peer requests, preventing the Tkinter GUI thread from freezing.

3. **Length-Prefixed Framing Protocol:**
   - TCP is a stream protocol without native message boundaries. To prevent packet fragmentation or merging, every outgoing payload is formatted into JSON and prefixed with a 4-byte big-endian integer indicating its length.
   - The receiving node reads the first 4 bytes to determine exact payload size before reading the actual message or file buffer.

4. **File Transfer Pipeline:**
   - Binary files (images, PDFs, archives) are read in chunk buffers, base64-encoded or directly streamed with framing metadata, and automatically stored inside the local `/downloads` folder upon reception.

---

## 📂 Project Structure

```text
P2P_Assignment/
├── main.py              # Tkinter GUI application & event handling
├── p2p_node.py          # Core P2P node logic, multi-threading & socket listener
├── protocol.py          # Custom length-prefix protocol encoder/decoder
├── requirements.txt     # Dependency information
├── README.md            # Application documentation
└── downloads/           # Automatic destination directory for incoming files
