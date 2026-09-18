import { env } from "@/config/env";
import type { SystemState } from "@/types/system.types";

export type WebSocketConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';
export type MessageCallback = (data: SystemState) => void;
export type StateChangeCallback = (state: WebSocketConnectionState) => void;

interface WSOptions {
  url?: string;
  reconnectInterval?: number;
  maxReconnectInterval?: number;
  reconnectDecay?: number;
}

/**
 * Generic WebSocket client handling native connection lifecycle and bounded reconnects.
 * It is completely agnostic to the SH-305 domain and message protocol.
 */
export class WebSocketClient {
  private url: string;
  private ws: WebSocket | null = null;
  private reconnectTimeout: number | null = null;
  
  private reconnectInterval: number;
  private maxReconnectInterval: number;
  private reconnectDecay: number;
  private currentReconnectInterval: number;
  
  private state: WebSocketConnectionState = 'disconnected';
  
  private messageListeners: Set<MessageCallback> = new Set();
  private stateListeners: Set<StateChangeCallback> = new Set();
  
  private intentionalDisconnect = false;

  constructor(options: WSOptions = {}) {
    this.url = options.url || env.WS_BASE_URL;
    this.reconnectInterval = options.reconnectInterval || 1000;
    this.maxReconnectInterval = options.maxReconnectInterval || 30000;
    this.reconnectDecay = options.reconnectDecay || 1.5;
    this.currentReconnectInterval = this.reconnectInterval;
  }

  public connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }
    
    this.intentionalDisconnect = false;
    this.setState('connecting');
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      this.setState('connected');
      this.currentReconnectInterval = this.reconnectInterval;
    };

    this.ws.onmessage = (event) => {
      // Parse basic JSON for the transport layer, but leave the structure uninterpreted
      try {
        const data = JSON.parse(event.data);
        this.notifyMessageListeners(data);
      } catch {
        // If not JSON, pass as is
        this.notifyMessageListeners(event.data);
      }
    };

    this.ws.onclose = () => {
      if (this.state !== 'error') {
        this.setState('disconnected');
      }
      this.ws = null;
      if (!this.intentionalDisconnect) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = () => {
      this.setState('error');
    };
  }

  public disconnect(): void {
    this.intentionalDisconnect = true;
    if (this.reconnectTimeout !== null) {
      window.clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setState('disconnected');
  }

  public subscribe(callback: MessageCallback): () => void {
    this.messageListeners.add(callback);
    return () => this.messageListeners.delete(callback);
  }
  
  public onStateChange(callback: StateChangeCallback): () => void {
    this.stateListeners.add(callback);
    return () => this.stateListeners.delete(callback);
  }

  public send(data: unknown): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const payload = typeof data === 'string' ? data : JSON.stringify(data);
      this.ws.send(payload);
    }
  }

  private notifyMessageListeners(data: SystemState): void {
    this.messageListeners.forEach(listener => listener(data));
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout !== null) {
      return;
    }
    
    this.reconnectTimeout = window.setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect();
    }, this.currentReconnectInterval);
    
    // Apply bounded exponential backoff
    this.currentReconnectInterval = Math.min(
      this.currentReconnectInterval * this.reconnectDecay,
      this.maxReconnectInterval
    );
  }

  private setState(newState: WebSocketConnectionState): void {
    if (this.state !== newState) {
      this.state = newState;
      this.stateListeners.forEach(listener => listener(this.state));
    }
  }
  
  public getState(): WebSocketConnectionState {
    return this.state;
  }
}

// Global generic transport singleton
export const wsClient = new WebSocketClient();
