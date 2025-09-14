"use client";

/**
 * Session Manager Component
 * Advanced session management for development and future multi-user features
 */

import { useState } from "react";
import { resetSession } from "@/app/api";
import { getAnonId, resetAnonId } from "@/lib/anon-id";

interface SessionManagerProps {
  currentClientId: string;
  onSessionChange: (newClientId: string) => void;
  onReset: () => void;
}

export function SessionManager({ currentClientId, onSessionChange, onReset }: SessionManagerProps) {
  const [loading, setLoading] = useState(false);

  const handleClearCurrentSession = async () => {
    setLoading(true);
    try {
      await resetSession(currentClientId);
      onReset();
      console.log("Current session cleared successfully");
    } catch (err) {
      console.error("Failed to clear session:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSession = () => {
    const newId = resetAnonId();
    onSessionChange(newId);
    onReset();
    console.log("Created new session:", newId);
  };

  const copySessionId = () => {
    navigator.clipboard.writeText(currentClientId);
    console.log("Session ID copied to clipboard");
  };

  return (
    <div className="session-manager">
      <details className="session-details">
        <summary className="session-summary">Session Management</summary>
        
        <div className="session-content">
          <div className="session-info">
            <p><strong>Current Session:</strong></p>
            <code className="session-id" onClick={copySessionId} title="Click to copy">
              {currentClientId.slice(0, 8)}...
            </code>
          </div>

          <div className="session-actions">
            <button 
              onClick={handleClearCurrentSession}
              disabled={loading}
              className="action-button clear-button"
            >
              {loading ? "Clearing..." : "Clear This Session"}
            </button>

            <button 
              onClick={handleNewSession}
              className="action-button new-button"
            >
              Start New Session
            </button>
          </div>

          <div className="session-help">
            <p><small>
              <strong>Clear Session:</strong> Removes all data but keeps same ID<br/>
              <strong>New Session:</strong> Creates completely new session ID
            </small></p>
          </div>
        </div>
      </details>

      <style jsx>{`
        .session-manager {
          margin-top: 1rem;
          border-top: 1px solid #e5e7eb;
          padding-top: 1rem;
        }

        .session-details {
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          padding: 0.5rem;
        }

        .session-summary {
          cursor: pointer;
          font-weight: 500;
          color: #6b7280;
          font-size: 0.875rem;
        }

        .session-content {
          margin-top: 1rem;
          space-y: 1rem;
        }

        .session-info {
          margin-bottom: 1rem;
        }

        .session-id {
          background: #f3f4f6;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-family: monospace;
          cursor: pointer;
          font-size: 0.75rem;
        }

        .session-id:hover {
          background: #e5e7eb;
        }

        .session-actions {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .action-button {
          padding: 0.5rem 1rem;
          border-radius: 4px;
          font-size: 0.875rem;
          cursor: pointer;
          border: 1px solid;
          transition: all 0.2s;
        }

        .clear-button {
          background: #fef2f2;
          color: #dc2626;
          border-color: #fecaca;
        }

        .clear-button:hover:not(:disabled) {
          background: #fee2e2;
        }

        .new-button {
          background: #f0f9ff;
          color: #0369a1;
          border-color: #bae6fd;
        }

        .new-button:hover {
          background: #e0f2fe;
        }

        .action-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .session-help {
          font-size: 0.75rem;
          color: #6b7280;
        }
      `}</style>
    </div>
  );
} 