import { UnifiedWebSocketService } from '../services/unified_websocket_service';

class EnhancedWebSocketManager {
    constructor(authToken, options = {}) {
        this.authToken = authToken;
        this.options = {
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 5,
            timeout: 20000,
            ...options
        };
        
        this.subscribedEncoders = new Set();
        this.messageQueue = [];
        this.connectionState = 'disconnected';
        this.retryCount = 0;
        
        this.initializeSocket();
    }
    
    initializeSocket() {
        this.socket = io({
            auth: {
                token: this.authToken
            },
            ...this.options
        });
        
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to WebSocket server');
            this.connectionState = 'connected';
            this.retryCount = 0;
            this.resubscribeEncoders();
            this.processMessageQueue();
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log('Disconnected:', reason);
            this.connectionState = 'disconnected';
            this.handleDisconnect(reason);
        });
        
        // Error handling
        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            if (error.message === 'Authentication failed') {
                this.handleAuthError();
            } else {
                this.handleConnectionError(error);
            }
        });
        
        this.socket.on('error', (error) => {
            if (error.message === 'Rate limit exceeded') {
                this.handleRateLimit();
            } else {
                console.error('Socket error:', error);
            }
        });
        
        // Encoder-specific events
        this.socket.on('encoder_update', (data) => {
            this.handleEncoderUpdate(data);
        });
        
        this.socket.on('encoder_state_change', (data) => {
            this.handleStateChange(data);
        });
        
        this.socket.on('encoder_alert', (data) => {
            this.handleEncoderAlert(data);
        });
    }
    
    // Subscription management
    async subscribeToEncoder(encoderId) {
        if (this.connectionState !== 'connected') {
            this.queueMessage('subscribe', { encoderId });
            return false;
        }
        
        try {
            const response = await this.emitWithAck('subscribe_encoder', { encoder_id: encoderId });
            if (response.status === 'success') {
                this.subscribedEncoders.add(encoderId);
                this.triggerCallback('onSubscribe', { encoderId, success: true });
                return true;
            }
        } catch (error) {
            console.error(`Failed to subscribe to encoder ${encoderId}:`, error);
            this.triggerCallback('onError', { type: 'subscription', encoderId, error });
        }
        return false;
    }
    
    // Message queue management
    queueMessage(type, data) {
        this.messageQueue.push({ type, data, timestamp: Date.now() });
    }
    
    async processMessageQueue() {
        const now = Date.now();
        const validMessages = this.messageQueue.filter(msg => now - msg.timestamp < 300000); // 5 minutes
        
        for (const message of validMessages) {
            if (message.type === 'subscribe') {
                await this.subscribeToEncoder(message.data.encoderId);
            }
            // Add other message type handling as needed
        }
        
        this.messageQueue = [];
    }
    
    // Error handlers
    handleAuthError() {
        this.connectionState = 'auth_failed';
        this.triggerCallback('onAuthError');
        // Optionally refresh auth token
        this.refreshAuthToken();
    }
    
    handleRateLimit() {
        console.warn('Rate limit reached, implementing backoff...');
        this.triggerCallback('onRateLimit');
        
        // Implement exponential backoff
        const backoffDelay = Math.min(1000 * Math.pow(2, this.retryCount), 30000);
        this.retryCount++;
        
        setTimeout(() => {
            this.retryCount = Math.max(0, this.retryCount - 1);
        }, backoffDelay);
    }
    
    handleConnectionError(error) {
        this.connectionState = 'error';
        this.triggerCallback('onConnectionError', { error });
    }
    
    // Update handlers
    handleEncoderUpdate(data) {
        try {
            // Process encoder metrics and status
            this.updateEncoderMetrics(data);
            
            // Update UI components
            this.triggerCallback('onEncoderUpdate', data);
            
            // Check for warnings/alerts in the data
            if (data.warnings?.length > 0) {
                this.triggerCallback('onWarning', data.warnings);
            }
        } catch (error) {
            console.error('Error handling encoder update:', error);
        }
    }
    
    // Utility methods
    async emitWithAck(event, data, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                reject(new Error('Acknowledgment timeout'));
            }, timeout);
            
            this.socket.emit(event, data, (response) => {
                clearTimeout(timer);
                resolve(response);
            });
        });
    }
    
    triggerCallback(event, data) {
        if (typeof this.options[event] === 'function') {
            this.options[event](data);
        }
    }
    
    // Cleanup
    destroy() {
        this.socket.disconnect();
        this.subscribedEncoders.clear();
        this.messageQueue = [];
    }
}

// Usage example:
const wsManager = new EnhancedWebSocketManager(authToken, {
    onEncoderUpdate: (data) => {
        console.log('Encoder update received:', data);
        updateDashboard(data);
    },
    onAuthError: () => {
        console.log('Authentication failed, redirecting to login...');
        window.location.href = '/login';
    },
    onRateLimit: () => {
        showNotification('Rate limit reached, please wait...');
    },
    onWarning: (warnings) => {
        warnings.forEach(warning => showAlert(warning));
    }
}); 