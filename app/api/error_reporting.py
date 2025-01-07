from flask import Blueprint, jsonify, request
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.core.error_handling import CentralErrorManager
from app.core.error_handling.analysis.correlation_analyzer import ErrorCorrelationAnalyzer
from app.core.error_handling import EnhancedErrorMetrics

error_reporting = Blueprint('error_reporting', __name__)

@error_reporting.route('/errors/summary', methods=['GET'])
async def get_error_summary():
    """Get comprehensive error summary"""
    time_range = request.args.get('time_range', 'day')
    source = request.args.get('source')
    error_type = request.args.get('error_type')
    
    summary = await CentralErrorManager.get_error_summary(
        time_range=time_range,
        source=source,
        error_type=error_type
    )
    
    return jsonify(summary)

@error_reporting.route('/errors/analysis', methods=['GET'])
async def get_error_analysis():
    """Get detailed error analysis"""
    encoder_id = request.args.get('encoder_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    analyzer = ErrorCorrelationAnalyzer()
    analysis = await analyzer.analyze_correlations({
        'encoder_id': encoder_id,
        'timestamp': datetime.fromisoformat(start_time),
        'end_time': datetime.fromisoformat(end_time)
    })
    
    return jsonify(analysis)

@error_reporting.route('/errors/metrics', methods=['GET'])
async def get_error_metrics():
    """Get detailed error metrics"""
    metrics = EnhancedErrorMetrics()
    return jsonify({
        'error_counts': metrics.get_error_counts(),
        'recovery_stats': metrics.get_recovery_stats(),
        'performance_impact': metrics.get_performance_impact(),
        'resource_impact': metrics.get_resource_impact()
    })

@error_reporting.route('/errors/alerts', methods=['GET'])
async def get_error_alerts():
    """Get active error alerts"""
    severity = request.args.get('severity')
    source = request.args.get('source')
    
    alerts = await CentralErrorManager.get_active_alerts(
        severity=severity,
        source=source
    )
    
    return jsonify(alerts) 