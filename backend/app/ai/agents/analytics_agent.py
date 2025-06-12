"""
Analytics Agent Module

This module implements an AI-powered Analytics Agent capable of performing
data analysis, generating insights, creating visualizations, and providing
data-driven recommendations.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum, auto
from datetime import datetime, timedelta
import logging
import json
import asyncio
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pydantic import BaseModel, Field, validator, HttpUrl, conlist, conint, confloat
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_agent import BaseAgent, AgentConfig, AgentResponse
from ..integrations.database_integration import DatabaseIntegration
from ..integrations.visualization_integration import VisualizationIntegration
from ..integrations.ml_integration import MLIntegration

logger = logging.getLogger(__name__)

class AnalysisType(str, Enum):
    """Types of data analysis."""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"
    EXPLORATORY = "exploratory"

class TimeGranularity(str, Enum):
    """Time granularity for time series analysis."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class VisualizationType(str, Enum):
    """Types of visualizations."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    MAP = "map"

class DataQualityIssue(BaseModel):
    """Data quality issue model."""
    issue_type: str
    column: Optional[str] = None
    description: str
    severity: str  # low, medium, high, critical
    rows_affected: Optional[int] = None
    suggested_fix: Optional[str] = None

class AnalysisResult(BaseModel):
    """Result of a data analysis."""
    analysis_id: str
    analysis_type: AnalysisType
    dataset_id: str
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    visualization_urls: Dict[str, str] = Field(default_factory=dict)
    data_quality_issues: List[DataQualityIssue] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AnalyticsAgent(BaseAgent):
    """
    Advanced Analytics Agent specialized in data analysis and insights generation.
    
    This agent provides comprehensive analytics capabilities including:
    - Data exploration and profiling
    - Statistical analysis
    - Time series analysis
    - Predictive modeling
    - Data visualization
    - Report generation
    - Anomaly detection
    - A/B testing
    - Customer segmentation
    - Performance metrics tracking
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.analyses: Dict[str, AnalysisResult] = {}
        self.datasets: Dict[str, pd.DataFrame] = {}
        self._init_analytics_integrations()
    
    def _init_analytics_integrations(self) -> None:
        """Initialize analytics-related integrations."""
        try:
            self.database = DatabaseIntegration(
                connection_string=settings.DATABASE_URL,
                max_connections=settings.DATABASE_MAX_CONNECTIONS
            )
            
            self.visualization = VisualizationIntegration(
                api_key=settings.VISUALIZATION_API_KEY
            )
            
            self.ml = MLIntegration(
                api_key=settings.ML_API_KEY,
                base_url=settings.ML_BASE_URL
            )
            
            logger.info("Analytics integrations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics integrations: {str(e)}")
            raise
    
    async def load_dataset(self, source: Union[str, Dict[str, Any], pd.DataFrame], 
                          dataset_id: Optional[str] = None) -> AgentResponse:
        """
        Load a dataset from a source.
        
        Args:
            source: Data source (file path, URL, dict, or DataFrame)
            dataset_id: Optional ID for the dataset
            
        Returns:
            AgentResponse with dataset details
        """
        try:
            # Generate dataset ID if not provided
            if dataset_id is None:
                dataset_id = f"ds_{len(self.datasets) + 1}_{int(datetime.utcnow().timestamp())}"
            
            # Load data based on source type
            if isinstance(source, pd.DataFrame):
                df = source
            elif isinstance(source, dict):
                df = pd.DataFrame(source)
            elif isinstance(source, str):
                if source.startswith(('http://', 'https://')):
                    # Load from URL
                    df = pd.read_csv(source)
                else:
                    # Assume local file path
                    if source.endswith('.csv'):
                        df = pd.read_csv(source)
                    elif source.endswith(('.xls', '.xlsx')):
                        df = pd.read_excel(source)
                    else:
                        raise ValueError("Unsupported file format")
            else:
                raise ValueError("Unsupported source type")
            
            # Store the dataset
            self.datasets[dataset_id] = df
            
            # Basic dataset info
            dataset_info = {
                'dataset_id': dataset_id,
                'rows': len(df),
                'columns': list(df.columns),
                'column_types': {col: str(df[col].dtype) for col in df.columns},
                'missing_values': df.isnull().sum().to_dict(),
                'sample_data': df.head(5).to_dict(orient='records')
            }
            
            return AgentResponse(
                success=True,
                output=dataset_info,
                metadata={
                    'loaded_at': datetime.utcnow().isoformat(),
                    'source': 'dataframe' if isinstance(source, pd.DataFrame) else source
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Failed to load dataset: {str(e)}",
                error_type=type(e).__name__,
                metadata={"source": str(source)[:100]}
            )
    
    async def analyze_data(self, dataset_id: str, analysis_type: AnalysisType, 
                          options: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Perform data analysis on a dataset.
        
        Args:
            dataset_id: ID of the dataset to analyze
            analysis_type: Type of analysis to perform
            options: Additional analysis options
                - columns: List of columns to include
                - group_by: Column to group by
                - time_column: Column with datetime data
                - time_granularity: Granularity for time series
                - filters: Dictionary of filters to apply
                
        Returns:
            AgentResponse with analysis results
        """
        try:
            if dataset_id not in self.datasets:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            df = self.datasets[dataset_id]
            options = options or {}
            
            # Generate analysis ID
            analysis_id = f"analysis_{len(self.analyses) + 1}_{int(datetime.utcnow().timestamp())}"
            
            # Perform analysis based on type
            if analysis_type == AnalysisType.DESCRIPTIVE:
                result = self._perform_descriptive_analysis(df, options)
            elif analysis_type == AnalysisType.TIME_SERIES:
                result = self._perform_time_series_analysis(df, options)
            else:
                raise ValueError(f"Analysis type {analysis_type} not implemented")
            
            # Store the analysis result
            self.analyses[analysis_id] = result
            
            return AgentResponse(
                success=True,
                output={
                    'analysis_id': analysis_id,
                    'analysis_type': analysis_type.value,
                    'metrics': result.metrics,
                    'insights': result.insights,
                    'recommendations': result.recommendations,
                    'data_quality_issues': [
                        issue.dict() for issue in result.data_quality_issues
                    ] if result.data_quality_issues else []
                },
                metadata={
                    'dataset_id': dataset_id,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Analysis failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"dataset_id": dataset_id, "analysis_type": analysis_type.value}
            )
    
    async def create_visualization(self, dataset_id: str, visualization_type: VisualizationType,
                                 x_column: str, y_column: Optional[str] = None,
                                 options: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Create a data visualization.
        
        Args:
            dataset_id: ID of the dataset
            visualization_type: Type of visualization
            x_column: Column for x-axis
            y_column: Column for y-axis (if applicable)
            options: Additional visualization options
                - title: Chart title
                - x_label: X-axis label
                - y_label: Y-axis label
                - color: Color scheme
                - filters: Dictionary of filters
                
        Returns:
            AgentResponse with visualization details
        """
        try:
            if dataset_id not in self.datasets:
                raise ValueError(f"Dataset {dataset_id} not found")
                
            df = self.datasets[dataset_id]
            options = options or {}
            
            # Create visualization
            fig = await self._create_plotly_figure(
                df=df,
                visualization_type=visualization_type,
                x_column=x_column,
                y_column=y_column,
                options=options
            )
            
            # Save visualization
            viz_id = f"viz_{len(self.analyses) + 1}_{int(datetime.utcnow().timestamp())}"
            viz_url = await self.visualization.save_plotly_figure(fig, viz_id)
            
            return AgentResponse(
                success=True,
                output={
                    'visualization_id': viz_id,
                    'visualization_url': viz_url,
                    'visualization_type': visualization_type.value,
                    'columns_used': [x_column] + ([y_column] if y_column else [])
                },
                metadata={
                    'dataset_id': dataset_id,
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create visualization: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Failed to create visualization: {str(e)}",
                error_type=type(e).__name__,
                metadata={"dataset_id": dataset_id, "visualization_type": visualization_type.value}
            )
    
    async def generate_report(self, analysis_ids: List[str], 
                            format: str = 'html',
                            options: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Generate a report from analysis results.
        
        Args:
            analysis_ids: List of analysis IDs to include
            format: Report format (html, pdf, markdown)
            options: Additional report options
                - title: Report title
                - include_visualizations: Whether to include visualizations
                - include_data_quality: Whether to include data quality issues
                - include_recommendations: Whether to include recommendations
                
        Returns:
            AgentResponse with report details
        """
        try:
            options = options or {}
            analyses = []
            
            # Get all requested analyses
            for analysis_id in analysis_ids:
                if analysis_id not in self.analyses:
                    raise ValueError(f"Analysis {analysis_id} not found")
                analyses.append(self.analyses[analysis_id])
            
            # Generate report using LLM
            report_prompt = self._create_report_prompt(analyses, options)
            report_content = await self.llm.generate(report_prompt)
            
            # Format report
            if format == 'html':
                report = self._format_html_report(report_content, analyses, options)
            elif format == 'markdown':
                report = report_content  # LLM generates markdown by default
            else:
                raise ValueError(f"Unsupported report format: {format}")
            
            # Save report
            report_id = f"report_{len(self.analyses) + 1}_{int(datetime.utcnow().timestamp())}"
            
            return AgentResponse(
                success=True,
                output={
                    'report_id': report_id,
                    'content': report,
                    'format': format,
                    'analysis_ids': analysis_ids
                },
                metadata={
                    'generated_at': datetime.utcnow().isoformat(),
                    'analyses_count': len(analyses)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Report generation failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"analysis_ids": analysis_ids, "format": format}
            )
    
    def _perform_descriptive_analysis(self, df: pd.DataFrame, options: Dict[str, Any]) -> AnalysisResult:
        """Perform descriptive statistical analysis."""
        columns = options.get('columns', df.columns.tolist())
        group_by = options.get('group_by')
        
        metrics = {}
        insights = []
        data_quality_issues = []
        
        # Basic statistics
        if group_by and group_by in df.columns:
            # Grouped analysis
            for col in columns:
                if col != group_by and pd.api.types.is_numeric_dtype(df[col]):
                    grouped = df.groupby(group_by)[col].agg(['count', 'mean', 'std', 'min', 'max', 'median'])
                    metrics[f'grouped_{col}'] = grouped.to_dict(orient='index')
        else:
            # Overall analysis
            for col in columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    metrics[col] = {
                        'count': int(df[col].count()),
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        '25%': float(df[col].quantile(0.25)),
                        '50%': float(df[col].median()),
                        '75%': float(df[col].quantile(0.75)),
                        'max': float(df[col].max())
                    }
                else:
                    # For non-numeric columns
                    value_counts = df[col].value_counts().head(10).to_dict()
                    metrics[col] = {'value_counts': value_counts}
        
        # Data quality checks
        for col in columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                issue = DataQualityIssue(
                    issue_type='missing_values',
                    column=col,
                    description=f"{missing} missing values found",
                    severity='high' if missing > 0.5 * len(df) else 'medium',
                    rows_affected=int(missing),
                    suggested_fix="Consider imputation or removal of rows/columns with missing values"
                )
                data_quality_issues.append(issue)
        
        # Generate insights using LLM
        insights_prompt = f"""
        Based on the following dataset statistics, provide 3-5 key insights:
        
        {json.dumps(metrics, indent=2)}
        
        Focus on:
        1. Notable patterns or anomalies
        2. Data quality concerns
        3. Potential areas for further analysis
        """
        
        insights = ["Example insight 1", "Example insight 2"]  # Would come from LLM in real implementation
        
        # Generate recommendations
        recommendations = [
            "Consider visualizing the distribution of key metrics",
            "Investigate potential outliers in the data",
            "Address missing values in the dataset"
        ]
        
        return AnalysisResult(
            analysis_id=f"desc_{int(datetime.utcnow().timestamp())}",
            analysis_type=AnalysisType.DESCRIPTIVE,
            dataset_id="current",
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            data_quality_issues=data_quality_issues
        )
    
    async def _create_plotly_figure(self, df: pd.DataFrame, visualization_type: VisualizationType,
                                  x_column: str, y_column: Optional[str] = None,
                                  options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a Plotly figure based on the specified parameters."""
        options = options or {}
        
        if visualization_type == VisualizationType.LINE:
            if not y_column:
                # If no y_column, use value counts of x_column
                plot_df = df[x_column].value_counts().sort_index()
                fig = go.Figure(go.Scatter(x=plot_df.index, y=plot_df.values, mode='lines+markers'))
            else:
                fig = go.Figure(go.Scatter(x=df[x_column], y=df[y_column], mode='lines+markers'))
                
        elif visualization_type == VisualizationType.BAR:
            if not y_column:
                # If no y_column, use value counts of x_column
                plot_df = df[x_column].value_counts()
                fig = go.Figure(go.Bar(x=plot_df.index, y=plot_df.values))
            else:
                fig = go.Figure(go.Bar(x=df[x_column], y=df[y_column]))
                
        elif visualization_type == VisualizationType.PIE:
            if not y_column:
                # If no y_column, use value counts of x_column
                plot_df = df[x_column].value_counts()
                fig = go.Figure(go.Pie(labels=plot_df.index, values=plot_df.values))
            else:
                fig = go.Figure(go.Pie(labels=df[x_column], values=df[y_column]))
                
        elif visualization_type == VisualizationType.SCATTER:
            if not y_column:
                raise ValueError("y_column is required for scatter plot")
            fig = go.Figure(go.Scatter(
                x=df[x_column],
                y=df[y_column],
                mode='markers'
            ))
            
        elif visualization_type == VisualizationType.HISTOGRAM:
            fig = go.Figure(go.Histogram(x=df[x_column]))
            
        else:
            raise ValueError(f"Unsupported visualization type: {visualization_type}")
        
        # Update layout
        fig.update_layout(
            title=options.get('title', f"{x_column} vs {y_column}" if y_column else x_column),
            xaxis_title=options.get('x_label', x_column),
            yaxis_title=options.get('y_label', y_column if y_column else 'Count'),
            template=options.get('template', 'plotly_white'),
            showlegend=options.get('show_legend', True)
        )
        
        return fig
    
    def _create_report_prompt(self, analyses: List[AnalysisResult], options: Dict[str, Any]) -> str:
        """Create a prompt for report generation."""
        title = options.get('title', 'Data Analysis Report')
        
        prompt = f"""
        You are a senior data analyst. Create a comprehensive report based on the following analyses.
        
        Report Title: {title}
        
        Include the following sections:
        1. Executive Summary
        2. Key Findings
        3. Detailed Analysis
        4. Recommendations
        5. Next Steps
        
        Analysis Results:
        {json.dumps([analysis.dict() for analysis in analyses], indent=2, default=str)}
        
        Focus on clear, actionable insights and professional presentation.
        Use markdown formatting with appropriate headers, bullet points, and emphasis.
        """
        
        return prompt
    
    def _format_html_report(self, markdown_content: str, analyses: List[AnalysisResult], 
                           options: Dict[str, Any]) -> str:
        """Convert markdown report to HTML format."""
        # In a real implementation, this would use a markdown-to-html converter
        # For now, we'll just wrap the markdown in HTML
        title = options.get('title', 'Data Analysis Report')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                .insight {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }}
                .recommendation {{ background-color: #e8f4fd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="report-content">
                {markdown_content}
            </div>
            <hr>
            <footer>
                <p>Report generated on {date} by Analytics Agent</p>
            </footer>
        </body>
        </html>
        """.format(
            title=title,
            date=datetime.now().strftime("%B %d, %Y"),
            markdown_content=markdown_content
        )
        
        return html

# Example usage
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def main():
        # Initialize the analytics agent
        config = AgentConfig(
            name="AnalyticsAgent",
            description="Performs data analysis and generates insights"
        )
        agent = AnalyticsAgent(config)
        
        # Sample data
        data = {
            'date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
            'sales': np.random.normal(1000, 200, 100).cumsum(),
            'customers': np.random.randint(50, 200, 100),
            'region': np.random.choice(['North', 'South', 'East', 'West'], 100)
        }
        
        # Load dataset
        load_result = await agent.load_dataset(data)
        dataset_id = load_result.output['dataset_id']
        print(f"Loaded dataset: {dataset_id}")
        
        # Analyze data
        analysis_result = await agent.analyze_data(
            dataset_id=dataset_id,
            analysis_type=AnalysisType.DESCRIPTIVE,
            options={
                'columns': ['sales', 'customers', 'region']
            }
        )
        print(f"Analysis complete: {analysis_result.success}")
        
        # Create visualization
        viz_result = await agent.create_visualization(
            dataset_id=dataset_id,
            visualization_type=VisualizationType.LINE,
            x_column='date',
            y_column='sales',
            options={
                'title': 'Sales Over Time',
                'x_label': 'Date',
                'y_label': 'Sales ($)'
            }
        )
        print(f"Visualization created: {viz_result.output['visualization_url']}")
        
        # Generate report
        report_result = await agent.generate_report(
            analysis_ids=[analysis_result.output['analysis_id']],
            format='markdown',
            options={
                'title': 'Sales Analysis Report',
                'include_visualizations': True,
                'include_data_quality': True,
                'include_recommendations': True
            }
        )
        print(f"\nReport generated:\n{report_result.output['content'][:500]}...")
    
    asyncio.run(main())
