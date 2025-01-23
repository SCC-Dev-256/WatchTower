import pytest
import asyncio
import socketio
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, stdev
from ..app.services.metrics_analyzer import MetricsAnalyzer

class WebSocketLoadTest:
    def __init__(self, base_url, num_clients=100):
        self.base_url = base_url
        self.num_clients = num_clients
        self.clients = []
        self.metrics = []
        self.analyzer = MetricsAnalyzer()

    async def setup_clients(self):
        """Initialize WebSocket clients"""
        for i in range(self.num_clients):
            sio = socketio.AsyncClient()
            
            @sio.on('connect')
            async def on_connect():
                self.metrics.append({
                    'client_id': i,
                    'connect_time': time.time(),
                    'latencies': []
                })

            @sio.on('encoder_update')
            async def on_message(data):
                latency = time.time() - data.get('timestamp', 0)
                client_metrics = next(m for m in self.metrics if m['client_id'] == i)
                client_metrics['latencies'].append(latency)

            self.clients.append(sio)

    async def run_load_test(self, duration=60):
        """Run load test for specified duration"""
        # Connect all clients
        await asyncio.gather(*[
            client.connect(self.base_url) for client in self.clients
        ])

        # Subscribe to encoders
        tasks = []
        for i, client in enumerate(self.clients):
            encoder_id = i % 5  # Distribute across 5 encoders
            tasks.append(
                client.emit('subscribe_encoder', {'encoder_id': encoder_id})
            )
        await asyncio.gather(*tasks)

        # Run for specified duration
        await asyncio.sleep(duration)

        # Disconnect clients
        await asyncio.gather(*[
            client.disconnect() for client in self.clients
        ])

        return self.analyze_results()

    def analyze_results(self):
        """Analyze test results"""
        results = {
            'connection_times': [],
            'message_latencies': [],
            'errors': [],
            'disconnects': 0
        }

        for metric in self.metrics:
            results['connection_times'].append(metric['connect_time'])
            results['message_latencies'].extend(metric['latencies'])

        return {
            'summary': {
                'avg_connection_time': mean(results['connection_times']),
                'avg_latency': mean(results['message_latencies']),
                'latency_stddev': stdev(results['message_latencies']),
                'max_latency': max(results['message_latencies']),
                'total_messages': len(results['message_latencies']),
                'messages_per_second': len(results['message_latencies']) / 60,
                'error_rate': len(results['errors']) / self.num_clients
            },
            'detailed': results
        }

@pytest.mark.asyncio
async def test_websocket_performance():
    load_test = WebSocketLoadTest('http://localhost:5000')
    await load_test.setup_clients()
    results = await load_test.run_load_test()
    
    # Assert performance requirements
    assert results['summary']['avg_latency'] < 0.1  # 100ms max average latency
    assert results['summary']['error_rate'] < 0.01  # Less than 1% error rate
    assert results['summary']['messages_per_second'] > 50  # Minimum message rate 