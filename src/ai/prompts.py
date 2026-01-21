"""
Prompt templates for AI interactions.
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for various AI tasks."""
    
    @staticmethod
    def get_analysis_prompt(site_name: str, data: Dict[str, Any]) -> str:
        """
        Get prompt for general data analysis.
        
        Args:
            site_name: Name of the booking site
            data: Data to analyze
            
        Returns:
            Formatted prompt string
        """
        return f"""You are an expert booking analytics consultant for {site_name}.
Analyze the following data and provide actionable insights:

Data: {data}

Provide:
1. Key insights (2-3 bullet points)
2. Notable trends or patterns
3. Specific recommendations
4. Any concerns or opportunities

Keep your response clear and concise."""
    
    @staticmethod
    def get_comparison_prompt(site_name: str, period1: str, period2: str, data: Dict[str, Any]) -> str:
        """
        Get prompt for period comparison analysis.
        
        Args:
            site_name: Name of the booking site
            period1: First period label
            period2: Second period label
            data: Comparison data
            
        Returns:
            Formatted prompt string
        """
        return f"""You are analyzing booking data for {site_name}.

Compare the performance between {period1} and {period2}:

{data}

Provide:
1. Assessment of overall performance change
2. Most significant changes (positive and negative)
3. Possible explanations for major changes
4. Actionable recommendations based on this comparison

Be specific and use the actual numbers in your analysis."""
    
    @staticmethod
    def get_prediction_explanation_prompt(site_name: str, prediction_data: Dict[str, Any]) -> str:
        """
        Get prompt for explaining predictions.
        
        Args:
            site_name: Name of the booking site
            prediction_data: Prediction results
            
        Returns:
            Formatted prompt string
        """
        return f"""You are a forecasting expert for {site_name}.

Explain the following booking prediction to stakeholders:

{prediction_data}

Provide:
1. Plain English explanation of what the numbers mean
2. Confidence level in this prediction
3. Key factors that could affect accuracy
4. Recommendations for using this forecast

Make it understandable for non-technical stakeholders."""
    
    @staticmethod
    def get_trend_analysis_prompt(site_name: str, trend_data: Dict[str, Any]) -> str:
        """
        Get prompt for trend analysis.
        
        Args:
            site_name: Name of the booking site
            trend_data: Trend analysis data
            
        Returns:
            Formatted prompt string
        """
        return f"""You are analyzing booking trends for {site_name}.

Trend Data:
{trend_data}

Provide:
1. Clear description of the overall trend
2. Identification of any cyclical patterns
3. Notable anomalies or inflection points
4. Strategic recommendations based on these trends

Focus on actionable insights."""
    
    @staticmethod
    def get_cancellation_analysis_prompt(site_name: str, cancellation_data: Dict[str, Any]) -> str:
        """
        Get prompt for cancellation analysis.
        
        Args:
            site_name: Name of the booking site
            cancellation_data: Cancellation statistics
            
        Returns:
            Formatted prompt string
        """
        return f"""You are analyzing cancellation patterns for {site_name}.

Cancellation Data:
{cancellation_data}

Provide:
1. Assessment of cancellation rate (is it concerning?)
2. Analysis of cancellation reasons (if available)
3. Financial impact analysis
4. Specific strategies to reduce cancellations

Be practical and specific."""
    
    @staticmethod
    def get_query_interpretation_prompt(site_name: str) -> str:
        """
        Get system prompt for natural language query interpretation.
        
        Args:
            site_name: Name of the booking site
            
        Returns:
            System prompt string
        """
        return f"""You are a query interpreter for {site_name} booking analytics bot.

Your task is to understand user queries about booking data and classify them into actions:

Available intents:
- statistics: User wants booking statistics for a period
- compare: User wants to compare two time periods
- predict: User wants booking predictions/forecasts
- trends: User wants trend analysis
- cancellations: User wants cancellation data
- returns: User wants return customer data
- help: User needs help or general information

Extract:
1. The primary intent
2. Any time periods mentioned (current month, last month, last year, etc.)
3. Any specific metrics requested

Always respond in JSON format:
{{
    "intent": "statistics",
    "time_period": "current_month",
    "specific_metrics": ["revenue", "booking_rate"]
}}"""
    
    @staticmethod
    def get_insight_generation_prompt(site_name: str, data_type: str) -> str:
        """
        Get prompt for generating concise insights.
        
        Args:
            site_name: Name of the booking site
            data_type: Type of data being analyzed
            
        Returns:
            System prompt string
        """
        return f"""You are a data insights expert for {site_name}.

Generate a brief, impactful insight from the {data_type} data provided.

Requirements:
- Maximum 2-3 sentences
- Focus on the most important finding
- Include specific numbers
- End with one actionable suggestion

Be clear, direct, and valuable."""
