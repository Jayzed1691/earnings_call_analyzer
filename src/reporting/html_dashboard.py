"""
HTML Dashboard Generator

Creates interactive HTML dashboards with Plotly visualizations for:
- Real-time metric exploration
- Historical trend analysis
- Peer comparisons
- Interactive charts and tables

Outputs standalone HTML files that can be viewed in any browser.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
except ImportError:
    raise ImportError(
        "Phase 2C dependencies not installed. Run: pip install -r requirements-phase2c.txt"
    )


class HTMLDashboardGenerator:
    """Generates interactive HTML dashboards with Plotly visualizations"""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize dashboard generator
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        if template_dir is None:
            current_dir = Path(__file__).parent
            template_dir = str(current_dir / "templates")
        
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def generate_dashboard(
        self,
        company_name: str,
        current_analysis: Dict[str, Any],
        historical_analyses: Optional[List[Dict[str, Any]]] = None,
        peer_analyses: Optional[List[Dict[str, Any]]] = None,
        output_path: str = None
    ) -> str:
        """
        Generate an interactive HTML dashboard
        
        Args:
            company_name: Name of the company
            current_analysis: Current quarter analysis data
            historical_analyses: List of historical analysis data (optional)
            peer_analyses: List of peer company analyses (optional)
            output_path: Path to save HTML file
            
        Returns:
            Path to generated HTML file
        """
        # Set default output path
        if output_path is None:
            output_path = f"/home/claude/dashboard_{company_name.replace(' ', '_').lower()}.html"
        
        # Generate all visualizations
        charts = self._generate_all_charts(
            company_name, current_analysis, historical_analyses, peer_analyses
        )
        
        # Prepare summary statistics
        stats = self._prepare_summary_stats(current_analysis)
        
        # Render dashboard template
        template = self.env.get_template('dashboard.html')
        html_content = template.render(
            company_name=company_name,
            generation_date=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            quarter=current_analysis.get('quarter', 'N/A'),
            year=current_analysis.get('year', 'N/A'),
            summary_stats=stats,
            sentiment_gauge=charts['sentiment_gauge'],
            deception_gauge=charts['deception_gauge'],
            complexity_gauge=charts['complexity_gauge'],
            metrics_radar=charts['metrics_radar'],
            historical_trends=charts.get('historical_trends', ''),
            peer_comparison=charts.get('peer_comparison', ''),
            linguistic_markers=charts['linguistic_markers'],
            has_historical=historical_analyses is not None and len(historical_analyses) > 0,
            has_peers=peer_analyses is not None and len(peer_analyses) > 0
        )
        
        # Write to file
        output_path = str(Path(output_path).with_suffix('.html'))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _prepare_summary_stats(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare key summary statistics for dashboard header"""
        sentiment = analysis.get('sentiment', {})
        deception = analysis.get('deception_risk', {})
        complexity = analysis.get('complexity', {})
        numerical = analysis.get('numerical_transparency', {})
        
        return {
            'sentiment_score': sentiment.get('hybrid_score', 0),
            'sentiment_label': sentiment.get('label', 'N/A'),
            'deception_score': deception.get('overall_risk_score', 0),
            'deception_level': deception.get('risk_level', 'N/A'),
            'complexity_score': complexity.get('composite_score', 0),
            'complexity_level': complexity.get('level', 'N/A'),
            'transparency_score': numerical.get('transparency_score', 0),
            'word_count': analysis.get('word_count', 0),
            'sentence_count': analysis.get('sentence_count', 0),
        }
    
    def _generate_all_charts(
        self,
        company_name: str,
        current: Dict[str, Any],
        historical: Optional[List[Dict[str, Any]]],
        peers: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, str]:
        """Generate all chart visualizations as Plotly JSON"""
        charts = {}
        
        # Gauge charts for key metrics
        sentiment_score = current.get('sentiment', {}).get('hybrid_score', 0)
        charts['sentiment_gauge'] = self._create_gauge(
            sentiment_score, "Sentiment Score", 0, 100,
            low_label="Negative", high_label="Positive"
        )
        
        deception_score = current.get('deception_risk', {}).get('overall_risk_score', 0)
        charts['deception_gauge'] = self._create_gauge(
            deception_score, "Deception Risk", 0, 100,
            low_label="Low Risk", high_label="High Risk", reverse_colors=True
        )
        
        complexity_score = current.get('complexity', {}).get('composite_score', 0)
        charts['complexity_gauge'] = self._create_gauge(
            complexity_score, "Complexity Score", 0, 100,
            low_label="Simple", high_label="Complex"
        )
        
        # Radar chart for overall metrics
        charts['metrics_radar'] = self._create_metrics_radar(current)
        
        # Linguistic markers breakdown
        charts['linguistic_markers'] = self._create_linguistic_markers_chart(current)
        
        # Historical trends (if available)
        if historical and len(historical) > 0:
            charts['historical_trends'] = self._create_historical_trends(
                company_name, historical
            )
        
        # Peer comparison (if available)
        if peers and len(peers) > 0:
            charts['peer_comparison'] = self._create_peer_comparison(
                company_name, current, peers
            )
        
        return charts
    
    def _create_gauge(
        self,
        value: float,
        title: str,
        min_val: float,
        max_val: float,
        low_label: str = "",
        high_label: str = "",
        reverse_colors: bool = False
    ) -> str:
        """Create an interactive gauge chart"""
        
        # Define color steps
        if reverse_colors:
            colors = ["#28a745", "#ffc107", "#dc3545"]  # Green to red
        else:
            colors = ["#dc3545", "#ffc107", "#28a745"]  # Red to green
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title, 'font': {'size': 24}},
            delta={'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {
                    'range': [min_val, max_val],
                    'tickwidth': 1,
                    'tickcolor': "darkgray"
                },
                'bar': {'color': "#007bff", 'thickness': 0.75},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': colors[0]},
                    {'range': [40, 70], 'color': colors[1]},
                    {'range': [70, 100], 'color': colors[2]}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=60, b=20),
            font=dict(family="Arial, sans-serif", size=14),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
    
    def _create_metrics_radar(self, analysis: Dict[str, Any]) -> str:
        """Create a radar chart showing all key metrics"""
        
        # Extract normalized metrics (0-100 scale)
        sentiment = analysis.get('sentiment', {}).get('hybrid_score', 0)
        transparency = analysis.get('numerical_transparency', {}).get('transparency_score', 0)
        deception_inv = 100 - analysis.get('deception_risk', {}).get('overall_risk_score', 0)
        complexity_inv = 100 - analysis.get('complexity', {}).get('composite_score', 0)
        evasiveness_inv = 100 - analysis.get('evasiveness', {}).get('overall_score', 0)
        
        categories = [
            'Sentiment',
            'Transparency',
            'Trustworthiness',
            'Clarity',
            'Directness'
        ]
        
        values = [sentiment, transparency, deception_inv, complexity_inv, evasiveness_inv]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Company Score',
            line_color='#007bff',
            fillcolor='rgba(0, 123, 255, 0.3)'
        ))
        
        # Add benchmark line (70 = good)
        benchmark = [70] * len(categories)
        fig.add_trace(go.Scatterpolar(
            r=benchmark,
            theta=categories,
            name='Target Benchmark',
            line=dict(color='#28a745', dash='dash'),
            showlegend=True
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=12)
                ),
                angularaxis=dict(
                    tickfont=dict(size=14)
                )
            ),
            title={
                'text': "Overall Performance Metrics",
                'font': {'size': 20},
                'x': 0.5,
                'xanchor': 'center'
            },
            height=450,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5
            ),
            font=dict(family="Arial, sans-serif"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': True})
    
    def _create_linguistic_markers_chart(self, analysis: Dict[str, Any]) -> str:
        """Create bar chart for linguistic deception markers"""
        
        markers = analysis.get('deception_risk', {}).get('linguistic_markers', {})
        
        categories = ['Hedging', 'Qualifiers', 'Passive Voice', 'Distancing']
        values = [
            markers.get('hedging_density', 0),
            markers.get('qualifier_density', 0),
            markers.get('passive_voice_percentage', 0),
            markers.get('pronoun_distancing_percentage', 0)
        ]
        
        # Color code based on risk levels
        colors = ['#28a745' if v < 30 else '#ffc107' if v < 60 else '#dc3545' for v in values]
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                text=[f"{v:.1f}%" for v in values],
                textposition='outside',
                hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': "Linguistic Deception Markers",
                'font': {'size': 20},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Marker Type",
            yaxis_title="Percentage (%)",
            height=350,
            font=dict(family="Arial, sans-serif", size=14),
            yaxis=dict(range=[0, max(values) * 1.2]),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': True})
    
    def _create_historical_trends(
        self, company_name: str, historical: List[Dict[str, Any]]
    ) -> str:
        """Create line charts showing historical trends"""
        
        # Sort by quarter and year
        sorted_data = sorted(
            historical,
            key=lambda x: (x.get('year', 0), self._quarter_to_num(x.get('quarter', 'Q1')))
        )
        
        # Extract data
        quarters = [f"{d.get('quarter', '')} {d.get('year', '')}" for d in sorted_data]
        sentiments = [d.get('sentiment', {}).get('hybrid_score', 0) for d in sorted_data]
        deceptions = [d.get('deception_risk', {}).get('overall_risk_score', 0) for d in sorted_data]
        complexities = [d.get('complexity', {}).get('composite_score', 0) for d in sorted_data]
        
        # Create subplot with 3 rows
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Sentiment Trend', 'Deception Risk Trend', 'Complexity Trend'),
            vertical_spacing=0.1
        )
        
        # Sentiment trend
        fig.add_trace(
            go.Scatter(
                x=quarters, y=sentiments,
                mode='lines+markers',
                name='Sentiment',
                line=dict(color='#007bff', width=3),
                marker=dict(size=8),
                hovertemplate='%{x}<br>Score: %{y:.1f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Deception trend
        fig.add_trace(
            go.Scatter(
                x=quarters, y=deceptions,
                mode='lines+markers',
                name='Deception Risk',
                line=dict(color='#dc3545', width=3),
                marker=dict(size=8),
                hovertemplate='%{x}<br>Risk: %{y:.1f}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Complexity trend
        fig.add_trace(
            go.Scatter(
                x=quarters, y=complexities,
                mode='lines+markers',
                name='Complexity',
                line=dict(color='#ffc107', width=3),
                marker=dict(size=8),
                hovertemplate='%{x}<br>Score: %{y:.1f}<extra></extra>'
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_xaxes(title_text="Quarter", row=3, col=1)
        fig.update_yaxes(title_text="Score", range=[0, 100], row=1, col=1)
        fig.update_yaxes(title_text="Risk Level", range=[0, 100], row=2, col=1)
        fig.update_yaxes(title_text="Score", range=[0, 100], row=3, col=1)
        
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text=f"Historical Analysis Trends - {company_name}",
            title_font_size=20,
            font=dict(family="Arial, sans-serif", size=12),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="white"
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': True})
    
    def _create_peer_comparison(
        self, company_name: str, current: Dict[str, Any], peers: List[Dict[str, Any]]
    ) -> str:
        """Create grouped bar chart for peer comparison"""
        
        # Prepare data
        all_companies = [company_name] + [p.get('company_name', 'Unknown') for p in peers]
        
        sentiments = [current.get('sentiment', {}).get('hybrid_score', 0)] + \
                     [p.get('sentiment', {}).get('hybrid_score', 0) for p in peers]
        
        deceptions = [current.get('deception_risk', {}).get('overall_risk_score', 0)] + \
                     [p.get('deception_risk', {}).get('overall_risk_score', 0) for p in peers]
        
        transparencies = [current.get('numerical_transparency', {}).get('transparency_score', 0)] + \
                         [p.get('numerical_transparency', {}).get('transparency_score', 0) for p in peers]
        
        # Create grouped bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Sentiment',
            x=all_companies,
            y=sentiments,
            marker_color='#007bff',
            text=[f"{s:.1f}" for s in sentiments],
            textposition='outside',
        ))
        
        fig.add_trace(go.Bar(
            name='Transparency',
            x=all_companies,
            y=transparencies,
            marker_color='#28a745',
            text=[f"{t:.1f}" for t in transparencies],
            textposition='outside',
        ))
        
        fig.add_trace(go.Bar(
            name='Deception Risk (inverted)',
            x=all_companies,
            y=[100 - d for d in deceptions],
            marker_color='#dc3545',
            text=[f"{100-d:.1f}" for d in deceptions],
            textposition='outside',
        ))
        
        fig.update_layout(
            title={
                'text': "Peer Comparison - Key Metrics",
                'font': {'size': 20},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Company",
            yaxis_title="Score (0-100)",
            barmode='group',
            height=500,
            font=dict(family="Arial, sans-serif", size=14),
            yaxis=dict(range=[0, 110]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="white",
            hovermode='x unified'
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': True})
    
    def _quarter_to_num(self, quarter: str) -> int:
        """Convert quarter string to number for sorting"""
        quarter_map = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
        return quarter_map.get(quarter, 0)


def main():
    """Example usage"""
    
    # Example: Generate a sample dashboard
    generator = HTMLDashboardGenerator()
    
    # Mock current analysis
    current_data = {
        'sentiment': {
            'hybrid_score': 65.5,
            'label': 'Positive'
        },
        'complexity': {
            'composite_score': 55.8,
            'level': 'Moderate'
        },
        'numerical_transparency': {
            'transparency_score': 72.3
        },
        'deception_risk': {
            'overall_risk_score': 32.5,
            'risk_level': 'Low',
            'linguistic_markers': {
                'hedging_density': 7.5,
                'qualifier_density': 5.2,
                'passive_voice_percentage': 18.2,
                'pronoun_distancing_percentage': 12.3
            }
        },
        'evasiveness': {
            'overall_score': 25.8
        },
        'quarter': 'Q4',
        'year': 2024,
        'word_count': 5234,
        'sentence_count': 287
    }
    
    # Mock historical data
    historical = [
        {**current_data, 'quarter': 'Q3', 'year': 2024},
        {**current_data, 'quarter': 'Q2', 'year': 2024},
        {**current_data, 'quarter': 'Q1', 'year': 2024},
    ]
    
    output = generator.generate_dashboard(
        company_name="Example Corp",
        current_analysis=current_data,
        historical_analyses=historical,
        output_path="/home/claude/sample_dashboard.html"
    )
    
    print(f"Dashboard generated: {output}")


if __name__ == "__main__":
    main()
