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
import platform
import psutil
from pathlib import Path
from datetime import datetime

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

    # Start background tasks
    asyncio.ensure_future(boot_greeting())
    asyncio.ensure_future(proactive_monitor())
    asyncio.ensure_future(system_stats_loop())

    # Keep alive
    await asyncio.Future()


# ── Boot Greeting ────────────────────────────────────────
async def boot_greeting():
    """Speak an unprompted greeting when ULTRON boots and a client connects."""
    # Wait for first client
    for _ in range(60):
        if clients:
            break
        await asyncio.sleep(1)

    if not clients:
        return

    await asyncio.sleep(2)  # Let the UI finish loading

    hour = datetime.now().hour
    if hour < 12:
        time_greeting = "Good morning"
    elif hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"

    boot_count = 1
    try:
        pfile = ROOT.parent / "jarvis" / "memory" / "personality.json"
        if pfile.exists():
            p = json.loads(pfile.read_text(encoding='utf-8'))
            boot_count = p.get('boot_count', 1)
    except:
        pass

    if boot_count <= 1:
        greeting = f"{time_greeting}, Sir. All systems are online. I am ULTRON. How may I serve you?"
    else:
        greeting = f"{time_greeting}, Sir. Systems online, boot cycle {boot_count}. All nominal."

    broadcast('assistant_message', {'text': greeting})

    try:
        audio = await voice.speak(greeting)
        if audio:
            b64 = base64.b64encode(audio).decode('ascii')
            broadcast('voice', {'audio': b64})
    except Exception as e:
        print(f"[BOOT] Voice error: {e}")


# ── Proactive Monitor ────────────────────────────────────
async def proactive_monitor():
    """Background loop that monitors the system and proactively notifies."""
    await asyncio.sleep(30)  # Let everything settle first

    last_cpu_alert = 0
    last_ram_alert = 0
    last_disk_alert = 0

    while True:
        try:
            now = time.time()

            # CPU check
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 90 and now - last_cpu_alert > 300:
                last_cpu_alert = now
                msg = f"Sir, CPU usage is critically high at {cpu:.0f}%. You may want to close some applications."
                broadcast('notification', {'text': msg, 'level': 'warning'})
                broadcast('assistant_message', {'text': msg})
                try:
                    audio = await voice.speak(msg)
                    if audio:
                        broadcast('voice', {'audio': base64.b64encode(audio).decode('ascii')})
                except:
                    pass

            # RAM check
            ram = psutil.virtual_memory()
            ram_pct = ram.percent
            if ram_pct > 90 and now - last_ram_alert > 300:
                last_ram_alert = now
                free_gb = ram.available / (1024**3)
                msg = f"Memory is running low — {ram_pct:.0f}% used, only {free_gb:.1f}GB free."
                broadcast('notification', {'text': msg, 'level': 'warning'})
                broadcast('assistant_message', {'text': msg})

            # Disk check  
            disk = psutil.disk_usage('/')
            disk_pct = disk.percent
            if disk_pct > 95 and now - last_disk_alert > 3600:
                last_disk_alert = now
                free_gb = disk.free / (1024**3)
                msg = f"Disk space critical — {disk_pct:.0f}% full, only {free_gb:.1f}GB remaining."
                broadcast('notification', {'text': msg, 'level': 'critical'})
                broadcast('assistant_message', {'text': msg})

        except Exception as e:
            pass

        await asyncio.sleep(15)  # Check every 15 seconds


# ── System Stats Broadcast ───────────────────────────────
async def system_stats_loop():
    """Continuously send real system stats to the HUD."""
    while True:
        try:
            cpu = psutil.cpu_percent(interval=0)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get battery if available
            battery = None
            try:
                bat = psutil.sensors_battery()
                if bat:
                    battery = {'percent': bat.percent, 'charging': bat.power_plugged}
            except:
                pass

            stats = {
                'cpu': round(cpu),
                'ram': round(ram.percent),
                'ram_used_gb': round(ram.used / (1024**3), 1),
                'ram_total_gb': round(ram.total / (1024**3), 1),
                'disk': round(disk.percent),
                'disk_free_gb': round(disk.free / (1024**3), 1),
                'uptime': ultron.get_status().get('uptime', ''),
                'memories': len(ultron.memory.knowledge),
                'conversations': len(ultron.memory.conversations),
                'goals': len(ultron.memory.get_active_goals()),
                'battery': battery,
            }
            broadcast('system_stats', stats)
        except:
            pass

        await asyncio.sleep(3)  # Every 3 seconds


if __name__ == '__main__':
    asyncio.run(main())
