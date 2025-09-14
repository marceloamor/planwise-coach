"use client";

/**
 * Chat Panel Component
 * Main interface for chatting with the AI running coach
 */

import { useState, useEffect, useRef } from "react";
import { sendChat, fetchPlan, resetSession, PlanDoc, ChatResponse } from "@/app/api";
import { getAnonId, resetAnonId } from "@/lib/anon-id";
import { PlanCard } from "./plan-card";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatPanel() {
  // State
  const [clientId, setClientId] = useState<string>("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentPlan, setCurrentPlan] = useState<PlanDoc | null>(null);
  const [planVersion, setPlanVersion] = useState<number | null>(null);
  const [planUpdatedAt, setPlanUpdatedAt] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize client ID and load existing plan
  useEffect(() => {
    const id = getAnonId();
    console.log("🔍 Initializing with client ID:", id);
    setClientId(id);
    
    // Load existing plan if any
    console.log("📡 Fetching existing plan...");
    fetchPlan(id)
      .then((response) => {
        console.log("📋 Plan fetch response:", response);
        if (response.plan) {
          console.log("✅ Plan found, setting state:", {
            goal: response.plan.meta.goal,
            weeks: Object.keys(response.plan.weeks).length,
            version: response.version
          });
          setCurrentPlan(response.plan);
          setPlanVersion(response.version || null);
          setPlanUpdatedAt(response.created_at || null);
        } else {
          console.log("📭 No existing plan found");
        }
      })
      .catch((err) => {
        console.warn("❌ Could not load existing plan:", err);
      });
  }, []);

  // Watch for client ID changes and reload plan
  useEffect(() => {
    if (clientId && clientId !== "ssr-placeholder") {
      console.log("🔄 Client ID changed, fetching plan for:", clientId);
      fetchPlan(clientId)
        .then((response) => {
          if (response.plan) {
            console.log("📋 Plan found for new client ID:", response.plan.meta.goal);
            setCurrentPlan(response.plan);
            setPlanVersion(response.version || null);
            setPlanUpdatedAt(response.created_at || null);
          } else {
            console.log("📭 No plan for new client ID");
            setCurrentPlan(null);
            setPlanVersion(null);
            setPlanUpdatedAt(null);
          }
        })
        .catch((err) => {
          console.warn("❌ Error fetching plan for new client ID:", err);
        });
    }
  }, [clientId]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);
    setLoading(true);

    // Add user message to chat
    const newUserMessage: ChatMessage = {
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newUserMessage]);

    try {
      // Send to backend
      const response: ChatResponse = await sendChat(clientId, userMessage);

      // Add assistant response to chat
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Update plan if it was updated
      if (response.plan_updated && response.plan) {
        console.log("📋 Plan updated from chat response:", {
          goal: response.plan.meta.goal,
          weeks: Object.keys(response.plan.weeks).length
        });
        setCurrentPlan(response.plan);
        // Get updated plan details
        const planResponse = await fetchPlan(clientId);
        setPlanVersion(planResponse.version || null);
        setPlanUpdatedAt(planResponse.created_at || null);
      } else if (response.plan) {
        console.log("📋 Plan received but not marked as updated:", {
          goal: response.plan.meta.goal,
          weeks: Object.keys(response.plan.weeks).length
        });
        // Even if not marked as updated, show the plan
        setCurrentPlan(response.plan);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // Clear conversation and plan
  const handleReset = async () => {
    console.log("🔄 Starting reset process...");
    console.log("Current state:", { 
      clientId, 
      hasCurrentPlan: !!currentPlan, 
      planVersion, 
      messagesCount: messages.length 
    });
    
    setLoading(true);
    setError(null);
    
    try {
      // ALWAYS clear frontend state first
      console.log("🗑️ Clearing frontend state...");
      setMessages([]);
      setCurrentPlan(null);
      setPlanVersion(null);
      setPlanUpdatedAt(null);
      
      // Try to clear backend data
      console.log("🌐 Attempting backend reset...");
      const resetResult = await resetSession(clientId);
      console.log("✅ Backend reset successful:", resetResult);
      
      // Verify backend is actually cleared
      console.log("🔍 Verifying backend clear...");
      const verifyResponse = await fetchPlan(clientId);
      if (verifyResponse.plan) {
        console.error("❌ Plan still exists after reset!", verifyResponse.plan);
        throw new Error("Backend reset failed - plan still exists");
      } else {
        console.log("✅ Backend verification: No plan found");
      }
      
    } catch (err) {
      console.warn("❌ Reset failed, creating new client ID:", err);
      
      // Fallback: Generate completely new client ID
      const newId = resetAnonId();
      console.log("🆕 New client ID generated:", newId);
      setClientId(newId);
      
      // Clear state again to be sure
      setMessages([]);
      setCurrentPlan(null);
      setPlanVersion(null);
      setPlanUpdatedAt(null);
    } finally {
      setLoading(false);
      console.log("🏁 Reset process complete");
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <h1>AI Running Coach</h1>
        <p className="subtitle">
          Chat to create a personalised training plan. Then iterate and improve it.
        </p>
        {(messages.length > 0 || currentPlan) && (
          <button 
            onClick={handleReset} 
            className="reset-button"
            title="Clear all conversations and plans to start fresh"
            disabled={loading}
          >
            {loading ? "Clearing..." : "Start Over"}
          </button>
        )}
      </div>

      {/* Welcome message */}
      {messages.length === 0 && (
        <div className="welcome-message">
          <h3>👋 Welcome!</h3>
          <p>I'm your AI running coach. Tell me about your goals and I'll create a personalised training plan for you.</p>
          <div className="example-prompts">
            <p><strong>Try asking:</strong></p>
            <ul>
              <li>"Create a 12-week half marathon plan for a beginner"</li>
              <li>"I run 30km/week, want to improve my 5K time"</li>
              <li>"8-week base building plan, 4 days per week"</li>
            </ul>
          </div>
        </div>
      )}

      {/* Messages */}
      {messages.length > 0 && (
        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <div className="message-header">
                  <span className="message-role">
                    {message.role === "user" ? "You" : "Coach"}
                  </span>
                  <span className="message-time">
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                </div>
                <div className="message-text">
                  {message.content}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Input form */}
      <form onSubmit={handleSubmit} className="chat-form">
        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}
        
        <div className="input-container">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              messages.length === 0 
                ? "Tell me your running goals (e.g., '12-week half marathon plan')" 
                : "Ask me to modify your plan or ask questions..."
            }
            disabled={loading}
            className="chat-input"
            autoFocus
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="send-button"
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>
      </form>

      {/* Plan display */}
      {currentPlan && (
        <PlanCard 
          plan={currentPlan} 
          version={planVersion || undefined}
          updatedAt={planUpdatedAt || undefined}
        />
      )}

      <style jsx>{`
        .chat-container {
          max-width: 900px;
          margin: 0 auto;
          padding: 1rem;
          font-family: system-ui, -apple-system, sans-serif;
        }
        
        .chat-header {
          text-align: center;
          margin-bottom: 2rem;
          position: relative;
        }
        
        .chat-header h1 {
          margin: 0 0 0.5rem 0;
          color: #1f2937;
          font-size: 2rem;
          font-weight: 700;
        }
        
        .subtitle {
          color: #6b7280;
          margin: 0 0 1rem 0;
          font-size: 1.1rem;
        }
        
        .reset-button {
          position: absolute;
          top: 0;
          right: 0;
          background: #f3f4f6;
          border: 1px solid #d1d5db;
          color: #6b7280;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.875rem;
          transition: all 0.2s;
        }
        
        .reset-button:hover {
          background: #e5e7eb;
          color: #374151;
        }
        
        .welcome-message {
          background: #f0f9ff;
          border: 1px solid #0ea5e9;
          border-radius: 8px;
          padding: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .welcome-message h3 {
          margin: 0 0 1rem 0;
          color: #0369a1;
        }
        
        .welcome-message p {
          margin: 0 0 1rem 0;
          color: #374151;
        }
        
        .example-prompts {
          margin-top: 1rem;
        }
        
        .example-prompts p {
          margin: 0 0 0.5rem 0;
          font-weight: 600;
          color: #1f2937;
        }
        
        .example-prompts ul {
          margin: 0;
          padding-left: 1.5rem;
          color: #4b5563;
        }
        
        .example-prompts li {
          margin-bottom: 0.25rem;
        }
        
        .messages-container {
          max-height: 500px;
          overflow-y: auto;
          margin-bottom: 2rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 1rem;
          background: #fafafa;
        }
        
        .message {
          margin-bottom: 1rem;
        }
        
        .message:last-child {
          margin-bottom: 0;
        }
        
        .message.user .message-content {
          background: #3b82f6;
          color: white;
          margin-left: 2rem;
        }
        
        .message.assistant .message-content {
          background: white;
          color: #1f2937;
          margin-right: 2rem;
          border: 1px solid #e5e7eb;
        }
        
        .message-content {
          padding: 1rem;
          border-radius: 8px;
        }
        
        .message-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
        }
        
        .message.user .message-header {
          color: rgba(255, 255, 255, 0.8);
        }
        
        .message.assistant .message-header {
          color: #6b7280;
        }
        
        .message-role {
          font-weight: 600;
        }
        
        .message-text {
          line-height: 1.6;
          white-space: pre-wrap;
        }
        
        .chat-form {
          position: sticky;
          bottom: 0;
          background: white;
          padding: 1rem 0;
          border-top: 1px solid #e5e7eb;
          margin-top: 2rem;
        }
        
        .error-message {
          background: #fef2f2;
          color: #dc2626;
          padding: 0.75rem;
          border-radius: 6px;
          border: 1px solid #fecaca;
          margin-bottom: 1rem;
        }
        
        .input-container {
          display: flex;
          gap: 0.75rem;
        }
        
        .chat-input {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-size: 1rem;
          outline: none;
          transition: border-color 0.2s;
        }
        
        .chat-input:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .chat-input:disabled {
          background: #f9fafb;
          color: #6b7280;
          cursor: not-allowed;
        }
        
        .send-button {
          padding: 0.75rem 1.5rem;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          min-width: 120px;
        }
        
        .send-button:hover:not(:disabled) {
          background: #2563eb;
        }
        
        .send-button:disabled {
          background: #9ca3af;
          cursor: not-allowed;
        }
        
        @media (max-width: 768px) {
          .chat-container {
            padding: 0.5rem;
          }
          
          .reset-button {
            position: static;
            margin-top: 1rem;
          }
          
          .message.user .message-content {
            margin-left: 1rem;
          }
          
          .message.assistant .message-content {
            margin-right: 1rem;
          }
          
          .input-container {
            flex-direction: column;
            gap: 0.5rem;
          }
        }
      `}</style>
    </div>
  );
} 