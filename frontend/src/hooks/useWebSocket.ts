import { useEffect, useRef, useState, useCallback } from 'react';
import { Incident } from '../types';

export type WebSocketStatus = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING';

export interface WebSocketMessage {
  event: 'INCIDENT_CREATED' | 'INCIDENT_UPDATED' | 'PONG' | string;
  data: Incident;
}

interface UseWebSocketOptions {
  onIncidentCreated?: (incident: Incident) => void;
  onIncidentUpdated?: (incident: Incident) => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const [status, setStatus] = useState<WebSocketStatus>('DISCONNECTED');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectCountRef = useRef<number>(0);

  const { onIncidentCreated, onIncidentUpdated } = options;

  const connect = useCallback(() => {
    // Determine WebSocket URL based on location or default port 8001
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || 'localhost';
    const wsUrl = `${protocol}//${host}:8001/ws/incidents`;

    setStatus(reconnectCountRef.current > 0 ? 'RECONNECTING' : 'CONNECTING');

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('CONNECTED');
        reconnectCountRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const payload: WebSocketMessage = JSON.parse(event.data);
          if (payload.event === 'INCIDENT_CREATED' && onIncidentCreated) {
            onIncidentCreated(payload.data);
          } else if (payload.event === 'INCIDENT_UPDATED' && onIncidentUpdated) {
            onIncidentUpdated(payload.data);
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        setStatus('DISCONNECTED');
        wsRef.current = null;
        // Schedule auto-reconnect with exponential backoff (max 10 seconds)
        const delay = Math.min(1000 * Math.pow(1.5, reconnectCountRef.current), 10000);
        reconnectCountRef.current += 1;
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      };

      ws.onerror = (error) => {
        console.warn('WebSocket error observed:', error);
        ws.close();
      };
    } catch (err) {
      console.error('WebSocket initialization error:', err);
      setStatus('DISCONNECTED');
    }
  }, [onIncidentCreated, onIncidentUpdated]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { status };
}
