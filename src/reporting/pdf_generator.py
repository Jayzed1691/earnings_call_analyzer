"""
PDF Report Generator

Generates professional PDF reports for earnings call analysis with:
- Executive summary
- Key metrics visualizations
- Historical trend charts
- Peer comparison tables
- Risk analysis sections

Uses Jinja2 templates and WeasyPrint for HTML-to-PDF conversion.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    from weasyprint import HTML, CSS
    import plotly.graph_objects as go
    import plotly.io as pio
except ImportError:
    raise ImportError(
        "Phase 2C dependencies not installed. Run: pip install -r requirements-phase2c.txt"
    )


class PDFReportGenerator:
    """Generates professional PDF reports from earnings call analysis data"""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize PDF generator
        
        Args:
            template_dir: Directory containing Jinja2 templates (default: src/reporting/templates)
        """
        if template_dir is None:
            # Default to templates directory next to this file
            current_dir = Path(__file__).parent
            template_dir = str(current_dir / "templates")
        
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Configure Plotly for static image export
        pio.kaleido.scope.mathjax = None
    
    def generate_report(
        self,
        company_name: str,
        analysis_data: Dict[str, Any],
        output_path: str,
        include_charts: bool = True,
        include_historical: bool = True,
        peer_data: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate a comprehensive PDF report
        
        Args:
            company_name: Name of the company
            analysis_data: Analysis results dictionary
            output_path: Path to save the PDF report
            include_charts: Whether to include visualization charts
            include_historical: Whether to include historical trend analysis
            peer_data: Optional peer comparison data
            
        Returns:
            Path to generated PDF file
        """
        # Prepare data for template
        report_data = self._prepare_report_data(
            company_name, analysis_data, include_historical, peer_data
        )
        
        # Generate charts if requested
        chart_images = {}
        if include_charts:
            chart_images = self._generate_charts(analysis_data, peer_data)
        
        # Render HTML from template
        template = self.env.get_template('report_template.html')
        html_content = template.render(
            company_name=company_name,
            report_data=report_data,
            charts=chart_images,
            generation_date=datetime.now().strftime("%B %d, %Y"),
            include_historical=include_historical,
            has_peer_data=peer_data is not None
        )
        
        # Convert HTML to PDF
        output_path = str(Path(output_path).with_suffix('.pdf'))
        HTML(string=html_content, base_url=self.template_dir).write_pdf(
            output_path,
            stylesheets=[self._get_pdf_styles()]
        )
        
        return output_path
    
    def _prepare_report_data(
        self,
        company_name: str,
        analysis_data: Dict[str, Any],
        include_historical: bool,
        peer_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Prepare and structure data for the report template"""
        
        # Extract key metrics
        sentiment = analysis_data.get('sentiment', {})
        complexity = analysis_data.get('complexity', {})
        numerical = analysis_data.get('numerical_transparency', {})
        deception = analysis_data.get('deception_risk', {})
        evasiveness = analysis_data.get('evasiveness', {})
        
        # Build executive summary
        executive_summary = self._build_executive_summary(
            sentiment, complexity, numerical, deception, evasiveness
        )
        
        # Organize metrics by category
        metrics = {
            'sentiment': self._format_sentiment_metrics(sentiment),
            'complexity': self._format_complexity_metrics(complexity),
            'numerical': self._format_numerical_metrics(numerical),
            'deception': self._format_deception_metrics(deception),
            'evasiveness': self._format_evasiveness_metrics(evasiveness),
        }
        
        # Extract insights
        insights = analysis_data.get('insights', {})
        
        # Prepare peer comparison if available
        peer_comparison = None
        if peer_data:
            peer_comparison = self._format_peer_comparison(peer_data)
        
        return {
            'executive_summary': executive_summary,
            'metrics': metrics,
            'insights': insights,
            'peer_comparison': peer_comparison,
            'quarter': analysis_data.get('quarter', 'N/A'),
            'year': analysis_data.get('year', 'N/A'),
            'word_count': analysis_data.get('word_count', 0),
            'sentence_count': analysis_data.get('sentence_count', 0),
        }
    
    def _build_executive_summary(
        self, sentiment, complexity, numerical, deception, evasiveness
    ) -> Dict[str, str]:
        """Build executive summary with key takeaways"""
        
        # Overall assessment
        sentiment_score = sentiment.get('hybrid_score', 0)
        deception_score = deception.get('overall_risk_score', 0)
        
        if sentiment_score >= 60 and deception_score < 40:
            overall = "Positive and transparent communication"
        elif sentiment_score < 40 or deception_score >= 60:
            overall = "Concerns identified - closer scrutiny recommended"
        else:
            overall = "Mixed signals - standard due diligence advised"
        
        # Key highlights
        highlights = []
        
        if sentiment_score >= 60:
            highlights.append(f"Positive sentiment ({sentiment_score:.1f}/100)")
        elif sentiment_score < 40:
            highlights.append(f"Concerning sentiment ({sentiment_score:.1f}/100)")
        
        if deception_score < 30:
            highlights.append("Low deception risk indicators")
        elif deception_score >= 60:
            highlights.append(f"Elevated deception risk ({deception_score:.1f}/100)")
        
        complexity_level = complexity.get('level', 'N/A')
        if complexity_level in ['High', 'Moderate']:
            highlights.append(f"{complexity_level} language complexity")
        
        return {
            'overall_assessment': overall,
            'highlights': highlights,
        }
    
    def _format_sentiment_metrics(self, sentiment: Dict) -> List[Dict[str, Any]]:
        """Format sentiment metrics for display"""
        return [
            {
                'name': 'Overall Sentiment',
                'value': f"{sentiment.get('hybrid_score', 0):.1f}",
                'unit': '/100',
                'interpretation': sentiment.get('label', 'N/A'),
                'color': self._get_sentiment_color(sentiment.get('hybrid_score', 0))
            },
            {
                'name': 'Lexicon Analysis',
                'value': f"{sentiment.get('lexicon_net_positivity', 0):.2f}",
                'unit': '',
                'interpretation': 'Net positive tone',
                'color': '#6c757d'
            },
            {
                'name': 'LLM Assessment',
                'value': f"{sentiment.get('llm_sentiment_score', 0):.1f}",
                'unit': '/100',
                'interpretation': 'AI-detected sentiment',
                'color': '#6c757d'
            },
        ]
    
    def _format_complexity_metrics(self, complexity: Dict) -> List[Dict[str, Any]]:
        """Format complexity metrics for display"""
        return [
            {
                'name': 'Overall Complexity',
                'value': f"{complexity.get('composite_score', 0):.1f}",
                'unit': '/100',
                'interpretation': complexity.get('level', 'N/A'),
                'color': self._get_complexity_color(complexity.get('level', ''))
            },
            {
                'name': 'Reading Ease',
                'value': f"{complexity.get('flesch_reading_ease', 0):.1f}",
                'unit': '',
                'interpretation': self._interpret_flesch(complexity.get('flesch_reading_ease', 0)),
                'color': '#6c757d'
            },
            {
                'name': 'Grade Level',
                'value': f"{complexity.get('flesch_kincaid_grade', 0):.1f}",
                'unit': '',
                'interpretation': 'Education level required',
                'color': '#6c757d'
            },
        ]
    
    def _format_numerical_metrics(self, numerical: Dict) -> List[Dict[str, Any]]:
        """Format numerical transparency metrics for display"""
        return [
            {
                'name': 'Transparency Score',
                'value': f"{numerical.get('transparency_score', 0):.1f}",
                'unit': '/100',
                'interpretation': 'Numerical clarity',
                'color': self._get_transparency_color(numerical.get('transparency_score', 0))
            },
            {
                'name': 'Specificity Index',
                'value': f"{numerical.get('specificity_index', 0):.2f}",
                'unit': '',
                'interpretation': 'Detail level',
                'color': '#6c757d'
            },
            {
                'name': 'Forward Guidance',
                'value': f"{numerical.get('forward_looking_density', 0):.1f}",
                'unit': '%',
                'interpretation': 'Future-focused',
                'color': '#6c757d'
            },
        ]
    
    def _format_deception_metrics(self, deception: Dict) -> List[Dict[str, Any]]:
        """Format deception risk metrics for display"""
        markers = deception.get('linguistic_markers', {})
        return [
            {
                'name': 'Deception Risk',
                'value': f"{deception.get('overall_risk_score', 0):.1f}",
                'unit': '/100',
                'interpretation': deception.get('risk_level', 'N/A'),
                'color': self._get_risk_color(deception.get('overall_risk_score', 0))
            },
            {
                'name': 'Hedging Density',
                'value': f"{markers.get('hedging_density', 0):.1f}",
                'unit': '%',
                'interpretation': 'Uncertainty language',
                'color': '#6c757d'
            },
            {
                'name': 'Passive Voice',
                'value': f"{markers.get('passive_voice_percentage', 0):.1f}",
                'unit': '%',
                'interpretation': 'Responsibility avoidance',
                'color': '#6c757d'
            },
        ]
    
    def _format_evasiveness_metrics(self, evasiveness: Dict) -> List[Dict[str, Any]]:
        """Format evasiveness metrics for display"""
        return [
            {
                'name': 'Evasiveness Score',
                'value': f"{evasiveness.get('overall_score', 0):.1f}",
                'unit': '/100',
                'interpretation': evasiveness.get('level', 'N/A'),
                'color': self._get_risk_color(evasiveness.get('overall_score', 0))
            },
        ]
    
    def _format_peer_comparison(self, peer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format peer comparison data"""
        return {
            'companies': [p.get('company_name', 'Unknown') for p in peer_data],
            'metrics': self._extract_peer_metrics(peer_data),
        }
    
    def _extract_peer_metrics(self, peer_data: List[Dict[str, Any]]) -> Dict[str, List]:
        """Extract comparable metrics across peers"""
        metrics = {
            'sentiment': [],
            'deception_risk': [],
            'complexity': [],
        }
        
        for peer in peer_data:
            metrics['sentiment'].append(peer.get('sentiment', {}).get('hybrid_score', 0))
            metrics['deception_risk'].append(peer.get('deception_risk', {}).get('overall_risk_score', 0))
            metrics['complexity'].append(peer.get('complexity', {}).get('composite_score', 0))
        
        return metrics
    
    def _generate_charts(
        self, analysis_data: Dict[str, Any], peer_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, str]:
        """Generate chart images for the report"""
        charts = {}
        
        # Sentiment gauge chart
        sentiment_score = analysis_data.get('sentiment', {}).get('hybrid_score', 0)
        charts['sentiment_gauge'] = self._create_gauge_chart(
            sentiment_score, "Sentiment Score", "Negative", "Positive"
        )
        
        # Deception risk gauge
        deception_score = analysis_data.get('deception_risk', {}).get('overall_risk_score', 0)
        charts['deception_gauge'] = self._create_gauge_chart(
            deception_score, "Deception Risk", "Low", "High", reverse_colors=True
        )
        
        # Peer comparison chart (if available)
        if peer_data:
            charts['peer_comparison'] = self._create_peer_comparison_chart(
                analysis_data, peer_data
            )
        
        return charts
    
    def _create_gauge_chart(
        self, value: float, title: str, low_label: str, high_label: str,
        reverse_colors: bool = False
    ) -> str:
        """Create a gauge chart and return as base64 image"""
        
        # Color ranges
        if reverse_colors:
            colors = ["#28a745", "#ffc107", "#dc3545"]  # Green, yellow, red
        else:
            colors = ["#dc3545", "#ffc107", "#28a745"]  # Red, yellow, green
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title, 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': colors[0]},
                    {'range': [40, 70], 'color': colors[1]},
                    {'range': [70, 100], 'color': colors[2]}
                ],
            }
        ))
        
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(size=12)
        )
        
        # Convert to base64 image
        img_bytes = fig.to_image(format="png", width=400, height=250)
        import base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    
    def _create_peer_comparison_chart(
        self, analysis_data: Dict[str, Any], peer_data: List[Dict[str, Any]]
    ) -> str:
        """Create a peer comparison bar chart"""
        
        companies = [p.get('company_name', 'Unknown') for p in peer_data]
        sentiments = [p.get('sentiment', {}).get('hybrid_score', 0) for p in peer_data]
        
        fig = go.Figure(data=[
            go.Bar(
                x=companies,
                y=sentiments,
                marker_color=['#007bff' if i == 0 else '#6c757d' for i in range(len(companies))],
                text=[f"{s:.1f}" for s in sentiments],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Sentiment Score Comparison",
            xaxis_title="Company",
            yaxis_title="Sentiment Score",
            height=300,
            margin=dict(l=40, r=20, t=60, b=40),
            showlegend=False,
            yaxis=dict(range=[0, 100])
        )
        
        # Convert to base64 image
        img_bytes = fig.to_image(format="png", width=600, height=300)
        import base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    
    def _get_pdf_styles(self) -> CSS:
        """Get CSS styles for PDF generation"""
        css_content = """
        @page {
            size: Letter;
            margin: 1in;
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            margin-top: 25px;
        }
        
        h3 {
            color: #7f8c8d;
            margin-top: 20px;
        }
        
        .metric-card {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            background-color: #f8f9fa;
            page-break-inside: avoid;
        }
        
        .metric-value {
            font-size: 24pt;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .chart-container {
            text-align: center;
            page-break-inside: avoid;
            margin: 20px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            page-break-inside: avoid;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        
        .executive-summary {
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .red-flag {
            color: #dc3545;
            font-weight: bold;
        }
        
        .strength {
            color: #28a745;
            font-weight: bold;
        }
        
        ul, ol {
            margin: 10px 0;
            padding-left: 25px;
        }
        
        li {
            margin: 5px 0;
        }
        """
        return CSS(string=css_content)
    
    # Helper methods for color coding
    def _get_sentiment_color(self, score: float) -> str:
        """Get color based on sentiment score"""
        if score >= 60:
            return '#28a745'  # Green
        elif score >= 40:
            return '#ffc107'  # Yellow
        else:
            return '#dc3545'  # Red
    
    def _get_complexity_color(self, level: str) -> str:
        """Get color based on complexity level"""
        if level == 'Low':
            return '#28a745'
        elif level == 'Moderate':
            return '#ffc107'
        else:
            return '#dc3545'
    
    def _get_transparency_color(self, score: float) -> str:
        """Get color based on transparency score"""
        if score >= 70:
            return '#28a745'
        elif score >= 50:
            return '#ffc107'
        else:
            return '#dc3545'
    
    def _get_risk_color(self, score: float) -> str:
        """Get color based on risk score (reversed)"""
        if score < 40:
            return '#28a745'
        elif score < 60:
            return '#ffc107'
        else:
            return '#dc3545'
    
    def _interpret_flesch(self, score: float) -> str:
        """Interpret Flesch Reading Ease score"""
        if score >= 80:
            return "Very Easy"
        elif score >= 60:
            return "Easy"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"


def main():
    """Example usage"""
    import sys
    
    # Example: Generate a sample report
    generator = PDFReportGenerator()
    
    # Mock analysis data
    sample_data = {
        'sentiment': {
            'hybrid_score': 65.5,
            'label': 'Positive',
            'lexicon_net_positivity': 0.15,
            'llm_sentiment_score': 68.2
        },
        'complexity': {
            'composite_score': 55.8,
            'level': 'Moderate',
            'flesch_reading_ease': 45.2,
            'flesch_kincaid_grade': 12.5
        },
        'numerical_transparency': {
            'transparency_score': 72.3,
            'specificity_index': 0.78,
            'forward_looking_density': 3.2
        },
        'deception_risk': {
            'overall_risk_score': 32.5,
            'risk_level': 'Low',
            'linguistic_markers': {
                'hedging_density': 7.5,
                'passive_voice_percentage': 18.2
            }
        },
        'evasiveness': {
            'overall_score': 25.8,
            'level': 'Low'
        },
        'insights': {
            'key_findings': [
                'Strong revenue growth',
                'Positive guidance'
            ],
            'red_flags': [],
            'strengths': [
                'Clear communication',
                'Transparent metrics'
            ]
        },
        'quarter': 'Q4',
        'year': 2024,
        'word_count': 5234,
        'sentence_count': 287
    }
    
    output = generator.generate_report(
        company_name="Example Corp",
        analysis_data=sample_data,
        output_path="/home/claude/sample_report.pdf"
    )
    
    print(f"Report generated: {output}")


if __name__ == "__main__":
    main()
