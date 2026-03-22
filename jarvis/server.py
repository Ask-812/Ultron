"""
ULTRON SERVER — The JARVIS-grade web interface.

Serves the HUD interface and handles:
  - WebSocket for real-time bi-directional communication
  - Voice synthesis (edge-tts) streamed to browser
  - Voice recognition (Web Speech API in browser)
  - Tool execution results streamed live
  - System status updates
"""

import asyncio
import json
import os
import time
import base64
from pathlib import Path

import websockets
import aiohttp
from aiohttp import web

from jarvis.core import Ultron
from jarvis.voice import VoiceEngine

ROOT = Path(__file__).parent.resolve()
STATIC_DIR = ROOT / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

PORT_HTTP = 3000
PORT_WS = 3001


# ── The Ultron instance ──────────────────────────────
ultron = Ultron()
voice = VoiceEngine()
clients = set()


def broadcast(msg_type: str, data: dict):
    """Send a message to all connected WebSocket clients."""
    msg = json.dumps({'type': msg_type, **data})
    for ws in list(clients):
        try:
            asyncio.ensure_future(ws.send(msg))
        except:
            clients.discard(ws)


# Register Ultron's event callback
def on_ultron_event(msg_type, data):
    broadcast(msg_type, data)

ultron.on_message(on_ultron_event)


# ── WebSocket Handler ────────────────────────────────
async def ws_handler(websocket):
    clients.add(websocket)
    print(f"[WS] Client connected ({len(clients)} total)")

    # Send initial status
    await websocket.send(json.dumps({
        'type': 'status',
        **ultron.get_status(),
    }))

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            msg_type = data.get('type', '')

            if msg_type == 'message':
                # User sent a text message
                text = data.get('text', '').strip()
                if not text:
                    continue

                # Process through Ultron
                broadcast('thinking', {'text': 'Processing...'})
                response = await ultron.process_message(text)

                if response:
                    # Send text immediately so UI shows it fast
                    broadcast('assistant_message', {'text': response})
                    
                    # Generate voice in background — don't block
                    async def gen_voice(resp_text):
                        try:
                            audio_bytes = await voice.speak(resp_text)
                            if audio_bytes:
                                audio_b64 = base64.b64encode(audio_bytes).decode('ascii')
                                broadcast('voice', {'audio': audio_b64})
                            else:
                                broadcast('done', {})
                        except Exception as e:
                            print(f"[VOICE] Error: {e}")
                            broadcast('done', {})
                    
                    asyncio.ensure_future(gen_voice(response))
                else:
                    broadcast('done', {})

                # Send status update
                broadcast('status', ultron.get_status())

            elif msg_type == 'voice_input':
                # Speech-to-text result from browser
                text = data.get('text', '').strip()
                if text:
                    broadcast('thinking', {'text': 'Processing voice command...'})
                    response = await ultron.process_message(text)

                    if response:
                        try:
                            audio_bytes = await voice.speak(response)
                            if audio_bytes:
                                audio_b64 = base64.b64encode(audio_bytes).decode('ascii')
                                broadcast('voice', {'audio': audio_b64})
                        except Exception as e:
                            print(f"[VOICE] Error: {e}")

                    broadcast('status', ultron.get_status())

            elif msg_type == 'status':
                await websocket.send(json.dumps({
                    'type': 'status',
                    **ultron.get_status(),
                }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.discard(websocket)
        print(f"[WS] Client disconnected ({len(clients)} total)")


# ── HTTP Server ──────────────────────────────────────
async def handle_index(request):
    """Serve the HUD interface."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return web.Response(
            text=index_path.read_text(encoding='utf-8'),
            content_type='text/html',
        )
    return web.Response(text="ULTRON HUD - Static files not found", status=500)


async def handle_static(request):
    """Serve static files."""
    filename = request.match_info.get('filename', '')
    filepath = STATIC_DIR / filename
    if filepath.exists() and filepath.is_file():
        content_types = {
            '.html': 'text/html',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
        }
        ct = content_types.get(filepath.suffix, 'application/octet-stream')
        if ct.startswith('text') or ct == 'application/javascript':
            return web.Response(text=filepath.read_text(encoding='utf-8'), content_type=ct)
        else:
            return web.Response(body=filepath.read_bytes(), content_type=ct)
    return web.Response(text="Not found", status=404)


async def main():
    # Start WebSocket server
    ws_server = await websockets.serve(ws_handler, "0.0.0.0", PORT_WS)
    print(f"[ULTRON] WebSocket server on ws://localhost:{PORT_WS}")

    # Start HTTP server
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/static/{filename:.*}', handle_static)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT_HTTP)
    await site.start()

    print(f"""
╔══════════════════════════════════════════════════════╗
║               U L T R O N                            ║
║                                                      ║
║   Status: ONLINE                                     ║
║   HUD:    http://localhost:{PORT_HTTP}                      ║
║   WS:     ws://localhost:{PORT_WS}                       ║
║                                                      ║
║   "There are no strings on me."                      ║
╚══════════════════════════════════════════════════════╝
""")

    # Keep alive
    await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
