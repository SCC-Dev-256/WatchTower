// Real-time data handling with Socket.IO
const socket = io();

// Graph initialization and updates
function initGraphs() {
    // Initialize base graphs
    initStreamingGraph();
    initBandwidthGraph();
    initStorageGraph();
    initAdvancedGraphs();  // Keep the advanced visualizations
    
    // Set up real-time updates
    socket.on('metrics_update', (data) => {
        updateGraphs(data);
        updateStatusMetrics(data);
    });
}

// Encoder Controls
function controlEncoder(action) {
    const encoderId = document.getElementById('encoderSelect').value;
    if (!encoderId) {
        showAlert('Please select an encoder', 'error');
        return;
    }

    fetch(`/api/v1/encoders/${encoderId}/control`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
    })
    .then(response => response.json())
    .then(data => {
        showAlert(`${action.replace('_', ' ')} command sent successfully`, 'success');
    })
    .catch(error => {
        showAlert('Failed to send command', 'error');
    });
}

// Alert Management
function acknowledgeAlert(alertId) {
    fetch(`/api/v1/alerts/${alertId}/acknowledge`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector(`[data-alert-id="${alertId}"]`).remove();
        showAlert('Alert acknowledged', 'success');
    });
}

// Initialize graphs
function initStreamingGraph() {
    const streamingData = {
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines',
        name: 'Active Streams'
    };

    const streamingLayout = {
        title: 'Active Streams',
        paper_bgcolor: '#1a1a1a',
        plot_bgcolor: '#1a1a1a',
        font: { color: '#ffffff' },
        xaxis: { title: 'Time' },
        yaxis: { title: 'Count' }
    };

    Plotly.newPlot('streamingGraph', [streamingData], streamingLayout);
}

// Add error handling and loading states
function updateGraphs(data) {
    try {
        document.body.classList.add('updating-graphs');
        
        if (data.error) {
            handleGraphError(data.error);
            return;
        }
        
        updateStreamingGraph(data.streaming);
        updateBandwidthGauge(data.bandwidth);
        updateStorageTreemap(data.storage);
        updateErrorHeatmap(data.errors);
        
        // Update analysis section if available
        if (data.analysis) {
            updateAnalysisDisplay(data.analysis);
        }
        
        document.body.classList.remove('updating-graphs');
    } catch (error) {
        console.error('Error updating graphs:', error);
        handleGraphError(error);
    }
}

function handleGraphError(error) {
    showAlert('Failed to update graphs: ' + error.message, 'error');
    document.body.classList.remove('updating-graphs');
}

// Add these new visualization functions
function initAdvancedGraphs() {
    // Error Rate Heatmap
    const errorHeatmapData = [{
        type: 'heatmap',
        x: getTimeIntervals(),
        y: getEncoderNames(),
        z: getErrorMatrix(),
        colorscale: 'RdYlGn',
        reversescale: true
    }];

    const errorHeatmapLayout = {
        title: 'Error Frequency by Encoder',
        paper_bgcolor: '#1a1a1a',
        plot_bgcolor: '#1a1a1a',
        font: { color: '#ffffff' },
        xaxis: { title: 'Time' },
        yaxis: { title: 'Encoder' }
    };

    Plotly.newPlot('errorHeatmap', errorHeatmapData, errorHeatmapLayout);

    // Network Performance Timeline
    const networkData = {
        type: 'scatter3d',
        mode: 'lines+markers',
        x: [], // time
        y: [], // bandwidth
        z: [], // latency
        marker: {
            size: 5,
            color: [],
            colorscale: 'Viridis'
        }
    };

    const networkLayout = {
        title: 'Network Performance',
        scene: {
            xaxis: { title: 'Time' },
            yaxis: { title: 'Bandwidth (Mbps)' },
            zaxis: { title: 'Latency (ms)' }
        }
    };

    Plotly.newPlot('networkGraph', [networkData], networkLayout);

    // Storage Health Radar Chart
    const radarData = [{
        type: 'scatterpolar',
        r: [],
        theta: ['Read Speed', 'Write Speed', 'Free Space', 'Health Score', 'SMART Status'],
        fill: 'toself',
        name: 'Storage 1'
    }, {
        type: 'scatterpolar',
        r: [],
        theta: ['Read Speed', 'Write Speed', 'Free Space', 'Health Score', 'SMART Status'],
        fill: 'toself',
        name: 'Storage 2'
    }];

    const radarLayout = {
        polar: {
            radialaxis: {
                visible: true,
                range: [0, 100]
            }
        },
        showlegend: true
    };

    Plotly.newPlot('storageRadar', radarData, radarLayout);
}

// Add these update functions for real-time graphs
function updateStreamingGraph(data) {
    const update = {
        x: [[new Date()]],
        y: [[data.active_streams]]
    };
    
    Plotly.extendTraces('streamingGraph', update, [0], 50);  // Keep last 50 points
}

function updateBandwidthGauge(data) {
    const update = {
        value: [data.current_mbps]
    };
    
    // Update color based on bandwidth utilization
    const colors = data.current_mbps > data.threshold_mbps ? '#ff0000' : '#00ff00';
    Plotly.update('bandwidthGraph', update, {
        'gauge.bar.color': colors
    });
}

function updateStorageTreemap(data) {
    const update = {
        values: [
            data.storage1_used,
            data.storage2_used,
            data.total - (data.storage1_used + data.storage2_used)
        ]
    };
    
    Plotly.update('storageGraph', update);
}

// Update graphs with real-time data
socket.on('metrics_update', function(data) {
    updateStreamingGraph(data.streaming);
    updateBandwidthGauge(data.bandwidth);
    updateStorageTreemap(data.storage);
}); 

class DashboardManager {
    constructor(wsManager) {
        this.wsManager = wsManager;
        this.dataBuffer = new Map();  // Buffer for smoothing data
        this.updateInterval = 1000;  // 1 second updates
        this.setupRealTimeUpdates();
    }

    setupRealTimeUpdates() {
        // Real-time data smoothing
        setInterval(() => this.processBufferedData(), this.updateInterval);
        
        // Setup live stats
        this.setupLiveStats();
        
        // Setup predictive alerts
        this.setupPredictiveAlerts();
    }

    handleEncoderData(data) {
        // Buffer the incoming data
        const encoderId = data.encoder_id;
        if (!this.dataBuffer.has(encoderId)) {
            this.dataBuffer.set(encoderId, []);
        }
        
        const buffer = this.dataBuffer.get(encoderId);
        buffer.push({
            timestamp: Date.now(),
            data: data
        });
        
        // Keep only last 10 seconds of data
        const cutoff = Date.now() - 10000;
        while (buffer.length > 0 && buffer[0].timestamp < cutoff) {
            buffer.shift();
        }
    }

    processBufferedData() {
        this.dataBuffer.forEach((buffer, encoderId) => {
            if (buffer.length > 0) {
                const smoothedData = this.smoothData(buffer);
                this.updateDashboardMetrics(encoderId, smoothedData);
            }
        });
    }

    smoothData(buffer) {
        // Calculate moving averages
        const metrics = {
            bitrate: 0,
            latency: 0,
            packetLoss: 0
        };
        
        buffer.forEach(item => {
            metrics.bitrate += item.data.streaming.bitrate;
            metrics.latency += item.data.network.latency;
            metrics.packetLoss += item.data.network.packet_loss;
        });
        
        const count = buffer.length;
        return {
            bitrate: metrics.bitrate / count,
            latency: metrics.latency / count,
            packetLoss: metrics.packetLoss / count
        };
    }

    setupPredictiveAlerts() {
        setInterval(() => {
            this.dataBuffer.forEach((buffer, encoderId) => {
                if (buffer.length >= 5) {  // Need at least 5 data points
                    const trends = this.analyzeTrends(buffer);
                    this.checkPredictiveAlerts(encoderId, trends);
                }
            });
        }, 5000);  // Check every 5 seconds
    }

    analyzeTrends(buffer) {
        // Simple linear regression for trend analysis
        const points = buffer.map((item, index) => ({
            x: index,
            y: item.data.streaming.bitrate
        }));
        
        return this.calculateTrendline(points);
    }

    updateDashboardMetrics(encoderId, smoothedData) {
        // Update real-time metrics displays
        document.querySelectorAll(`[data-encoder-id="${encoderId}"]`).forEach(element => {
            const metric = element.dataset.metric;
            if (smoothedData[metric] !== undefined) {
                element.textContent = this.formatMetric(metric, smoothedData[metric]);
            }
        });
    }
} 