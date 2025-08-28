// Chat functionality for CUNY AI Assistant
class CUNYChatbot {
    constructor() {
        this.conversationHistory = [];
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCampusInfo();
    }

    bindEvents() {
        // Send button click
        document.querySelector('.send-button').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key press
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Clear chat button
        document.querySelector('.clear-chat').addEventListener('click', () => {
            this.clearChat();
        });
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message || this.isLoading) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        messageInput.value = '';

        // Show loading indicator
        this.showLoading();

        try {
            // Prepare conversation history for API
            const history = this.conversationHistory.map(msg => ({
                role: msg.type,
                content: msg.content
            }));

            // Send to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: history
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Add bot response to chat
                this.addMessage(data.response, 'bot');
            } else {
                throw new Error(data.error || 'Failed to get response');
            }

        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error. Please try again or contact support.', 'bot');
        } finally {
            this.hideLoading();
        }
    }

    addMessage(content, type) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (type === 'bot') {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        } else {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        }

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);

        // Store in conversation history
        this.conversationHistory.push({
            type: type,
            content: content,
            timestamp: new Date().toISOString()
        });

        // Scroll to bottom
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Convert URLs to clickable links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        content = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        
        // Convert line breaks to <br> tags
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showLoading() {
        this.isLoading = true;
        document.getElementById('loadingIndicator').style.display = 'flex';
        document.querySelector('.send-button').disabled = true;
    }

    hideLoading() {
        this.isLoading = false;
        document.getElementById('loadingIndicator').style.display = 'none';
        document.querySelector('.send-button').disabled = false;
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        
        // Keep only the welcome message
        const welcomeMessage = chatMessages.querySelector('.bot-message');
        chatMessages.innerHTML = '';
        if (welcomeMessage) {
            chatMessages.appendChild(welcomeMessage);
        }

        // Clear conversation history
        this.conversationHistory = [];
    }

    async loadCampusInfo() {
        try {
            const response = await fetch('/api/campus-info');
            const data = await response.json();
            
            // Update campus info in sidebar
            const campusInfo = document.getElementById('campusInfo');
            if (campusInfo && data.campuses) {
                campusInfo.innerHTML = `
                    <div class="info-item">
                        <strong>Campuses:</strong> ${data.campuses.length} colleges across NYC
                    </div>
                    <div class="info-item">
                        <strong>Students:</strong> ${data.total_students}
                    </div>
                    <div class="info-item">
                        <strong>Founded:</strong> ${data.founded}
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading campus info:', error);
        }
    }

    async askQuickQuestion(question) {
        // Add the question to the input and send it
        const messageInput = document.getElementById('messageInput');
        messageInput.value = question;
        this.sendMessage();
    }
}

// Global functions for HTML onclick handlers
function sendMessage() {
    if (window.chatbot) {
        window.chatbot.sendMessage();
    }
}

function askQuestion(question) {
    if (window.chatbot) {
        window.chatbot.askQuickQuestion(question);
    }
}

function clearChat() {
    if (window.chatbot) {
        window.chatbot.clearChat();
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new CUNYChatbot();
});

// Add some interactive features
document.addEventListener('DOMContentLoaded', () => {
    // Add typing indicator
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.querySelector('.send-button');

    messageInput.addEventListener('input', () => {
        if (messageInput.value.trim()) {
            sendButton.style.opacity = '1';
        } else {
            sendButton.style.opacity = '0.6';
        }
    });

    // Add smooth scrolling for chat messages
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.style.scrollBehavior = 'smooth';

    // Add hover effects for quick questions
    const quickQuestions = document.querySelectorAll('.quick-question');
    quickQuestions.forEach(question => {
        question.addEventListener('mouseenter', () => {
            question.style.transform = 'translateY(-2px)';
        });
        
        question.addEventListener('mouseleave', () => {
            question.style.transform = 'translateY(0)';
        });
    });

    // Add focus styles for input
    messageInput.addEventListener('focus', () => {
        messageInput.parentElement.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
    });

    messageInput.addEventListener('blur', () => {
        messageInput.parentElement.style.boxShadow = 'none';
    });
});

// Add error handling for network issues
window.addEventListener('online', () => {
    console.log('Connection restored');
    // Could add a notification here
});

window.addEventListener('offline', () => {
    console.log('Connection lost');
    // Could add a notification here
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to send message
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
    
    // Escape to clear input
    if (e.key === 'Escape') {
        const messageInput = document.getElementById('messageInput');
        messageInput.value = '';
        messageInput.blur();
    }
});
