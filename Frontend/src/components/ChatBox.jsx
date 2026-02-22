import { useState, useRef, useEffect } from 'react';
import { createSession, sendMessage, getSessionHistory } from '../services/api';
import './ChatBox.css';

const ChatBox = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            text: "Hello! I'm PlanIT, your AI planning assistant. How can I help you organize your day?",
            sender: 'bot',
            timestamp: new Date()
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [isThinking, setIsThinking] = useState(false); // For agent thinking state

    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Initialize session
    useEffect(() => {
        const initSession = async () => {
            try {
                // Check local storage for existing session
                const savedSessionId = localStorage.getItem('planit_session_id');

                if (savedSessionId) {
                    // Verify session is valid (and get history)
                    try {
                        const history = await getSessionHistory(savedSessionId);
                        setSessionId(savedSessionId);

                        // Optional: Load history into messages if desired
                        // For now we just keep the welcome message and continue
                        console.log("Resumed session:", savedSessionId);
                        return;
                    } catch (e) {
                        console.warn("Saved session expired or invalid, creating new one");
                        localStorage.removeItem('planit_session_id');
                    }
                }

                // Create new session
                const newSession = await createSession();
                setSessionId(newSession.session_id);
                localStorage.setItem('planit_session_id', newSession.session_id);
                console.log("Created new session:", newSession.session_id);
            } catch (error) {
                console.error("Failed to initialize chat session:", error);
                setMessages(prev => [...prev, {
                    id: Date.now(),
                    text: "⚠️ Connection error: Unable to connect to backend service.",
                    sender: 'bot',
                    isError: true,
                    timestamp: new Date()
                }]);
            }
        };

        initSession();
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping, isThinking]);

    const handleSend = async () => {
        if (!inputValue.trim() || !sessionId) return;

        const userText = inputValue;
        const userMessage = {
            id: Date.now(),
            text: userText,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsTyping(true);
        setIsThinking(true);

        try {
            const response = await sendMessage(sessionId, userText);

            const botMessage = {
                id: Date.now() + 1,
                text: response.response,
                sender: 'bot',
                timestamp: new Date(),
                toolCalls: response.tool_calls // Can be used to show "Checked availability..." etc.
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error("Chat error:", error);
            const errorMessage = {
                id: Date.now() + 1,
                text: "Sorry, I encountered an error. Please try again.",
                sender: 'bot',
                isError: true,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsTyping(false);
            setIsThinking(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.style.height = 'auto';
            inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
        }
    }, [inputValue]);

    const formatTime = (date) => {
        return new Date(date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="chatbox-container">
            <div className="chatbox-header">
                <div className="header-content">
                    <div className="bot-avatar">
                        <div className="avatar-icon">🤖</div>
                        <div className={`status-indicator ${sessionId ? 'online' : 'offline'}`}></div>
                    </div>
                    <div className="header-info">
                        <h3>PlanIT Assistant</h3>
                        <p className="status-text">
                            {sessionId ? 'Powered by Agentic AI' : 'Connecting...'}
                        </p>
                    </div>
                </div>
                <div className="header-actions">
                    <button className="icon-btn" title="Settings">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="3" />
                            <path d="M12 1v6m0 6v6m5.196-15.196l-4.242 4.242m-5.908 5.908l-4.242 4.242M23 12h-6m-6 0H1m15.196 5.196l-4.242-4.242m-5.908-5.908l-4.242-4.242" />
                        </svg>
                    </button>
                </div>
            </div>

            <div className="chatbox-messages">
                {messages.map((message, index) => (
                    <div
                        key={message.id}
                        className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
                        style={{ animationDelay: `${0}s` }}
                    >
                        {message.sender === 'bot' && (
                            <div className="message-avatar">🤖</div>
                        )}
                        <div className="message-content">
                            <div className="message-bubble">
                                <p style={{ whiteSpace: 'pre-line' }}>{message.text}</p>
                            </div>

                            {/* Display tool usage if available (Agentic transparency) */}
                            {message.toolCalls && message.toolCalls.length > 0 && (
                                <div className="tool-usage">
                                    <small> Used: {message.toolCalls.map(t => t.tool).join(", ")}</small>
                                </div>
                            )}

                            <span className="message-time">{formatTime(message.timestamp)}</span>
                        </div>
                        {message.sender === 'user' && (
                            <div className="message-avatar user-avatar">👤</div>
                        )}
                    </div>
                ))}

                {(isTyping || isThinking) && (
                    <div className="message bot typing-indicator">
                        <div className="message-avatar">🤖</div>
                        <div className="message-content">
                            <div className="message-bubble thinking-bubble">
                                {isThinking && <span className="thinking-text">Thinking...</span>}
                                <div className="typing-dots">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <div className="chatbox-input">
                <div className="input-container">
                    <button className="icon-btn attachment-btn" title="Attach file">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
                        </svg>
                    </button>

                    <textarea
                        ref={inputRef}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder={sessionId ? "Type your message..." : "Connecting..."}
                        rows="1"
                        className="message-input"
                        disabled={!sessionId || isTyping}
                    />

                    <button
                        className="send-btn"
                        onClick={handleSend}
                        disabled={!inputValue.trim() || !sessionId || isTyping}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="22" y1="2" x2="11" y2="13" />
                            <polygon points="22 2 15 22 11 13 2 9 22 2" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatBox;
