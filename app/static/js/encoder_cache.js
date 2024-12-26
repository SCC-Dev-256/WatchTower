class EncoderCache {
    constructor(options = {}) {
        this.maxAge = options.maxAge || 5000; // 5 seconds
        this.maxSize = options.maxSize || 100; // Maximum number of cached items
        this.cache = new Map();
        this.metrics = {
            hits: 0,
            misses: 0,
            updates: 0
        };
    }
    
    set(encoderId, data) {
        // Implement LRU eviction if cache is full
        if (this.cache.size >= this.maxSize) {
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
        }
        
        this.cache.set(encoderId, {
            data: data,
            timestamp: Date.now(),
            updateCount: 0
        });
        this.metrics.updates++;
    }
    
    get(encoderId) {
        const entry = this.cache.get(encoderId);
        if (!entry) {
            this.metrics.misses++;
            return null;
        }
        
        const age = Date.now() - entry.timestamp;
        if (age > this.maxAge) {
            this.cache.delete(encoderId);
            this.metrics.misses++;
            return null;
        }
        
        this.metrics.hits++;
        return entry.data;
    }
    
    update(encoderId, partialData) {
        const existing = this.cache.get(encoderId);
        if (existing) {
            this.set(encoderId, {
                ...existing.data,
                ...partialData,
                _lastUpdated: Date.now()
            });
            existing.updateCount++;
        } else {
            this.set(encoderId, {
                ...partialData,
                _lastUpdated: Date.now()
            });
        }
    }
    
    getMetrics() {
        const hitRate = this.metrics.hits / 
            (this.metrics.hits + this.metrics.misses) || 0;
        
        return {
            ...this.metrics,
            hitRate: hitRate.toFixed(2),
            cacheSize: this.cache.size,
            maxSize: this.maxSize
        };
    }
} 