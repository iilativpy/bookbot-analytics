"""
LangChain agent for natural language interaction with booking analytics.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from config import get_config
from src.services.statistics import StatisticsService
from src.services.analytics import AnalyticsService
from src.services.predictions import PredictionService

logger = logging.getLogger(__name__)


class BookingAnalyticsAgent:
    """
    LangChain agent for natural language booking analytics queries.
    Uses OpenRouter as the LLM backend.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the booking analytics agent.
        
        Args:
            session: Database session
        """
        self.session = session
        self.config = get_config()
        
        # Initialize services
        self.stats_service = StatisticsService(session)
        self.analytics_service = AnalyticsService(session)
        self.prediction_service = PredictionService(session)
        
        # Initialize LLM with OpenRouter
        self.llm = self._create_llm()
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent_executor = self._create_agent()
        
        logger.info("BookingAnalyticsAgent initialized")
    
    def _create_llm(self) -> ChatOpenAI:
        """
        Create LangChain LLM instance using OpenRouter.
        
        Returns:
            ChatOpenAI instance configured for OpenRouter
        """
        return ChatOpenAI(
            model=self.config.openrouter_model,
            openai_api_key=self.config.openrouter_api_key,
            openai_api_base=self.config.openrouter_base_url,
            temperature=0.7,
            max_tokens=1000
        )
    
    def _create_tools(self) -> List[Tool]:
        """
        Create LangChain tools for the agent.
        
        Returns:
            List of Tool objects
        """
        tools = [
            Tool(
                name="get_current_month_statistics",
                func=self._tool_current_month_stats,
                description="Get booking statistics for the current month including total bookings, revenue, rates, etc."
            ),
            Tool(
                name="get_last_month_statistics",
                func=self._tool_last_month_stats,
                description="Get booking statistics for the previous month"
            ),
            Tool(
                name="compare_with_last_month",
                func=self._tool_compare_last_month,
                description="Compare current month statistics with last month and show changes"
            ),
            Tool(
                name="compare_with_last_year",
                func=self._tool_compare_last_year,
                description="Compare current month with the same month last year (year-over-year comparison)"
            ),
            Tool(
                name="get_cancellation_statistics",
                func=self._tool_cancellation_stats,
                description="Get detailed cancellation statistics including rates, reasons, and lost revenue"
            ),
            Tool(
                name="get_return_customer_rate",
                func=self._tool_return_customer_stats,
                description="Get return customer statistics and retention rates"
            ),
            Tool(
                name="get_trend_analysis",
                func=self._tool_trend_analysis,
                description="Analyze booking trends over the past 6-12 months"
            ),
            Tool(
                name="generate_prediction",
                func=self._tool_generate_prediction,
                description="Generate booking predictions for upcoming days/weeks using statistical models"
            ),
        ]
        return tools
    
    def _tool_current_month_stats(self, query: str = "") -> str:
        """Tool: Get current month statistics."""
        try:
            stats = self.stats_service.get_current_month_stats()
            return self._format_stats(stats)
        except Exception as e:
            logger.error(f"Error in current month stats tool: {e}")
            return f"Error retrieving statistics: {str(e)}"
    
    def _tool_last_month_stats(self, query: str = "") -> str:
        """Tool: Get last month statistics."""
        try:
            stats = self.stats_service.get_last_month_stats()
            return self._format_stats(stats)
        except Exception as e:
            logger.error(f"Error in last month stats tool: {e}")
            return f"Error retrieving statistics: {str(e)}"
    
    def _tool_compare_last_month(self, query: str = "") -> str:
        """Tool: Compare with last month."""
        try:
            comparison = self.analytics_service.compare_with_last_month()
            return self._format_comparison(comparison)
        except Exception as e:
            logger.error(f"Error in comparison tool: {e}")
            return f"Error performing comparison: {str(e)}"
    
    def _tool_compare_last_year(self, query: str = "") -> str:
        """Tool: Compare with last year."""
        try:
            comparison = self.analytics_service.compare_with_last_year()
            return self._format_comparison(comparison)
        except Exception as e:
            logger.error(f"Error in year comparison tool: {e}")
            return f"Error performing comparison: {str(e)}"
    
    def _tool_cancellation_stats(self, query: str = "") -> str:
        """Tool: Get cancellation statistics."""
        try:
            stats = self.stats_service.get_cancellation_stats()
            return f"""Cancellation Statistics:
- Total Cancelled: {stats['total_cancelled']}
- Lost Revenue: ${stats['lost_revenue']:.2f}
- Avg Days to Cancel: {stats['average_days_to_cancel']:.1f} days
- Reasons: {stats.get('cancellation_reasons', {})}"""
        except Exception as e:
            logger.error(f"Error in cancellation stats tool: {e}")
            return f"Error retrieving cancellation statistics: {str(e)}"
    
    def _tool_return_customer_stats(self, query: str = "") -> str:
        """Tool: Get return customer statistics."""
        try:
            current_stats = self.stats_service.get_current_month_stats()
            return f"""Return Customer Statistics:
- Total Customers: {current_stats.get('total_customers', 0)}
- Return Customers: {current_stats.get('return_customers', 0)}
- New Customers: {current_stats.get('new_customers', 0)}
- Return Rate: {current_stats.get('return_rate', 0):.2f}%"""
        except Exception as e:
            logger.error(f"Error in return customer stats tool: {e}")
            return f"Error retrieving return customer statistics: {str(e)}"
    
    def _tool_trend_analysis(self, query: str = "") -> str:
        """Tool: Analyze trends."""
        try:
            trends = self.analytics_service.identify_trends(months=6)
            trend_dir = trends.get('trend', 'unknown')
            trend_pct = trends.get('trend_percentage', 0)
            
            best = trends.get('best_month', {})
            worst = trends.get('worst_month', {})
            
            return f"""Trend Analysis (Last 6 Months):
- Overall Trend: {trend_dir} by {trend_pct:.1f}%
- Best Month: {best.get('year', '')}-{best.get('month', '')} with {best.get('bookings', 0)} bookings
- Worst Month: {worst.get('year', '')}-{worst.get('month', '')} with {worst.get('bookings', 0)} bookings
- First Half Avg: {trends.get('average_first_half', 0):.1f} bookings/month
- Second Half Avg: {trends.get('average_second_half', 0):.1f} bookings/month"""
        except Exception as e:
            logger.error(f"Error in trend analysis tool: {e}")
            return f"Error analyzing trends: {str(e)}"
    
    def _tool_generate_prediction(self, query: str = "30") -> str:
        """Tool: Generate predictions."""
        try:
            # Extract number of days from query if present
            import re
            match = re.search(r'\d+', query)
            days = int(match.group()) if match else 30
            days = min(max(days, 7), 90)  # Clamp between 7 and 90 days
            
            prediction = self.prediction_service.predict_with_prophet(days_ahead=days)
            
            if not prediction.get("success"):
                return f"Unable to generate prediction: {prediction.get('error', 'Unknown error')}"
            
            summary = prediction.get("summary", {})
            return f"""Booking Prediction (Next {days} Days):
- Method: {prediction.get('method', 'Unknown')}
- Total Predicted Bookings: {summary.get('total_predicted_bookings', 0):.0f}
- Average Daily Bookings: {summary.get('average_daily_bookings', 0):.2f}
- Based on: {summary.get('historical_data_days', 0)} days of historical data"""
        except Exception as e:
            logger.error(f"Error in prediction tool: {e}")
            return f"Error generating prediction: {str(e)}"
    
    def _format_stats(self, stats: Dict[str, Any]) -> str:
        """Format statistics for display."""
        return f"""{stats.get('period_label', 'Statistics')}:
- Total Bookings: {stats.get('total_bookings', 0)}
- Confirmed: {stats.get('confirmed', 0)}
- Cancelled: {stats.get('cancelled', 0)}
- Completed: {stats.get('completed', 0)}
- Total Revenue: ${stats.get('total_revenue', 0):.2f}
- Average Booking Value: ${stats.get('average_booking_value', 0):.2f}
- Booking Rate: {stats.get('booking_rate', 0):.2f}%
- Cancellation Rate: {stats.get('cancellation_rate', 0):.2f}%
- Return Customer Rate: {stats.get('return_rate', 0):.2f}%"""
    
    def _format_comparison(self, comparison: Dict[str, Any]) -> str:
        """Format comparison data."""
        labels = comparison.get('labels', {})
        changes = comparison.get('changes', {})
        
        return f"""Comparison: {labels.get('period1')} vs {labels.get('period2')}

Changes:
- Bookings: {changes.get('bookings_change', 0):+.2f}%
- Revenue: {changes.get('revenue_change', 0):+.2f}%
- Booking Rate: {changes.get('booking_rate_change', 0):+.2f} percentage points
- Cancellation Rate: {changes.get('cancellation_rate_change', 0):+.2f} percentage points"""
    
    def _create_agent(self) -> AgentExecutor:
        """
        Create LangChain agent with tools.
        
        Returns:
            AgentExecutor instance
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a helpful booking analytics assistant for {self.config.site_name}.
You have access to tools to retrieve booking statistics, compare periods, analyze trends, and generate predictions.

When users ask questions about bookings, use the appropriate tools to get accurate data.
Always provide clear, concise answers with specific numbers and insights.

Available capabilities:
- Current and historical statistics
- Period comparisons (month-over-month, year-over-year)
- Cancellation analysis
- Return customer metrics
- Trend analysis
- Booking predictions"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    async def process_query(self, query: str) -> str:
        """
        Process a natural language query.
        
        Args:
            query: User's natural language query
            
        Returns:
            Response string
        """
        try:
            result = await self.agent_executor.ainvoke({"input": query})
            return result.get("output", "I couldn't process that query.")
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
