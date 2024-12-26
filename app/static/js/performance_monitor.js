class PerformanceMonitor {
    constructor(wsManager) {
        this.wsManager = wsManager;
        this.metrics = new Map();
        this.thresholds = {
            latency: 200,      // ms
            messageRate: 100,   // messages per second
            processingTime: 50  // ms
        };
        this.setupMonitoring();
    }

    setupMonitoring() {
        // Monitor WebSocket performance
        this.wsManager.socket.on('connect', () => {
            this.startPerformanceTracking();
        });

        // Track message processing time
        const originalHandleUpdate = this.wsManager.handleEncoderUpdate;
        this.wsManager.handleEncoderUpdate = (data) => {
            const start = performance.now();
            originalHandleUpdate.call(this.wsManager, data);
            this.recordProcessingTime(performance.now() - start);
        };

        // Start periodic reporting
        setInterval(() => this.reportMetrics(), 5000);
    }

    startPerformanceTracking() {
        this.metrics.set('startTime', Date.now());
        this.metrics.set('messageCount', 0);
        this.metrics.set('processingTimes', []);
        this.metrics.set('latencies', []);

        // Setup Resource Timing API monitoring
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach(entry => {
                if (entry.initiatorType === 'websocket') {
                    this.recordLatency(entry.duration);
                }
            });
        });

        observer.observe({ entryTypes: ['resource'] });
    }

    recordProcessingTime(time) {
        const times = this.metrics.get('processingTimes');
        times.push(time);
        if (times.length > 100) times.shift();  // Keep last 100 measurements

        if (time > this.thresholds.processingTime) {
            this.reportPerformanceIssue('processing', time);
        }
    }

    recordLatency(latency) {
        const latencies = this.metrics.get('latencies');
        latencies.push(latency);
        if (latencies.length > 100) latencies.shift();

        if (latency > this.thresholds.latency) {
            this.reportPerformanceIssue('latency', latency);
        }
    }

    calculateMetrics() {
        const processingTimes = this.metrics.get('processingTimes');
        const latencies = this.metrics.get('latencies');

        return {
            averageProcessingTime: this.calculateAverage(processingTimes),
            averageLatency: this.calculateAverage(latencies),
            messageRate: this.calculateMessageRate(),
            performanceScore: this.calculatePerformanceScore()
        };
    }

    reportMetrics() {
        const metrics = this.calculateMetrics();
        
        // Update performance dashboard
        document.querySelectorAll('[data-performance-metric]').forEach(element => {
            const metric = element.dataset.performanceMetric;
            if (metrics[metric] !== undefined) {
                element.textContent = this.formatMetric(metric, metrics[metric]);
            }
        });

        // Send to server for logging
        this.wsManager.socket.emit('performance_metrics', metrics);
    }

    reportPerformanceIssue(type, value) {
        console.warn(`Performance issue detected: ${type} = ${value}`);
        this.wsManager.showAlert(
            `Performance warning: High ${type} detected (${value.toFixed(2)})`,
            'warning'
        );
    }

    calculatePerformanceScore() {
        const metrics = {
            processingTime: this.calculateProcessingTimeScore(),
            latency: this.calculateLatencyScore(),
            messageRate: this.calculateMessageRateScore(),
            memoryUsage: this.calculateMemoryScore(),
            frameRate: this.calculateFrameRateScore()
        };

        // Weight the scores
        return {
            overall: Object.values(metrics).reduce((sum, score) => sum + score, 0) / Object.keys(metrics).length,
            detailed: metrics
        };
    }

    calculateProcessingTimeScore() {
        const times = this.metrics.get('processingTimes');
        const avg = this.calculateAverage(times);
        const variance = this.calculateVariance(times);
        
        // Score based on average and stability
        const avgScore = Math.max(0, 100 - (avg / this.thresholds.processingTime * 100));
        const stabilityScore = Math.max(0, 100 - (variance / 1000));
        
        return (avgScore * 0.7 + stabilityScore * 0.3);
    }

    monitorResourceUsage() {
        if ('performance' in window) {
            // Monitor memory usage
            if (performance.memory) {
                this.recordMemoryUsage({
                    usedJSHeapSize: performance.memory.usedJSHeapSize,
                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                });
            }

            // Monitor frame rate
            let lastTime = performance.now();
            let frames = 0;
            
            const checkFrame = () => {
                frames++;
                const currentTime = performance.now();
                
                if (currentTime - lastTime >= 1000) {
                    this.recordFrameRate(frames);
                    frames = 0;
                    lastTime = currentTime;
                }
                
                requestAnimationFrame(checkFrame);
            };
            
            requestAnimationFrame(checkFrame);
        }
    }

    monitorNetworkQuality() {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            
            const updateNetworkInfo = () => {
                this.recordNetworkQuality({
                    downlink: connection.downlink,
                    rtt: connection.rtt,
                    effectiveType: connection.effectiveType,
                    saveData: connection.saveData
                });
            };
            
            connection.addEventListener('change', updateNetworkInfo);
            updateNetworkInfo();
        }
    }

    generatePerformanceReport() {
        const currentMetrics = this.calculateMetrics();
        const report = {
            timestamp: new Date().toISOString(),
            metrics: currentMetrics,
            performance: {
                memory: this.metrics.get('memoryUsage'),
                network: this.metrics.get('networkQuality'),
                frameRate: this.metrics.get('frameRate')
            },
            thresholds: {
                ...this.thresholds,
                violated: this.getViolatedThresholds()
            },
            recommendations: this.generateRecommendations()
        };

        // Send detailed report to server
        this.wsManager.socket.emit('performance_report', report);
        return report;
    }
} 