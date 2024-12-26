const socket = io('http://your-api-server');

socket.on('connect', () => {
    console.log('Connected to encoder monitoring service');
});

socket.on('encoder_event', (event) => {
    console.log('Received encoder event:', event);
    
    switch(event.type) {
        case 'status_change':
            updateEncoderStatus(event.data);
            break;
        case 'warning':
            showWarning(event.data);
            break;
        case 'error':
            showError(event.data);
            break;
        // Handle other event types
    }
});

socket.on('encoder_states', (states) => {
    console.log('Received encoder states:', states);
    // Update UI with current states
    Object.entries(states).forEach(([encoderId, state]) => {
        updateEncoderDisplay(encoderId, state);
    });
});

function updateEncoderDisplay(encoderId, state) {
    const encoderElement = document.getElementById(`encoder-${encoderId}`);
    if (encoderElement) {
        encoderElement.querySelector('.status').textContent = state.status;
        encoderElement.querySelector('.streaming').textContent = 
            state.streaming ? 'Streaming' : 'Not Streaming';
        encoderElement.querySelector('.recording').textContent = 
            state.recording ? 'Recording' : 'Not Recording';
        
        // Update metrics
        updateMetrics(encoderId, state.metrics);
        
        // Update health indicators
        updateHealthDisplay(encoderId, state.health);
    }
} 