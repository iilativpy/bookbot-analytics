"""
OpenRouter API client for LLM interactions.
Configurable model selection - defaults to deepseek/deepseek-v3.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx
from config import get_config

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Client for OpenRouter API with universal model support.
    Model can be easily changed in configuration.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (defaults to config)
            model: Model identifier (defaults to config, which defaults to deepseek/deepseek-v3)
        """
        config = get_config()
        self.api_key = api_key or config.openrouter_api_key
        self.model = model or config.openrouter_model
        self.base_url = config.openrouter_base_url
        self.site_name = config.site_name
        
        logger.info(f"OpenRouter client initialized with model: {self.model}")
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send completion request to OpenRouter.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters for the API
            
        Returns:
            API response dictionary
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": f"https://{self.site_name}",  # Optional
            "X-Title": f"{self.site_name} Booking Bot"     # Optional
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenRouter client: {e}")
            raise
    
    async def analyze_booking_trends(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze booking trends using AI.
        
        Args:
            context: Dictionary with historical data and context
            
        Returns:
            Dictionary with AI analysis
        """
        historical_data = context.get("historical_data", [])
        statistical_prediction = context.get("statistical_prediction", {})
        days_ahead = context.get("days_ahead", 30)
        
        # Format historical data for prompt
        data_summary = "\n".join([
            f"- {m['year']}-{m['month']:02d}: {m['bookings']} bookings, ${m['revenue']:.2f} revenue"
            for m in historical_data[-6:]  # Last 6 months
        ])
        
        stat_summary = ""
        if statistical_prediction and statistical_prediction.get("success"):
            summary = statistical_prediction.get("summary", {})
            stat_summary = f"""
Statistical Model Prediction ({statistical_prediction.get('method', 'Unknown')}):
- Predicted total bookings for next {days_ahead} days: {summary.get('total_predicted_bookings', 0)}
- Average daily bookings: {summary.get('average_daily_bookings', 0)}
"""
        
        prompt = f"""You are an expert booking analytics consultant for {self.site_name}. 
Analyze the following booking data and provide insights:

Recent Historical Data (last 6 months):
{data_summary}

{stat_summary}

Please provide:
1. Key trends you observe
2. Factors that might be influencing bookings
3. Recommendations for improving booking rates
4. Your assessment of the statistical prediction
5. Any concerns or opportunities you see

Keep your response concise and actionable."""
        
        messages = [
            {
                "role": "system",
                "content": f"You are an expert data analyst specializing in booking analytics for {self.site_name}. Provide clear, actionable insights."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = await self.complete(messages, temperature=0.7, max_tokens=800)
            
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "analysis": content,
                "model_used": self.model,
                "summary": content.split('\n\n')[0] if content else "No analysis available"
            }
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {
                "error": str(e),
                "analysis": "Unable to generate AI analysis at this time."
            }
    
    async def interpret_natural_language_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Interpret natural language query to determine intent and parameters.
        
        Args:
            query: User's natural language query
            conversation_history: Optional conversation context
            
        Returns:
            Dictionary with interpreted intent and parameters
        """
        system_prompt = f"""You are a query interpreter for {self.site_name} booking analytics bot.
Your job is to understand user queries and extract:
1. intent: The user's goal (e.g., "get_statistics", "compare_periods", "predict", "trends", "cancellations", "returns")
2. parameters: Any specific parameters (e.g., time periods, comparison types)

Return your response in JSON format like:
{{
    "intent": "get_statistics",
    "parameters": {{"period": "current_month"}},
    "confidence": 0.95
}}

Available intents:
- get_statistics: Get booking statistics for a period
- compare_periods: Compare two time periods
- predict: Generate booking predictions
- trends: Analyze trends
- cancellations: Get cancellation statistics
- returns: Get return customer statistics
- help: Get help information
"""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages for context
        
        messages.append({"role": "user", "content": query})
        
        try:
            response = await self.complete(messages, temperature=0.3, max_tokens=200)
            
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Fallback: extract intent from text
                intent = "get_statistics"
                if "compare" in query.lower():
                    intent = "compare_periods"
                elif "predict" in query.lower() or "forecast" in query.lower():
                    intent = "predict"
                elif "trend" in query.lower():
                    intent = "trends"
                elif "cancel" in query.lower():
                    intent = "cancellations"
                elif "return" in query.lower():
                    intent = "returns"
                
                return {
                    "intent": intent,
                    "parameters": {},
                    "confidence": 0.5,
                    "raw_response": content
                }
        except Exception as e:
            logger.error(f"Error interpreting query: {e}")
            return {
                "intent": "error",
                "error": str(e)
            }
    
    async def generate_insights(
        self,
        data: Dict[str, Any],
        query_type: str
    ) -> str:
        """
        Generate natural language insights from data.
        
        Args:
            data: Data dictionary to analyze
            query_type: Type of query (statistics, comparison, etc.)
            
        Returns:
            Natural language insights
        """
        import json
        
        data_str = json.dumps(data, indent=2, default=str)
        
        prompt = f"""Based on the following {query_type} data for {self.site_name}, provide a brief, 
insightful summary in 2-3 sentences. Focus on the most important findings and actionable insights.

Data:
{data_str}

Provide a clear, concise analysis:"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a data analyst providing concise, actionable insights."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = await self.complete(messages, temperature=0.7, max_tokens=200)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content if content else "Analysis complete."
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return "Data analysis complete. See details above."
