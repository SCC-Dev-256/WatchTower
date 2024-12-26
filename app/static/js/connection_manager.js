class ConnectionManager {
    constructor(options = {}) {
        this.baseDelay = options.baseDelay || 1000;
        this.maxDelay = options.maxDelay || 30000;
        this.maxAttempts = options.maxAttempts || 10;
        this.jitter = options.jitter || 0.1;
        
        this.attemptCount = 0;
        this.currentDelay = this.baseDelay;
    }
    
    calculateNextDelay() {
        // Exponential backoff with jitter
        const exponentialDelay = Math.min(
            this.maxDelay,
            this.baseDelay * Math.pow(2, this.attemptCount)
        );
        
        // Add random jitter (±10% by default)
        const jitterRange = exponentialDelay * this.jitter;
        const jitter = (Math.random() * 2 - 1) * jitterRange;
        
        return exponentialDelay + jitter;
    }
    
    async attemptReconnection(connectFunc) {
        while (this.attemptCount < this.maxAttempts) {
            try {
                await connectFunc();
                // Reset on successful connection
                this.reset();
                return true;
            } catch (error) {
                this.attemptCount++;
                const delay = this.calculateNextDelay();
                console.log(`Reconnection attempt ${this.attemptCount} failed. Waiting ${delay}ms`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        return false;
    }
    
    reset() {
        this.attemptCount = 0;
        this.currentDelay = this.baseDelay;
    }
} 