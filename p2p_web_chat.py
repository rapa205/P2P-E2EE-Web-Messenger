import asyncio
import json
import argparse
import websockets
from cryptography.fernet import Fernet

def get_html_page(ws_port):
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>P2P E2EE Messenger</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .chat-container {{ width: 450px; background: #1e293b; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow: hidden; height: 600px; }}
        .chat-header {{ background: #3b82f6; padding: 15px; font-weight: bold; text-align: center; font-size: 16px; }}
        .chat-messages {{ flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }}
        .message {{ padding: 10px 14px; border-radius: 8px; max-width: 75%; word-break: break-word; font-size: 14px; }}
        .message.incoming {{ background: #334155; align-self: flex-start; }}
        .message.outgoing {{ background: #2563eb; align-self: flex-end; }}
        .chat-input {{ display: flex; padding: 12px; background: #0f172a; border-top: 1px solid #334155; }}
        .chat-input input {{ flex: 1; background: #1e293b; border: 1px solid #475569; padding: 10px; border-radius: 6px; color: white; outline: none; font-size: 14px; }}
        .chat-input input:focus {{ border-color: #3b82f6; }}
        .chat-input button {{ background: #3b82f6; color: white; border: none; padding: 10px 18px; margin-left: 8px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
        .chat-input button:hover {{ background: #2563eb; }}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">🔒 P2P Secure Chat (E2EE)</div>
        <div class="chat-messages" id="messages"></div>
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Введите сообщение..." autofocus onkeydown="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Отправить</button>
        </div>
    </div>

    <script>
        const ws = new WebSocket("ws://localhost:{ws_port}");
        const messagesDiv = document.getElementById("messages");

        ws.onopen = function() {{
            console.log("✅ WebSocket Connected successfully!");
        }};

        ws.onerror = function(error) {{
            console.error("❌ WebSocket Error:", error);
        }};

        ws.onmessage = function(event) {{
            console.log("📩 Received from server:", event.data);
            const data = JSON.parse(event.data);
            const msgDiv = document.createElement("div");
            msgDiv.className = "message " + data.type;
            msgDiv.textContent = data.text;
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }};

        function sendMessage() {{
            const input = document.getElementById("messageInput");
            const text = input.value.trim();
            if (!text) return;
            
            console.log("📤 Sending message:", text);
            ws.send(text);
            
            const msgDiv = document.createElement("div");
            msgDiv.className = "message outgoing";
            msgDiv.textContent = "You: " + text;
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            input.value = "";
        }}
    </script>
</body>
</html>
"""

class WebP2PNode:
    def __init__(self, bind_port, peer_host, peer_port, http_port, ws_port, shared_key=None):
        self.bind_port = bind_port
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.http_port = http_port
        self.ws_port = ws_port
        
        if shared_key:
            self.key = shared_key.encode()
        else:
            self.key = Fernet.generate_key()
            print(f"\n🔑 [SECRET KEY]: {self.key.decode()}\n")
            
        self.cipher = Fernet(self.key)
        self.browser_clients = set()
        self.peer_writer = None

    async def p2p_server_handler(self, reader, writer):
        print("🟢 [P2P] Peer connected to our server.")
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                try:
                    decrypted = self.cipher.decrypt(data).decode()
                    print(f"📩 Decrypted incoming: {decrypted}")
                    
                    # ОТПРАВЛЯЕМ В БРАУЗЕР (этого не хватало!)
                    payload = json.dumps({"type": "incoming", "text": f"Peer: {decrypted}"})
                    for ws in self.browser_clients:
                        await ws.send(payload)
                except Exception as e:
                    print(f"❌ Decryption error: {e}")
        finally:
            writer.close()

    async def p2p_client_loop(self):
        await asyncio.sleep(1)
        while True:
            try:
                reader, writer = await asyncio.open_connection(self.peer_host, self.peer_port)
                self.peer_writer = writer
                print("🔗 P2P Link established with peer!")
                
                while True:
                    data = await reader.read(4096)
                    if not data:
                        break
                    try:
                        decrypted = self.cipher.decrypt(data).decode()
                        print(f"📩 Decrypted from client loop: {decrypted}")
                        
                        # ОТПРАВЛЯЕМ В БРАУЗЕР (и здесь тоже!)
                        payload = json.dumps({"type": "incoming", "text": f"Peer: {decrypted}"})
                        for ws in self.browser_clients:
                            await ws.send(payload)
                    except Exception as e:
                        print(f"❌ Client Decryption error: {e}")
            except:
                await asyncio.sleep(3)

    async def ws_handler(self, websocket):
        print("💻 [BROWSER] Browser connected via WebSocket")
        self.browser_clients.add(websocket)
        try:
            async for message in websocket:
                print(f"💻 [BROWSER MESSAGE]: {message}")
                if self.peer_writer:
                    try:
                        encrypted = self.cipher.encrypt(message.encode())
                        self.peer_writer.write(encrypted)
                        await self.peer_writer.drain()
                        print("🚀 [P2P SENT] Encrypted message sent to peer.")
                    except Exception as e:
                        print(f"❌ Send error: {e}")
                else:
                    print("⚠️ [WARNING] No peer writer available (not connected to peer yet).")
        finally:
            self.browser_clients.remove(websocket)
            print("💻 [BROWSER] Browser disconnected")

    async def http_server(self, reader, writer):
        html_content = get_html_page(self.ws_port)
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n{html_content}"
        writer.write(response.encode('utf-8'))
        await writer.drain()
        writer.close()

    async def run(self):
        p2p_srv = await asyncio.start_server(self.p2p_server_handler, "0.0.0.0", self.bind_port)
        http_srv = await asyncio.start_server(self.http_server, "127.0.0.1", self.http_port)
        ws_srv = await websockets.serve(self.ws_handler, "127.0.0.1", self.ws_port)
        
        print(f"🌐 [WEB UI] Open browser at: http://localhost:{self.http_port}")

        asyncio.create_task(self.p2p_client_loop())
        
        await asyncio.gather(
            p2p_srv.serve_forever(),
            http_srv.serve_forever(),
            ws_srv.wait_closed()
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P2P Web Messenger")
    parser.add_argument("--port", type=int, required=True, help="Your P2P port")
    parser.add_argument("--peer-host", required=True, help="Peer IP")
    parser.add_argument("--peer-port", type=int, required=True, help="Peer port")
    parser.add_argument("--http-port", type=int, default=8080, help="HTTP port for browser")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket port")
    parser.add_argument("--key", default=None, help="Shared key")

    args = parser.parse_args()
    
    node = WebP2PNode(args.port, args.peer_host, args.peer_port, args.http_port, args.ws_port, args.key)
    try:
        asyncio.run(node.run())
    except KeyboardInterrupt:
        print("\n👋 App stopped.")