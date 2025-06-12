import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, RefreshCw, AlertCircle } from 'lucide-react';

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant' | 'system';
  timestamp: Date;
  status: 'sending' | 'sent' | 'error';
  error?: string;
}

interface ChatInterfaceProps {
  workflowId?: string;
  onSendMessage: (message: string) => Promise<void>;
  messages?: Message[];
  isProcessing?: boolean;
  className?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  workflowId,
  onSendMessage,
  messages: externalMessages = [],
  isProcessing = false,
  className = '',
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [localMessages, setLocalMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Combine external messages with local messages
  const allMessages = [...externalMessages, ...localMessages].sort(
    (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
  );

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [allMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isProcessing) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      status: 'sending',
    };
    
    setLocalMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    
    try {
      await onSendMessage(inputMessage);
      
      // Update message status to sent
      setLocalMessages(prev =>
        prev.map(msg =>
          msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
        )
      );
    } catch (error) {
      // Update message status to error
      setLocalMessages(prev =>
        prev.map(msg =>
          msg.id === userMessage.id
            ? {
                ...msg,
                status: 'error',
                error: error instanceof Error ? error.message : 'Failed to send message',
              }
            : msg
        )
      );
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const getMessageAvatar = (sender: string) => {
    switch (sender) {
      case 'user':
        return <User className="w-5 h-5 text-blue-500" />;
      case 'assistant':
        return <Bot className="w-5 h-5 text-purple-500" />;
      default:
        return <div className="w-5 h-5 rounded-full bg-gray-300" />;
    }
  };

  return (
    <div className={`flex flex-col h-full bg-white rounded-lg border border-gray-200 overflow-hidden ${className}`}>
      {/* Chat header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h3 className="font-medium text-gray-900">
          {workflowId ? `Chat - Workflow #${workflowId.slice(0, 8)}` : 'Chat'}
        </h3>
        <div className="flex items-center space-x-2">
          {isProcessing && (
            <div className="flex items-center text-sm text-gray-500">
              <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
              Processing...
            </div>
          )}
        </div>
      </div>
      
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {allMessages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <Bot className="w-10 h-10 mx-auto mb-2 text-gray-300" />
              <p>How can I help you with this workflow?</p>
            </div>
          </div>
        ) : (
          allMessages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3/4 rounded-lg p-3 ${
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none'
                }`}
              >
                <div className="flex items-start space-x-2">
                  {message.sender !== 'user' && (
                    <div className="mt-0.5">
                      {getMessageAvatar(message.sender)}
                    </div>
                  )}
                  <div>
                    <div className="whitespace-pre-wrap break-words">
                      {message.content}
                    </div>
                    {message.error && (
                      <div className="mt-1 flex items-center text-xs text-red-500">
                        <AlertCircle className="w-3.5 h-3.5 mr-1" />
                        {message.error}
                      </div>
                    )}
                  </div>
                  {message.sender === 'user' && (
                    <div className="mt-0.5">
                      {getMessageAvatar(message.sender)}
                    </div>
                  )}
                </div>
                <div className="mt-1 text-xs opacity-70 text-right">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Message input */}
      <form onSubmit={handleSendMessage} className="border-t border-gray-200 p-3 bg-gray-50">
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={1}
              disabled={isProcessing}
            />
          </div>
          <button
            type="submit"
            disabled={!inputMessage.trim() || isProcessing}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
            title="Send message"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;
