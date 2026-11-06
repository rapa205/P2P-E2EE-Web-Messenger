Markdown
# 🔒 P2P E2EE Web Messenger

A lightweight, secure peer-to-peer encrypted messenger built from scratch in Python. It features direct node-to-node TCP communication, end-to-end encryption (E2EE) using Fernet (AES), an asynchronous core via `asyncio`, WebSockets, and a modern dark-mode web UI.

---

## 🚀 Key Features

* **True P2P Architecture**: No central servers or intermediaries. Nodes communicate directly with each other.
* **End-to-End Encryption (E2EE)**: Messages are symmetrically encrypted on the client side. Only peers sharing the secret key can decrypt them.
* **Modern Web Interface**: A clean, responsive dark-mode UI accessible via your web browser.
* **Async Engine**: Powered by Python's `asyncio` for high-performance, non-blocking networking.
* **Flexible Configuration**: Easily run and test multi-node setups locally or across networks using command-line arguments.

---

## 🛠️ Tech Stack

* **Python 3.10+**
* `asyncio` (Networking & Concurrency)
* `cryptography` (Fernet symmetric encryption)
* `websockets` (Browser-to-Python bridge)
* HTML5 / CSS3 / JavaScript (Frontend UI)

---

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/p2p-web-messenger.git](https://github.com/YOUR_USERNAME/p2p-web-messenger.git)
   cd p2p-web-messenger
Install dependencies:

Bash
pip install websockets cryptography
Run Node 1:

Bash
python p2p_chat.py --port 8888 --peer-host 127.0.0.1 --peer-port 9999 --http-port 8080 --ws-port 8765
Open http://localhost:8080 in your browser.

Copy the generated SECRET KEY from the terminal.

Run Node 2 (in a separate terminal):

Bash
python p2p_chat.py --port 9999 --peer-host 127.0.0.1 --peer-port 8888 --http-port 8081 --ws-port 8766 --key "YOUR_COPIED_KEY"
Open http://localhost:8081 in another browser tab or window, and start chatting!
