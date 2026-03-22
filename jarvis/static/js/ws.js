/**
 * ULTRON — WebSocket Communication
 * 
 * Handles bidirectional communication with the Python backend.
 * Auto-reconnects on disconnect.
 */

export class WS {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.connected = false;
    this.reconnectInterval = null;
    
    // Callbacks
    this.onMessage = null;
    this.onConnect = null;
    this.onDisconnect = null;
    
    this.connect();
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);
    } catch (e) {
      this._scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.connected = true;
      if (this.reconnectInterval) {
        clearInterval(this.reconnectInterval);
        this.reconnectInterval = null;
      }
      if (this.onConnect) this.onConnect();
    };

    this.ws.onclose = () => {
      this.connected = false;
      if (this.onDisconnect) this.onDisconnect();
      this._scheduleReconnect();
    };

    this.ws.onerror = () => {};

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (this.onMessage) this.onMessage(data);
      } catch (e) {
        console.warn('[WS] Parse error:', e);
      }
    };
  }

  send(type, data = {}) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ type, ...data }));
  }

  _scheduleReconnect() {
    if (this.reconnectInterval) return;
    this.reconnectInterval = setInterval(() => {
      if (!this.connected) this.connect();
    }, 3000);
  }
}
