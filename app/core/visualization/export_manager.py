from typing import Dict, List, Optional
import pandas as pd
import json
from datetime import datetime
import csv
import xlsxwriter
from io import BytesIO
from app.core.visualization.error_visualizer import ErrorVisualizer
from app.core.error_handling.enhanced_metrics import EnhancedErrorMetrics

class ReportExporter:
    """Handle export of error reports in various formats"""
    
    def __init__(self, visualizer: ErrorVisualizer, metrics: EnhancedErrorMetrics):
        self.visualizer = visualizer
        self.metrics = metrics
        self.export_formats = {
            'csv': self._export_csv,
            'excel': self._export_excel,
            'json': self._export_json,
            'pdf': self._export_pdf
        }

    async def export_report(self, 
                          encoder_id: str, 
                          report_type: str,
                          format: str,
                          time_range: str) -> BytesIO:
        """Export error report in specified format"""
        
        # Gather report data
        report_data = await self._gather_report_data(encoder_id, report_type, time_range)
        
        # Export in requested format
        export_func = self.export_formats.get(format, self._export_json)
        return await export_func(report_data, report_type)

    async def _gather_report_data(self, 
                                encoder_id: str, 
                                report_type: str,
                                time_range: str) -> Dict:
        """Gather all necessary data for report"""
        
        data = {
            'metadata': {
                'encoder_id': encoder_id,
                'report_type': report_type,
                'time_range': time_range,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
        
        if report_type == 'error_summary':
            data.update(await self._gather_error_summary(encoder_id, time_range))
        elif report_type == 'pattern_analysis':
            data.update(await self._gather_pattern_analysis(encoder_id, time_range))
        elif report_type == 'performance_impact':
            data.update(await self._gather_performance_data(encoder_id, time_range))
            
        return data

    async def _export_excel(self, data: Dict, report_type: str) -> BytesIO:
        """Export report as Excel file"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # Add metadata sheet
        meta_sheet = workbook.add_worksheet('Metadata')
        for i, (key, value) in enumerate(data['metadata'].items()):
            meta_sheet.write(i, 0, key)
            meta_sheet.write(i, 1, str(value))
            
        # Add data sheets based on report type
        if report_type == 'error_summary':
            self._write_error_summary_sheets(workbook, data)
        elif report_type == 'pattern_analysis':
            self._write_pattern_analysis_sheets(workbook, data)
            
        workbook.close()
        output.seek(0)
        return output

    async def _export_pdf(self, data: Dict, report_type: str) -> BytesIO:
        """Export report as PDF with visualizations"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        
        # Generate report elements
        elements = []
        
        # Add metadata
        elements.extend(self._create_pdf_metadata(data['metadata']))
        
        # Add visualizations
        if report_type == 'error_summary':
            elements.extend(await self._create_pdf_error_summary(data))
        elif report_type == 'pattern_analysis':
            elements.extend(await self._create_pdf_pattern_analysis(data))
            
        doc.build(elements)
        output.seek(0)
        return output 