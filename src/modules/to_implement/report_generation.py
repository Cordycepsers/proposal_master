"""
Report Generation Module - Independent Report Generation and Visualization

This module handles comprehensive report generation with advanced visualizations.
It can be developed, tested, and upgraded independently of other modules.
Includes data visualization, chart generation, and multi-format report export.

Features:
- Multi-format report generation (PDF, HTML, Word, Excel)
- Advanced data visualizations with matplotlib and plotly
- Interactive dashboards and charts
- Campaign performance analysis
- Competitive intelligence reports
- Executive summaries and detailed analysis
- Customizable templates and branding
"""

import asyncio
import logging
import json
import os
import io
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
import base64
import hashlib

# Data processing libraries
import pandas as pd
import numpy as np

# Visualization libraries
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Report generation libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.shared import OxmlElement, qn
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.chart import BarChart, LineChart, PieChart, Reference
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReportData:
    """Report data structure"""
    title: str
    organization_name: str
    report_type: str  # 'rfp_analysis', 'campaign_research', 'competitive_analysis'
    generated_date: datetime
    data: Dict[str, Any]
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    chart_type: str  # 'bar', 'line', 'pie', 'scatter', 'heatmap', 'funnel'
    title: str
    data_source: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    color_scheme: str = "default"
    interactive: bool = True
    size: Tuple[int, int] = (800, 600)
    export_formats: List[str] = field(default_factory=lambda: ['png', 'html'])

class ReportGeneratorInterface(ABC):
    """Abstract interface for report generators"""
    
    @abstractmethod
    async def generate_report(self, report_data: ReportData, output_path: str) -> str:
        """Generate report in specific format"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return supported output formats"""
        pass
    
    @abstractmethod
    def get_generator_name(self) -> str:
        """Return generator name"""
        pass

class PDFReportGenerator(ReportGeneratorInterface):
    """PDF report generator using ReportLab"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation")
        
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
    
    def _create_custom_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles"""
        custom_styles = {}
        
        # Title style
        custom_styles['CustomTitle'] = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB'),
            alignment=1  # Center alignment
        )
        
        # Heading style
        custom_styles['CustomHeading'] = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#A23B72'),
            borderWidth=1,
            borderColor=colors.HexColor('#A23B72'),
            borderPadding=5
        )
        
        # Subheading style
        custom_styles['CustomSubheading'] = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#F18F01')
        )
        
        # Body style
        custom_styles['CustomBody'] = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            textColor=colors.HexColor('#333333')
        )
        
        # Bullet style
        custom_styles['CustomBullet'] = ParagraphStyle(
            'CustomBullet',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            bulletIndent=10,
            spaceBefore=3,
            spaceAfter=3
        )
        
        return custom_styles
    
    async def generate_report(self, report_data: ReportData, output_path: str) -> str:
        """Generate PDF report"""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story (content)
            story = []
            
            # Title page
            story.extend(self._create_title_page(report_data))
            
            # Executive summary
            story.extend(self._create_executive_summary(report_data))
            
            # Main content sections
            story.extend(self._create_main_content(report_data))
            
            # Visualizations
            story.extend(self._create_visualizations_section(report_data))
            
            # Recommendations
            story.extend(self._create_recommendations_section(report_data))
            
            # Appendix
            story.extend(self._create_appendix(report_data))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def _create_title_page(self, report_data: ReportData) -> List:
        """Create title page"""
        story = []
        
        # Title
        story.append(Paragraph(report_data.title, self.custom_styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Organization
        story.append(Paragraph(f"Organization: {report_data.organization_name}", self.custom_styles['CustomSubheading']))
        story.append(Spacer(1, 10))
        
        # Report type
        story.append(Paragraph(f"Report Type: {report_data.report_type.replace('_', ' ').title()}", self.custom_styles['CustomBody']))
        story.append(Spacer(1, 10))
        
        # Generated date
        story.append(Paragraph(f"Generated: {report_data.generated_date.strftime('%B %d, %Y')}", self.custom_styles['CustomBody']))
        story.append(Spacer(1, 30))
        
        # Summary
        if report_data.summary:
            story.append(Paragraph("Executive Summary", self.custom_styles['CustomHeading']))
            story.append(Paragraph(report_data.summary, self.custom_styles['CustomBody']))
        
        return story
    
    def _create_executive_summary(self, report_data: ReportData) -> List:
        """Create executive summary section"""
        story = []
        
        if not report_data.summary:
            return story
        
        story.append(Paragraph("Executive Summary", self.custom_styles['CustomHeading']))
        story.append(Paragraph(report_data.summary, self.custom_styles['CustomBody']))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_main_content(self, report_data: ReportData) -> List:
        """Create main content sections"""
        story = []
        
        # Organization Profile
        if 'organization_profile' in report_data.data:
            story.extend(self._create_organization_section(report_data.data['organization_profile']))
        
        # Campaign Analysis
        if 'campaigns' in report_data.data:
            story.extend(self._create_campaigns_section(report_data.data['campaigns']))
        
        # RFP Analysis
        if 'rfp_analysis' in report_data.data:
            story.extend(self._create_rfp_analysis_section(report_data.data['rfp_analysis']))
        
        # Competitive Analysis
        if 'competitive_analysis' in report_data.data:
            story.extend(self._create_competitive_section(report_data.data['competitive_analysis']))
        
        return story
    
    def _create_organization_section(self, org_data: Dict[str, Any]) -> List:
        """Create organization profile section"""
        story = []
        
        story.append(Paragraph("Organization Profile", self.custom_styles['CustomHeading']))
        
        # Basic information
        basic_info = [
            ['Name', org_data.get('name', 'N/A')],
            ['Sector', org_data.get('sector', 'N/A')],
            ['Headquarters', org_data.get('headquarters', 'N/A')],
            ['Founded', str(org_data.get('founded_year', 'N/A'))],
            ['Website', org_data.get('website', 'N/A')]
        ]
        
        table = Table(basic_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 15))
        
        # Mission statement
        if org_data.get('mission_statement'):
            story.append(Paragraph("Mission Statement", self.custom_styles['CustomSubheading']))
            story.append(Paragraph(org_data['mission_statement'], self.custom_styles['CustomBody']))
            story.append(Spacer(1, 10))
        
        # Key focus areas
        if org_data.get('key_focus_areas'):
            story.append(Paragraph("Key Focus Areas", self.custom_styles['CustomSubheading']))
            for area in org_data['key_focus_areas'][:10]:
                story.append(Paragraph(f"• {area}", self.custom_styles['CustomBullet']))
            story.append(Spacer(1, 10))
        
        # Geographic presence
        if org_data.get('geographic_presence'):
            story.append(Paragraph("Geographic Presence", self.custom_styles['CustomSubheading']))
            for location in org_data['geographic_presence'][:10]:
                story.append(Paragraph(f"• {location}", self.custom_styles['CustomBullet']))
            story.append(Spacer(1, 15))
        
        return story
    
    def _create_campaigns_section(self, campaigns_data: List[Dict[str, Any]]) -> List:
        """Create campaigns analysis section"""
        story = []
        
        story.append(Paragraph("Campaign Analysis", self.custom_styles['CustomHeading']))
        
        if not campaigns_data:
            story.append(Paragraph("No campaign data available.", self.custom_styles['CustomBody']))
            return story
        
        story.append(Paragraph(f"Total campaigns analyzed: {len(campaigns_data)}", self.custom_styles['CustomBody']))
        story.append(Spacer(1, 10))
        
        # Campaign types analysis
        campaign_types = {}
        for campaign in campaigns_data:
            campaign_type = campaign.get('campaign_type', 'Unknown')
            campaign_types[campaign_type] = campaign_types.get(campaign_type, 0) + 1
        
        if campaign_types:
            story.append(Paragraph("Campaign Types Distribution", self.custom_styles['CustomSubheading']))
            
            type_data = [[campaign_type.title(), str(count)] for campaign_type, count in campaign_types.items()]
            type_table = Table(type_data, colWidths=[3*inch, 1*inch])
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(type_table)
            story.append(Spacer(1, 15))
        
        # Top campaigns
        story.append(Paragraph("Notable Campaigns", self.custom_styles['CustomSubheading']))
        
        for i, campaign in enumerate(campaigns_data[:5]):
            story.append(Paragraph(f"{i+1}. {campaign.get('title', 'Untitled Campaign')}", self.custom_styles['CustomBody']))
            
            if campaign.get('description'):
                story.append(Paragraph(campaign['description'][:200] + "...", self.custom_styles['CustomBody']))
            
            campaign_details = []
            if campaign.get('campaign_type'):
                campaign_details.append(f"Type: {campaign['campaign_type'].title()}")
            if campaign.get('channels_used'):
                campaign_details.append(f"Channels: {', '.join(campaign['channels_used'])}")
            
            if campaign_details:
                story.append(Paragraph(" | ".join(campaign_details), self.custom_styles['CustomBody']))
            
            story.append(Spacer(1, 8))
        
        return story
    
    def _create_rfp_analysis_section(self, rfp_data: Dict[str, Any]) -> List:
        """Create RFP analysis section"""
        story = []
        
        story.append(Paragraph("RFP Analysis", self.custom_styles['CustomHeading']))
        
        # Qualification score
        if 'qualification_score' in rfp_data:
            score = rfp_data['qualification_score']
            recommendation = rfp_data.get('recommendation', 'Unknown')
            
            story.append(Paragraph("Qualification Assessment", self.custom_styles['CustomSubheading']))
            story.append(Paragraph(f"Score: {score}/100", self.custom_styles['CustomBody']))
            story.append(Paragraph(f"Recommendation: {recommendation.replace('_', ' ').title()}", self.custom_styles['CustomBody']))
            story.append(Spacer(1, 10))
        
        # Green flags
        if 'green_flags' in rfp_data and rfp_data['green_flags']:
            story.append(Paragraph("Green Flags (Positive Indicators)", self.custom_styles['CustomSubheading']))
            for flag in rfp_data['green_flags']:
                story.append(Paragraph(f"✓ {flag}", self.custom_styles['CustomBullet']))
            story.append(Spacer(1, 10))
        
        # Red flags
        if 'red_flags' in rfp_data and rfp_data['red_flags']:
            story.append(Paragraph("Red Flags (Risk Indicators)", self.custom_styles['CustomSubheading']))
            for flag in rfp_data['red_flags']:
                story.append(Paragraph(f"✗ {flag}", self.custom_styles['CustomBullet']))
            story.append(Spacer(1, 10))
        
        # Extracted information
        if 'extracted_info' in rfp_data:
            info = rfp_data['extracted_info']
            story.append(Paragraph("Key Information Extracted", self.custom_styles['CustomSubheading']))
            
            info_table_data = []
            if info.get('deadline'):
                info_table_data.append(['Deadline', info['deadline']])
            if info.get('budget'):
                info_table_data.append(['Budget', info['budget']])
            if info.get('geographic_scope'):
                info_table_data.append(['Geographic Scope', ', '.join(info['geographic_scope'])])
            if info.get('deliverables'):
                info_table_data.append(['Deliverables', ', '.join(info['deliverables'])])
            
            if info_table_data:
                info_table = Table(info_table_data, colWidths=[2*inch, 4*inch])
                info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('BACKGROUND', (1, 0), (1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(info_table)
                story.append(Spacer(1, 15))
        
        return story
    
    def _create_competitive_section(self, comp_data: Dict[str, Any]) -> List:
        """Create competitive analysis section"""
        story = []
        
        story.append(Paragraph("Competitive Analysis", self.custom_styles['CustomHeading']))
        
        # Identified competitors
        if 'identified_competitors' in comp_data:
            story.append(Paragraph("Key Competitors", self.custom_styles['CustomSubheading']))
            for competitor in comp_data['identified_competitors']:
                story.append(Paragraph(f"• {competitor}", self.custom_styles['CustomBullet']))
            story.append(Spacer(1, 10))
        
        # Competitive advantages
        if 'competitive_advantages' in comp_data:
            story.append(Paragraph("Competitive Advantages", self.custom_styles['CustomSubheading']))
            for advantage in comp_data['competitive_advantages']:
                story.append(Paragraph(f"• {advantage}", self.custom_styles['CustomBullet']))
            story.append(Spacer(1, 10))
        
        # Market position
        if 'market_position' in comp_data:
            story.append(Paragraph("Market Position", self.custom_styles['CustomSubheading']))
            story.append(Paragraph(comp_data['market_position'], self.custom_styles['CustomBody']))
            story.append(Spacer(1, 15))
        
        return story
    
    def _create_visualizations_section(self, report_data: ReportData) -> List:
        """Create visualizations section"""
        story = []
        
        if not report_data.visualizations:
            return story
        
        story.append(Paragraph("Data Visualizations", self.custom_styles['CustomHeading']))
        
        for viz in report_data.visualizations:
            if viz.get('image_path') and os.path.exists(viz['image_path']):
                story.append(Paragraph(viz.get('title', 'Visualization'), self.custom_styles['CustomSubheading']))
                
                # Add image
                img = Image(viz['image_path'], width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 10))
                
                # Add description if available
                if viz.get('description'):
                    story.append(Paragraph(viz['description'], self.custom_styles['CustomBody']))
                    story.append(Spacer(1, 15))
        
        return story
    
    def _create_recommendations_section(self, report_data: ReportData) -> List:
        """Create recommendations section"""
        story = []
        
        if not report_data.recommendations:
            return story
        
        story.append(Paragraph("Recommendations", self.custom_styles['CustomHeading']))
        
        for i, recommendation in enumerate(report_data.recommendations, 1):
            story.append(Paragraph(f"{i}. {recommendation}", self.custom_styles['CustomBody']))
            story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 15))
        return story
    
    def _create_appendix(self, report_data: ReportData) -> List:
        """Create appendix section"""
        story = []
        
        story.append(Paragraph("Appendix", self.custom_styles['CustomHeading']))
        
        # Metadata
        if report_data.metadata:
            story.append(Paragraph("Report Metadata", self.custom_styles['CustomSubheading']))
            
            metadata_items = []
            for key, value in report_data.metadata.items():
                if isinstance(value, (str, int, float)):
                    metadata_items.append([key.replace('_', ' ').title(), str(value)])
            
            if metadata_items:
                metadata_table = Table(metadata_items, colWidths=[2*inch, 4*inch])
                metadata_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (1, 0), (1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(metadata_table)
        
        return story
    
    def get_supported_formats(self) -> List[str]:
        return ['pdf']
    
    def get_generator_name(self) -> str:
        return "PDF Report Generator"

class HTMLReportGenerator(ReportGeneratorInterface):
    """HTML report generator with interactive visualizations"""
    
    def __init__(self):
        self.template = self._create_html_template()
    
    def _create_html_template(self) -> str:
        """Create HTML template"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    background: linear-gradient(135deg, #2E86AB, #A23B72);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                }}
                .header .subtitle {{
                    margin: 10px 0 0 0;
                    font-size: 1.2em;
                    opacity: 0.9;
                }}
                .section {{
                    background: white;
                    margin: 20px 0;
                    padding: 25px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .section h2 {{
                    color: #2E86AB;
                    border-bottom: 3px solid #F18F01;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .section h3 {{
                    color: #A23B72;
                    margin-top: 25px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .info-card {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #F18F01;
                }}
                .info-card h4 {{
                    margin: 0 0 10px 0;
                    color: #2E86AB;
                }}
                .tag {{
                    display: inline-block;
                    background: #e9ecef;
                    color: #495057;
                    padding: 4px 8px;
                    margin: 2px;
                    border-radius: 15px;
                    font-size: 0.9em;
                }}
                .green-flag {{
                    color: #28a745;
                    font-weight: bold;
                }}
                .red-flag {{
                    color: #dc3545;
                    font-weight: bold;
                }}
                .score {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #2E86AB;
                    text-align: center;
                    margin: 20px 0;
                }}
                .recommendation {{
                    background: #e8f4f8;
                    border-left: 4px solid #2E86AB;
                    padding: 15px;
                    margin: 10px 0;
                }}
                .visualization {{
                    margin: 20px 0;
                    text-align: center;
                }}
                .table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                .table th, .table td {{
                    border: 1px solid #dee2e6;
                    padding: 12px;
                    text-align: left;
                }}
                .table th {{
                    background-color: #2E86AB;
                    color: white;
                }}
                .table tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    color: #6c757d;
                    border-top: 1px solid #dee2e6;
                }}
                @media (max-width: 768px) {{
                    body {{
                        padding: 10px;
                    }}
                    .header h1 {{
                        font-size: 2em;
                    }}
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
            {plotly_js}
        </head>
        <body>
            {content}
        </body>
        </html>
        """
    
    async def generate_report(self, report_data: ReportData, output_path: str) -> str:
        """Generate HTML report"""
        try:
            # Build content sections
            content_sections = []
            
            # Header
            content_sections.append(self._create_header(report_data))
            
            # Executive summary
            if report_data.summary:
                content_sections.append(self._create_summary_section(report_data.summary))
            
            # Organization profile
            if 'organization_profile' in report_data.data:
                content_sections.append(self._create_organization_html_section(report_data.data['organization_profile']))
            
            # RFP analysis
            if 'rfp_analysis' in report_data.data:
                content_sections.append(self._create_rfp_html_section(report_data.data['rfp_analysis']))
            
            # Campaign analysis
            if 'campaigns' in report_data.data:
                content_sections.append(self._create_campaigns_html_section(report_data.data['campaigns']))
            
            # Visualizations
            if report_data.visualizations:
                content_sections.append(self._create_visualizations_html_section(report_data.visualizations))
            
            # Recommendations
            if report_data.recommendations:
                content_sections.append(self._create_recommendations_html_section(report_data.recommendations))
            
            # Footer
            content_sections.append(self._create_footer(report_data))
            
            # Combine all content
            content = '\n'.join(content_sections)
            
            # Include Plotly.js if needed
            plotly_js = ""
            if PLOTLY_AVAILABLE and any('plotly' in viz.get('type', '') for viz in report_data.visualizations):
                plotly_js = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'
            
            # Generate final HTML
            html_content = self.template.format(
                title=report_data.title,
                content=content,
                plotly_js=plotly_js
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            raise
    
    def _create_header(self, report_data: ReportData) -> str:
        """Create header section"""
        return f"""
        <div class="header">
            <h1>{report_data.title}</h1>
            <div class="subtitle">{report_data.organization_name}</div>
            <div class="subtitle">{report_data.generated_date.strftime('%B %d, %Y')}</div>
        </div>
        """
    
    def _create_summary_section(self, summary: str) -> str:
        """Create summary section"""
        return f"""
        <div class="section">
            <h2>Executive Summary</h2>
            <p>{summary}</p>
        </div>
        """
    
    def _create_organization_html_section(self, org_data: Dict[str, Any]) -> str:
        """Create organization section"""
        html = ['<div class="section">', '<h2>Organization Profile</h2>']
        
        # Basic info grid
        html.append('<div class="info-grid">')
        
        basic_info = [
            ('Name', org_data.get('name', 'N/A')),
            ('Sector', org_data.get('sector', 'N/A')),
            ('Headquarters', org_data.get('headquarters', 'N/A')),
            ('Founded', str(org_data.get('founded_year', 'N/A'))),
            ('Website', org_data.get('website', 'N/A'))
        ]
        
        for label, value in basic_info:
            html.append(f'''
            <div class="info-card">
                <h4>{label}</h4>
                <p>{value}</p>
            </div>
            ''')
        
        html.append('</div>')
        
        # Mission statement
        if org_data.get('mission_statement'):
            html.append(f'<h3>Mission Statement</h3>')
            html.append(f'<p>{org_data["mission_statement"]}</p>')
        
        # Focus areas
        if org_data.get('key_focus_areas'):
            html.append('<h3>Key Focus Areas</h3>')
            html.append('<div>')
            for area in org_data['key_focus_areas'][:10]:
                html.append(f'<span class="tag">{area}</span>')
            html.append('</div>')
        
        # Geographic presence
        if org_data.get('geographic_presence'):
            html.append('<h3>Geographic Presence</h3>')
            html.append('<div>')
            for location in org_data['geographic_presence'][:10]:
                html.append(f'<span class="tag">{location}</span>')
            html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _create_rfp_html_section(self, rfp_data: Dict[str, Any]) -> str:
        """Create RFP analysis section"""
        html = ['<div class="section">', '<h2>RFP Analysis</h2>']
        
        # Qualification score
        if 'qualification_score' in rfp_data:
            score = rfp_data['qualification_score']
            recommendation = rfp_data.get('recommendation', 'Unknown').replace('_', ' ').title()
            
            html.append(f'<div class="score">{score}/100</div>')
            html.append(f'<p style="text-align: center; font-size: 1.2em;"><strong>Recommendation: {recommendation}</strong></p>')
        
        # Green flags
        if 'green_flags' in rfp_data and rfp_data['green_flags']:
            html.append('<h3>Green Flags (Positive Indicators)</h3>')
            html.append('<ul>')
            for flag in rfp_data['green_flags']:
                html.append(f'<li class="green-flag">✓ {flag}</li>')
            html.append('</ul>')
        
        # Red flags
        if 'red_flags' in rfp_data and rfp_data['red_flags']:
            html.append('<h3>Red Flags (Risk Indicators)</h3>')
            html.append('<ul>')
            for flag in rfp_data['red_flags']:
                html.append(f'<li class="red-flag">✗ {flag}</li>')
            html.append('</ul>')
        
        # Extracted information
        if 'extracted_info' in rfp_data:
            info = rfp_data['extracted_info']
            html.append('<h3>Key Information Extracted</h3>')
            html.append('<table class="table">')
            html.append('<thead><tr><th>Field</th><th>Value</th></tr></thead>')
            html.append('<tbody>')
            
            if info.get('deadline'):
                html.append(f'<tr><td>Deadline</td><td>{info["deadline"]}</td></tr>')
            if info.get('budget'):
                html.append(f'<tr><td>Budget</td><td>{info["budget"]}</td></tr>')
            if info.get('geographic_scope'):
                html.append(f'<tr><td>Geographic Scope</td><td>{", ".join(info["geographic_scope"])}</td></tr>')
            if info.get('deliverables'):
                html.append(f'<tr><td>Deliverables</td><td>{", ".join(info["deliverables"])}</td></tr>')
            
            html.append('</tbody></table>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _create_campaigns_html_section(self, campaigns_data: List[Dict[str, Any]]) -> str:
        """Create campaigns section"""
        html = ['<div class="section">', '<h2>Campaign Analysis</h2>']
        
        if not campaigns_data:
            html.append('<p>No campaign data available.</p>')
            html.append('</div>')
            return '\n'.join(html)
        
        html.append(f'<p><strong>Total campaigns analyzed:</strong> {len(campaigns_data)}</p>')
        
        # Campaign types
        campaign_types = {}
        for campaign in campaigns_data:
            campaign_type = campaign.get('campaign_type', 'Unknown')
            campaign_types[campaign_type] = campaign_types.get(campaign_type, 0) + 1
        
        if campaign_types:
            html.append('<h3>Campaign Types Distribution</h3>')
            html.append('<table class="table">')
            html.append('<thead><tr><th>Campaign Type</th><th>Count</th></tr></thead>')
            html.append('<tbody>')
            
            for campaign_type, count in campaign_types.items():
                html.append(f'<tr><td>{campaign_type.title()}</td><td>{count}</td></tr>')
            
            html.append('</tbody></table>')
        
        # Notable campaigns
        html.append('<h3>Notable Campaigns</h3>')
        
        for i, campaign in enumerate(campaigns_data[:5]):
            html.append(f'<div class="info-card">')
            html.append(f'<h4>{i+1}. {campaign.get("title", "Untitled Campaign")}</h4>')
            
            if campaign.get('description'):
                html.append(f'<p>{campaign["description"][:200]}...</p>')
            
            campaign_details = []
            if campaign.get('campaign_type'):
                campaign_details.append(f'<strong>Type:</strong> {campaign["campaign_type"].title()}')
            if campaign.get('channels_used'):
                campaign_details.append(f'<strong>Channels:</strong> {", ".join(campaign["channels_used"])}')
            
            if campaign_details:
                html.append(f'<p>{" | ".join(campaign_details)}</p>')
            
            html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _create_visualizations_html_section(self, visualizations: List[Dict[str, Any]]) -> str:
        """Create visualizations section"""
        html = ['<div class="section">', '<h2>Data Visualizations</h2>']
        
        for viz in visualizations:
            html.append('<div class="visualization">')
            html.append(f'<h3>{viz.get("title", "Visualization")}</h3>')
            
            if viz.get('html_content'):
                # Interactive Plotly chart
                html.append(viz['html_content'])
            elif viz.get('image_path'):
                # Static image
                html.append(f'<img src="{viz["image_path"]}" alt="{viz.get("title", "Chart")}" style="max-width: 100%; height: auto;">')
            
            if viz.get('description'):
                html.append(f'<p>{viz["description"]}</p>')
            
            html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _create_recommendations_html_section(self, recommendations: List[str]) -> str:
        """Create recommendations section"""
        html = ['<div class="section">', '<h2>Recommendations</h2>']
        
        for i, recommendation in enumerate(recommendations, 1):
            html.append(f'<div class="recommendation">')
            html.append(f'<strong>{i}.</strong> {recommendation}')
            html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _create_footer(self, report_data: ReportData) -> str:
        """Create footer"""
        return f"""
        <div class="footer">
            <p>Report generated on {report_data.generated_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>RFP Automation System - Organization Research Module</p>
        </div>
        """
    
    def get_supported_formats(self) -> List[str]:
        return ['html']
    
    def get_generator_name(self) -> str:
        return "HTML Report Generator"

class VisualizationEngine:
    """Visualization engine for creating charts and graphs"""
    
    def __init__(self):
        self.matplotlib_style = 'seaborn-v0_8'
        self.color_palette = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83']
        
        # Set matplotlib style
        try:
            plt.style.use(self.matplotlib_style)
        except:
            plt.style.use('default')
        
        # Set seaborn palette
        sns.set_palette(self.color_palette)
    
    async def create_visualization(self, config: VisualizationConfig, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization based on configuration"""
        try:
            if config.interactive and PLOTLY_AVAILABLE:
                return await self._create_plotly_visualization(config, data)
            else:
                return await self._create_matplotlib_visualization(config, data)
        
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_plotly_visualization(self, config: VisualizationConfig, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive Plotly visualization"""
        try:
            fig = None
            
            if config.chart_type == 'bar':
                fig = self._create_plotly_bar_chart(config, data)
            elif config.chart_type == 'line':
                fig = self._create_plotly_line_chart(config, data)
            elif config.chart_type == 'pie':
                fig = self._create_plotly_pie_chart(config, data)
            elif config.chart_type == 'scatter':
                fig = self._create_plotly_scatter_chart(config, data)
            elif config.chart_type == 'heatmap':
                fig = self._create_plotly_heatmap(config, data)
            elif config.chart_type == 'funnel':
                fig = self._create_plotly_funnel_chart(config, data)
            else:
                raise ValueError(f"Unsupported chart type: {config.chart_type}")
            
            if fig is None:
                raise ValueError("Failed to create chart")
            
            # Update layout
            fig.update_layout(
                title=config.title,
                width=config.size[0],
                height=config.size[1],
                font=dict(family="Arial, sans-serif", size=12),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            # Generate outputs
            outputs = {}
            
            if 'html' in config.export_formats:
                html_content = pyo.plot(fig, output_type='div', include_plotlyjs=False)
                outputs['html_content'] = html_content
            
            if 'png' in config.export_formats:
                # Note: PNG export requires kaleido package
                try:
                    img_bytes = fig.to_image(format="png", width=config.size[0], height=config.size[1])
                    img_path = f"/tmp/chart_{hashlib.md5(config.title.encode()).hexdigest()[:8]}.png"
                    with open(img_path, 'wb') as f:
                        f.write(img_bytes)
                    outputs['image_path'] = img_path
                except Exception as e:
                    logger.warning(f"PNG export failed: {e}")
            
            return {
                'success': True,
                'type': 'plotly',
                'title': config.title,
                **outputs
            }
            
        except Exception as e:
            logger.error(f"Plotly visualization failed: {e}")
            raise
    
    def _create_plotly_bar_chart(self, config: VisualizationConfig, data: Dict[str, Any]) -> go.Figure:
        """Create Plotly bar chart"""
        source_data = data.get(config.data_source, {})
        
        if isinstance(source_data, dict):
            x_values = list(source_data.keys())
            y_values = list(source_data.values())
        elif isinstance(source_data, list) and config.x_axis and config.y_axis:
            x_values = [item.get(config.x_axis) for item in source_data]
            y_values = [item.get(config.y_axis) for item in source_data]
        else:
            raise ValueError("Invalid data format for bar chart")
        
        fig = go.Figure(data=[
            go.Bar(
                x=x_values,
                y=y_values,
                marker_color=self.color_palette[0]
            )
        ])
        
        return fig
    
    def _create_plotly_line_chart(self, config: VisualizationConfig, data: Dict[str, Any]) -> go.Figure:
        """Create Plotly line chart"""
        source_data = data.get(config.data_source, [])
        
        if not isinstance(source_data, list):
            raise ValueError("Line chart requires list data")
        
        x_values = [item.get(config.x_axis) for item in source_data]
        y_values = [item.get(config.y_axis) for item in source_data]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines+markers',
                line=dict(color=self.color_palette[0], width=3),
                marker=dict(size=8)
            )
        ])
        
        return fig
    
    def _create_plotly_pie_chart(self, config: VisualizationConfig, data: Dict[str, Any]) -> go.Figure:
        """Create Plotly pie chart"""
        source_data = data.get(config.data_source, {})
        
        if isinstance(source_data, dict):
            labels = list(source_data.keys())
            values = list(source_data.values())
        else:
            raise ValueError("Invalid data format for pie chart")
        
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                marker_colors=self.color_palette[:len(labels)]
            )
        ])
        
        return fig
    
    def _create_plotly_scatter_chart(self, config: VisualizationConfig, data: Dict[str, Any]) -> go.Figure:
        """Create Plotly scatter chart"""
        source_data = data.get(config.data_source, [])
        
        if not isinstance(source_data, list):
            raise ValueError("Scatter chart requires list data")
        
        x_values = [item.get(config.x_axis) for item in source_data]
        y_values = [item.get(config.y_axis) for item in source_data]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                marker=dict(
                    size=10,
                    color=self.color_palette[0],
                    opacity=0.7
                )
            )
        ])
        
        return fig
    
    def _create_plotly_heatmap(self, config: VisualizationConfig, data: Dict[str, Any]) -> go.Figure:
        """Create Plotly heatmap"""
        source_data = data.get(config.data_source, [])
        
        # Convert to matrix format
        if isinstance(source_data, list):
            # Assume data has x, y, and value fields
            df = pd.DataFrame(source_data)
            pivot_table = df.pivot_table(
                values='value',
                index=config.y_axis,
                columns=config.x_axis,
                fill_value=0
            )
            z_values = pivot_table.values
            x_labels = pivot_table.columns.tolist()
            y_labels = pivot_table.index.tolist()
        else:
            raise ValueError("Invalid data format for heatmap")
        
        fig = go.Figure(data=[
            go.Heatmap(
                z=z_values,
                x=x_labels,
                y=y_labels,
                colorscale='Blues'
            )
        ])
        
        return fig
    
    def _create_plotly_funnel_chart(self, config: VisualizationConfig, data: Dict[str, Any]) -> go.Figure:
        """Create Plotly funnel chart"""
        source_data = data.get(config.data_source, {})
        
        if isinstance(source_data, dict):
            labels = list(source_data.keys())
            values = list(source_data.values())
        else:
            raise ValueError("Invalid data format for funnel chart")
        
        fig = go.Figure(data=[
            go.Funnel(
                y=labels,
                x=values,
                marker_color=self.color_palette[0]
            )
        ])
        
        return fig
    
    async def _create_matplotlib_visualization(self, config: VisualizationConfig, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create static matplotlib visualization"""
        try:
            fig, ax = plt.subplots(figsize=(config.size[0]/100, config.size[1]/100))
            
            if config.chart_type == 'bar':
                self._create_matplotlib_bar_chart(ax, config, data)
            elif config.chart_type == 'line':
                self._create_matplotlib_line_chart(ax, config, data)
            elif config.chart_type == 'pie':
                self._create_matplotlib_pie_chart(ax, config, data)
            elif config.chart_type == 'scatter':
                self._create_matplotlib_scatter_chart(ax, config, data)
            else:
                raise ValueError(f"Unsupported chart type: {config.chart_type}")
            
            # Set title and labels
            ax.set_title(config.title, fontsize=16, fontweight='bold', pad=20)
            
            # Save to file
            img_path = f"/tmp/chart_{hashlib.md5(config.title.encode()).hexdigest()[:8]}.png"
            plt.tight_layout()
            plt.savefig(img_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return {
                'success': True,
                'type': 'matplotlib',
                'title': config.title,
                'image_path': img_path
            }
            
        except Exception as e:
            logger.error(f"Matplotlib visualization failed: {e}")
            raise
    
    def _create_matplotlib_bar_chart(self, ax, config: VisualizationConfig, data: Dict[str, Any]):
        """Create matplotlib bar chart"""
        source_data = data.get(config.data_source, {})
        
        if isinstance(source_data, dict):
            x_values = list(source_data.keys())
            y_values = list(source_data.values())
        else:
            raise ValueError("Invalid data format for bar chart")
        
        bars = ax.bar(x_values, y_values, color=self.color_palette[0])
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height}', ha='center', va='bottom')
        
        ax.set_xlabel(config.x_axis or 'Categories')
        ax.set_ylabel(config.y_axis or 'Values')
        plt.xticks(rotation=45, ha='right')
    
    def _create_matplotlib_line_chart(self, ax, config: VisualizationConfig, data: Dict[str, Any]):
        """Create matplotlib line chart"""
        source_data = data.get(config.data_source, [])
        
        if not isinstance(source_data, list):
            raise ValueError("Line chart requires list data")
        
        x_values = [item.get(config.x_axis) for item in source_data]
        y_values = [item.get(config.y_axis) for item in source_data]
        
        ax.plot(x_values, y_values, color=self.color_palette[0], linewidth=3, marker='o', markersize=8)
        ax.set_xlabel(config.x_axis or 'X Axis')
        ax.set_ylabel(config.y_axis or 'Y Axis')
        ax.grid(True, alpha=0.3)
    
    def _create_matplotlib_pie_chart(self, ax, config: VisualizationConfig, data: Dict[str, Any]):
        """Create matplotlib pie chart"""
        source_data = data.get(config.data_source, {})
        
        if isinstance(source_data, dict):
            labels = list(source_data.keys())
            values = list(source_data.values())
        else:
            raise ValueError("Invalid data format for pie chart")
        
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=self.color_palette[:len(labels)],
            autopct='%1.1f%%',
            startangle=90
        )
        
        # Improve text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    def _create_matplotlib_scatter_chart(self, ax, config: VisualizationConfig, data: Dict[str, Any]):
        """Create matplotlib scatter chart"""
        source_data = data.get(config.data_source, [])
        
        if not isinstance(source_data, list):
            raise ValueError("Scatter chart requires list data")
        
        x_values = [item.get(config.x_axis) for item in source_data]
        y_values = [item.get(config.y_axis) for item in source_data]
        
        ax.scatter(x_values, y_values, color=self.color_palette[0], s=100, alpha=0.7)
        ax.set_xlabel(config.x_axis or 'X Axis')
        ax.set_ylabel(config.y_axis or 'Y Axis')
        ax.grid(True, alpha=0.3)

class ReportGenerationModule:
    """Main Report Generation Module - Orchestrates all generators"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize generators
        self.generators = {}
        
        # PDF generator
        if REPORTLAB_AVAILABLE:
            self.generators['pdf'] = PDFReportGenerator()
        
        # HTML generator (always available)
        self.generators['html'] = HTMLReportGenerator()
        
        # Word generator
        if DOCX_AVAILABLE:
            # Would implement WordReportGenerator here
            pass
        
        # Excel generator
        if OPENPYXL_AVAILABLE:
            # Would implement ExcelReportGenerator here
            pass
        
        # Initialize visualization engine
        self.viz_engine = VisualizationEngine()
        
        # Configuration
        self.default_format = self.config.get('default_format', 'html')
        self.output_directory = self.config.get('output_directory', '/tmp/reports')
        self.enable_visualizations = self.config.get('enable_visualizations', True)
        
        # Create output directory
        os.makedirs(self.output_directory, exist_ok=True)
        
        logger.info(f"Report Generation Module initialized with {len(self.generators)} generators")
        logger.info(f"Available formats: {list(self.generators.keys())}")
        print(f"REPORTLAB_AVAILABLE: {REPORTLAB_AVAILABLE}")
    
    async def generate_comprehensive_report(self, report_data: ReportData, formats: List[str] = None) -> Dict[str, str]:
        """Generate comprehensive report in multiple formats"""
        if formats is None:
            formats = [self.default_format]
        
        # Generate visualizations if enabled
        if self.enable_visualizations and 'visualizations' in report_data.data:
            await self._generate_visualizations(report_data)
        
        # Generate reports in requested formats
        generated_reports = {}
        
        for format_name in formats:
            if format_name not in self.generators:
                logger.warning(f"Format {format_name} not available")
                continue
            
            try:
                # Generate filename
                safe_title = "".join(c for c in report_data.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title}_{report_data.generated_date.strftime('%Y%m%d_%H%M%S')}.{format_name}"
                output_path = os.path.join(self.output_directory, filename)
                
                # Generate report
                generator = self.generators[format_name]
                result_path = await generator.generate_report(report_data, output_path)
                generated_reports[format_name] = result_path
                
                logger.info(f"Generated {format_name} report: {result_path}")
                
            except Exception as e:
                logger.error(f"Failed to generate {format_name} report: {e}")
                generated_reports[format_name] = f"Error: {str(e)}"
        
        return generated_reports
    
    async def _generate_visualizations(self, report_data: ReportData):
        """Generate visualizations for report data"""
        try:
            visualizations = []
            
            # Campaign type distribution
            if 'campaigns' in report_data.data:
                campaigns = report_data.data['campaigns']
                if campaigns:
                    campaign_types = {}
                    for campaign in campaigns:
                        campaign_type = campaign.get('campaign_type', 'Unknown')
                        campaign_types[campaign_type] = campaign_types.get(campaign_type, 0) + 1
                    
                    if campaign_types:
                        viz_config = VisualizationConfig(
                            chart_type='pie',
                            title='Campaign Types Distribution',
                            data_source='campaign_types',
                            color_scheme='default',
                            interactive=True
                        )
                        
                        viz_data = {'campaign_types': campaign_types}
                        viz_result = await self.viz_engine.create_visualization(viz_config, viz_data)
                        
                        if viz_result.get('success'):
                            visualizations.append(viz_result)
            
            # RFP qualification score
            if 'rfp_analysis' in report_data.data:
                rfp_data = report_data.data['rfp_analysis']
                if 'qualification_score' in rfp_data:
                    score = rfp_data['qualification_score']
                    
                    # Create gauge chart data
                    score_data = {
                        'score_breakdown': {
                            'Score': score,
                            'Remaining': 100 - score
                        }
                    }
                    
                    viz_config = VisualizationConfig(
                        chart_type='pie',
                        title=f'RFP Qualification Score: {score}/100',
                        data_source='score_breakdown',
                        color_scheme='default',
                        interactive=True
                    )
                    
                    viz_result = await self.viz_engine.create_visualization(viz_config, score_data)
                    
                    if viz_result.get('success'):
                        visualizations.append(viz_result)
            
            # Geographic presence
            if 'organization_profile' in report_data.data:
                org_profile = report_data.data['organization_profile']
                if org_profile.get('geographic_presence'):
                    geo_data = {}
                    for location in org_profile['geographic_presence'][:10]:
                        geo_data[location] = 1  # Equal weight for now
                    
                    viz_config = VisualizationConfig(
                        chart_type='bar',
                        title='Geographic Presence',
                        data_source='geographic_data',
                        color_scheme='default',
                        interactive=True
                    )
                    
                    viz_data = {'geographic_data': geo_data}
                    viz_result = await self.viz_engine.create_visualization(viz_config, viz_data)
                    
                    if viz_result.get('success'):
                        visualizations.append(viz_result)
            
            # Update report data with visualizations
            report_data.visualizations = visualizations
            
        except Exception as e:
            logger.error(f"Visualization generation failed: {e}")
    
    def get_available_formats(self) -> List[str]:
        """Get list of available report formats"""
        return list(self.generators.keys())
    
    def get_generator_status(self) -> Dict[str, Any]:
        """Get status of all generators"""
        return {
            'generators': {
                name: generator.get_generator_name()
                for name, generator in self.generators.items()
            },
            'libraries': {
                'reportlab': REPORTLAB_AVAILABLE,
                'docx': DOCX_AVAILABLE,
                'openpyxl': OPENPYXL_AVAILABLE,
                'plotly': PLOTLY_AVAILABLE
            },
            'config': {
                'default_format': self.default_format,
                'output_directory': self.output_directory,
                'enable_visualizations': self.enable_visualizations
            }
        }
    
    async def test_generators(self) -> Dict[str, Any]:
        """Test all generators with sample data"""
        # Create sample report data
        sample_data = ReportData(
            title="Test Report",
            organization_name="Sample Organization",
            report_type="test",
            generated_date=datetime.now(),
            data={
                'organization_profile': {
                    'name': 'Sample Organization',
                    'sector': 'Non-profit',
                    'headquarters': 'New York, USA',
                    'founded_year': 2000,
                    'website': 'https://example.org',
                    'mission_statement': 'To make the world a better place through innovative solutions.',
                    'key_focus_areas': ['Environment', 'Education', 'Health'],
                    'geographic_presence': ['United States', 'Canada', 'Mexico']
                },
                'campaigns': [
                    {
                        'title': 'Climate Action Campaign',
                        'campaign_type': 'awareness',
                        'description': 'A comprehensive campaign to raise awareness about climate change.',
                        'channels_used': ['social_media', 'digital']
                    },
                    {
                        'title': 'Education Initiative',
                        'campaign_type': 'advocacy',
                        'description': 'Advocating for better education policies.',
                        'channels_used': ['print', 'tv']
                    }
                ],
                'rfp_analysis': {
                    'qualification_score': 85,
                    'recommendation': 'high_priority',
                    'green_flags': ['Strong expertise match', 'Good geographic alignment'],
                    'red_flags': ['Tight deadline'],
                    'extracted_info': {
                        'deadline': '2024-03-15',
                        'budget': '$100,000 - $150,000',
                        'geographic_scope': ['North America'],
                        'deliverables': ['Report', 'Presentation', 'Training materials']
                    }
                }
            },
            summary="This is a test report to validate the report generation system.",
            recommendations=[
                "Proceed with proposal submission",
                "Allocate senior team members to this project",
                "Prepare detailed budget breakdown"
            ]
        )
        
        test_results = {}
        
        for format_name, generator in self.generators.items():
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Generate test report
                filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_name}"
                output_path = os.path.join(self.output_directory, filename)
                
                result_path = await generator.generate_report(sample_data, output_path)
                
                end_time = asyncio.get_event_loop().time()
                
                # Check if file was created
                file_exists = os.path.exists(result_path)
                file_size = os.path.getsize(result_path) if file_exists else 0
                
                test_results[format_name] = {
                    'status': 'success',
                    'processing_time': end_time - start_time,
                    'output_path': result_path,
                    'file_exists': file_exists,
                    'file_size_bytes': file_size,
                    'generator_name': generator.get_generator_name()
                }
                
            except Exception as e:
                test_results[format_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'generator_name': generator.get_generator_name()
                }
        
        return test_results

# Example usage and testing
async def main():
    """Example usage of Report Generation Module"""
    
    # Initialize module
    config = {
        'default_format': 'html',
        'output_directory': '/tmp/reports',
        'enable_visualizations': True
    }
    
    report_module = ReportGenerationModule(config)
    
    # Show generator status
    print("Generator Status:")
    status = report_module.get_generator_status()
    print(f"Available formats: {list(status['generators'].keys())}")
    print(f"Library availability: {status['libraries']}")
    
    # Test generators
    print("\nTesting generators...")
    test_results = await report_module.test_generators()
    print(json.dumps(test_results, indent=2, default=str))
    
    # Example comprehensive report generation
    sample_report_data = ReportData(
        title="UNICEF Organization Analysis Report",
        organization_name="UNICEF",
        report_type="organization_research",
        generated_date=datetime.now(),
        data={
            'organization_profile': {
                'name': 'UNICEF',
                'sector': 'International',
                'headquarters': 'New York, USA',
                'founded_year': 1946,
                'website': 'https://www.unicef.org',
                'mission_statement': 'UNICEF works in over 190 countries and territories to save children\'s lives, to defend their rights, and to help them fulfill their potential, from early childhood through adolescence.',
                'key_focus_areas': ['Child Protection', 'Education', 'Health', 'Nutrition', 'Water and Sanitation', 'Emergency Response'],
                'geographic_presence': ['Global', 'Africa', 'Asia', 'Europe', 'Americas', 'Middle East'],
                'leadership': [
                    {'name': 'Catherine Russell', 'title': 'Executive Director', 'bio': 'Leading UNICEF\'s global mission'}
                ],
                'partnerships': ['World Health Organization', 'World Food Programme', 'UNHCR'],
                'awards_recognition': [
                    {'title': 'Nobel Peace Prize', 'year': 1965, 'description': 'For promotion of brotherhood among nations'}
                ]
            },
            'campaigns': [
                {
                    'title': 'Every Child Alive',
                    'campaign_type': 'awareness',
                    'description': 'Global campaign to end preventable newborn deaths',
                    'channels_used': ['social_media', 'digital', 'tv'],
                    'hashtags': ['#EveryChildAlive'],
                    'success_metrics': {'reach': '50M people', 'engagement': '2M interactions'}
                },
                {
                    'title': 'Education Cannot Wait',
                    'campaign_type': 'fundraising',
                    'description': 'Emergency education funding for children in crisis',
                    'channels_used': ['digital', 'partnerships'],
                    'success_metrics': {'funds_raised': '$1.2B', 'children_reached': '7M'}
                }
            ],
            'rfp_analysis': {
                'qualification_score': 92,
                'recommendation': 'high_priority',
                'green_flags': [
                    'Strong expertise in child-focused programs',
                    'Global presence and reach',
                    'Established partnerships with UN agencies',
                    'Award-winning organization',
                    'Multimedia and digital campaign experience'
                ],
                'red_flags': [
                    'Large organization may have slower decision-making'
                ],
                'extracted_info': {
                    'deadline': '2024-04-30',
                    'budget': '$500,000 - $750,000',
                    'geographic_scope': ['Global', 'Sub-Saharan Africa'],
                    'deliverables': ['Campaign strategy', 'Creative assets', 'Digital platform', 'Impact report']
                }
            },
            'competitive_analysis': {
                'identified_competitors': ['Save the Children', 'World Vision', 'Plan International'],
                'competitive_advantages': [
                    'UN agency status and credibility',
                    'Global brand recognition',
                    'Extensive field presence',
                    'Strong digital capabilities'
                ],
                'market_position': 'Market Leader',
                'differentiation_factors': [
                    'Focus specifically on children',
                    'Emergency response expertise',
                    'Innovation in digital solutions'
                ]
            }
        },
        summary="UNICEF is a highly qualified organization for child-focused RFP opportunities. With a qualification score of 92/100, the organization demonstrates strong alignment with typical RFP requirements through its global presence, established partnerships, multimedia expertise, and award-winning track record. The organization's focus on children, emergency response capabilities, and digital innovation provide significant competitive advantages.",
        recommendations=[
            "Proceed with high-priority proposal development",
            "Leverage UNICEF's global presence and UN agency status in proposal",
            "Highlight multimedia campaign successes and digital innovation capabilities",
            "Emphasize emergency response expertise for crisis-related RFPs",
            "Consider partnership opportunities with other UN agencies",
            "Prepare case studies from 'Every Child Alive' and 'Education Cannot Wait' campaigns"
        ],
        metadata={
            'research_confidence': 0.95,
            'data_sources': ['Official website', 'Campaign databases', 'News articles'],
            'processing_time': 45.2,
            'last_updated': datetime.now().isoformat()
        }
    )
    
    print(f"\nGenerating comprehensive report for {sample_report_data.organization_name}...")
    
    # Generate in multiple formats
    formats = ['html', 'pdf'] if 'pdf' in report_module.get_available_formats() else ['html']
    generated_reports = await report_module.generate_comprehensive_report(sample_report_data, formats)
    
    print("Generated reports:")
    for format_name, path in generated_reports.items():
        if not path.startswith("Error:"):
            file_size = os.path.getsize(path) if os.path.exists(path) else 0
            print(f"- {format_name.upper()}: {path} ({file_size:,} bytes)")
        else:
            print(f"- {format_name.upper()}: {path}")

if __name__ == "__main__":
    asyncio.run(main())
