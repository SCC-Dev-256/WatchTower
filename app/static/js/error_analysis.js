// Error Analysis Visualizations
function initErrorAnalysis() {
    // Error Correlation Network
    const networkData = {
        nodes: [],
        edges: []
    };
    
    const networkLayout = {
        title: 'Error Correlation Network',
        showlegend: true,
        hovermode: 'closest',
        margin: { b: 20, l: 5, r: 5, t: 40 }
    };
    
    Plotly.newPlot('errorNetwork', networkData, networkLayout);
    
    // Root Cause Analysis Tree
    const treeData = [{
        type: "treemap",
        labels: ["Root Cause", "Effect 1", "Effect 2"],
        parents: ["", "Root Cause", "Root Cause"],
        values: [10, 5, 5],
        textinfo: "label+value",
        marker: { colors: ['#ff0000', '#ff6666', '#ff9999'] }
    }];
    
    Plotly.newPlot('rootCauseTree', treeData);
    
    // Error Frequency Timeline
    const timelineData = [{
        type: 'scatter',
        mode: 'lines+markers',
        x: [], // timestamps
        y: [], // error counts
        name: 'Error Frequency',
        line: { color: '#ff0000' }
    }];
    
    const timelineLayout = {
        title: 'Error Frequency Over Time',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Error Count' }
    };
    
    Plotly.newPlot('errorTimeline', timelineData, timelineLayout);
}

// Update error analysis visualizations with new data
function updateErrorAnalysis(analysisData) {
    updateCorrelationNetwork(analysisData.correlation);
    updateRootCauseTree(analysisData.root_cause);
    updateErrorTimeline(analysisData.historical_context);
}

// Handle error details view
function showErrorDetails(errorId) {
    fetch(`/api/errors/${errorId}/analysis`)
        .then(response => response.json())
        .then(analysis => {
            displayErrorAnalysis(analysis);
            highlightCorrelatedErrors(analysis.correlation);
            showRemediationSteps(analysis.suggested_actions);
        });
} 