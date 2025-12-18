import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { analyticsAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';

const MessageBubble = React.memo(function MessageBubble({ message }) {
  return (
    <motion.div
      initial={false}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-6`}
    >
      <div className="flex items-end space-x-3 max-w-[85%]">
        {message.role === 'assistant' && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.3 }}
            className="w-10 h-10 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-xl"
          >
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </motion.div>
        )}
        <div
          className={`relative px-6 py-4 rounded-2xl shadow-md ${
            message.role === 'user'
              ? 'bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 text-white border border-blue-400/30'
              : 'bg-black/40 border border-white/20 text-gray-100'
          }`}
        >
          {message.role === 'user' && (
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-400 rounded-full animate-pulse shadow-lg shadow-blue-400/50"></div>
          )}
          {message.role === 'user' ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap font-medium">{message.content}</p>
          ) : (
            <div className="text-sm prose prose-sm prose-invert max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>
        {message.role === 'user' && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.3 }}
            className="w-10 h-10 bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-xl"
          >
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
});

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [storeId, setStoreId] = useState('auto-shopai.myshopify.com');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleInputChange = useCallback((e) => {
    setInput(e.target.value);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await analyticsAPI.askQuestion(storeId, input.trim());
      const botMessage = { 
        role: 'assistant', 
        content: response.answer || response.response || 'Sorry, I could not process your request.' 
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = { 
        role: 'assistant', 
        content: `Error: ${error.error || 'Something went wrong. Please try again.'}` 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };
  // MessageBubble is defined at module scope above to avoid re-creation per render

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 relative overflow-hidden">
      {/* Premium animated background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 right-0 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-violet-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '4s' }}></div>
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent"></div>
      </div>
      
      <div className="relative z-10 max-w-6xl mx-auto p-8 h-screen flex flex-col">
        {/* Premium Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="bg-black/30 backdrop-blur-2xl rounded-3xl shadow-2xl border border-white/10 p-8 mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div
                className="w-16 h-16 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 rounded-2xl flex items-center justify-center shadow-2xl relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-t from-white/20 to-transparent"></div>
                <svg className="w-8 h-8 text-white relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent mb-2">Shopify Analytics Assistant</h1>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <p className="text-gray-300 text-sm font-medium">Powered by Advanced AI</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative group">
                <input
                  type="text"
                  value={storeId}
                  onChange={(e) => setStoreId(e.target.value)}
                  placeholder="Store domain"
                  className="pl-5 pr-12 py-4 bg-black/20 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-400/50 focus:border-amber-400/50 backdrop-blur-xl transition-all duration-300 font-medium w-64"
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <svg className="w-5 h-5 text-gray-400 group-hover:text-amber-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Messages Container */}
        <div
          className="flex-1 bg-black/30 rounded-3xl shadow-2xl border border-white/10 p-6 mb-6 overflow-hidden flex flex-col"
        >
          <div className="flex-1 overflow-y-auto pr-4 space-y-2">
            <AnimatePresence initial={false}>
              {messages.length === 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, ease: 'easeOut' }}
                  className="relative text-center py-20"
                >
                  <div className="pointer-events-none absolute inset-0">
                    <div className="absolute -top-10 left-1/2 -translate-x-1/2 w-72 h-72 rounded-full bg-violet-500/20 blur-3xl"></div>
                    <div className="absolute bottom-0 right-1/4 w-56 h-56 rounded-full bg-indigo-500/10 blur-3xl"></div>
                  </div>
                  <motion.div
                    animate={{ y: [0, -6, 0] }}
                    transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
                    className="w-20 h-20 bg-gradient-to-br from-violet-500 to-indigo-600 rounded-2xl ring-1 ring-white/20 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-violet-600/30 relative"
                  >
                    <div className="absolute inset-0 bg-gradient-to-t from-white/20 to-transparent rounded-2xl"></div>
                    <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </motion.div>
                  <h3 className="text-3xl font-extrabold bg-gradient-to-r from-violet-200 via-white to-violet-200 bg-clip-text text-transparent mb-2">Welcome to Analytics Assistant</h3>
                  <p className="text-violet-200/80 mb-10">Ask me anything about your Shopify store</p>
                  <div className="flex flex-wrap justify-center gap-3">
                    {['Show me sales trends', 'Top products this month', 'Customer analytics', 'Revenue comparison'].map((suggestion, index) => (
                      <motion.button
                        key={suggestion}
                        onClick={() => setInput(suggestion)}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.08 * index, duration: 0.25 }}
                        className="px-5 py-2.5 rounded-full bg-white/5 border border-white/10 text-white/90 hover:bg-white/10 hover:border-white/20 focus:outline-none focus:ring-2 focus:ring-violet-500/30 transition-all"
                      >
                        {suggestion}
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              )}
              {messages.map((message, index) => (
                <MessageBubble key={`message-${index}-${message.role}`} message={message} />
              ))}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start mb-6"
                >
                  <div className="flex items-end space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-r from-violet-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div className="bg-white/95 backdrop-blur-sm border border-gray-100/80 rounded-2xl px-5 py-4 shadow-lg">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                 </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Form */}
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3, ease: 'easeOut' }}
          className="bg-black/40 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 p-6"
        >
          <div className="flex space-x-3">
            <div className="flex-1 relative">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={handleInputChange}
                placeholder="Ask about your store analytics..."
                className="w-full pl-5 pr-12 py-4 bg-black/60 backdrop-blur-sm border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-400/50 focus:border-amber-400/50 transition-all duration-200 font-medium"
                disabled={isLoading}
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
            </div>
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-8 py-4 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 text-white rounded-2xl hover:from-amber-500 hover:via-orange-600 hover:to-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-3 shadow-xl font-bold"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <span>Send</span>
            </button>
          </div>
        </motion.form>
      </div>
    </div>
  );
};

export default ChatBot;
