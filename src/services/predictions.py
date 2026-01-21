"""
Prediction service combining statistical models and AI analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from src.database.queries import get_daily_booking_counts, get_monthly_trend_data

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for generating booking predictions using hybrid approach."""
    
    def __init__(self, session: Session, llm_client=None):
        """
        Initialize prediction service.
        
        Args:
            session: Database session
            llm_client: Optional LLM client for AI-powered insights
        """
        self.session = session
        self.llm_client = llm_client
    
    def _prepare_time_series_data(
        self,
        days_back: int = 90
    ) -> pd.DataFrame:
        """
        Prepare time series data for prediction models.
        
        Args:
            days_back: Number of days of historical data
            
        Returns:
            DataFrame with date and booking count
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        daily_counts = get_daily_booking_counts(self.session, start_date, end_date)
        
        df = pd.DataFrame(daily_counts, columns=['ds', 'y'])
        df['ds'] = pd.to_datetime(df['ds'])
        
        return df
    
    def predict_with_prophet(
        self,
        days_ahead: int = 30,
        historical_days: int = 90
    ) -> Dict[str, Any]:
        """
        Generate predictions using Facebook Prophet.
        
        Args:
            days_ahead: Number of days to predict
            historical_days: Days of historical data to use
            
        Returns:
            Dictionary with predictions and confidence intervals
        """
        try:
            from prophet import Prophet
            
            df = self._prepare_time_series_data(historical_days)
            
            if len(df) < 14:
                return {
                    "success": False,
                    "error": "Insufficient historical data (need at least 14 days)"
                }
            
            # Initialize and fit Prophet model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False if len(df) < 365 else True,
                interval_width=0.95
            )
            
            model.fit(df)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=days_ahead)
            forecast = model.predict(future)
            
            # Extract predictions
            predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
            
            # Calculate summary statistics
            total_predicted = predictions['yhat'].sum()
            avg_daily_predicted = predictions['yhat'].mean()
            
            return {
                "success": True,
                "method": "Prophet",
                "predictions": predictions.to_dict('records'),
                "summary": {
                    "total_predicted_bookings": round(total_predicted, 0),
                    "average_daily_bookings": round(avg_daily_predicted, 2),
                    "prediction_period_days": days_ahead,
                    "historical_data_days": len(df)
                }
            }
        except ImportError:
            logger.warning("Prophet not available, falling back to simple moving average")
            return self._simple_moving_average_prediction(days_ahead, historical_days)
        except Exception as e:
            logger.error(f"Error in Prophet prediction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def predict_with_statsmodels(
        self,
        days_ahead: int = 30,
        historical_days: int = 90
    ) -> Dict[str, Any]:
        """
        Generate predictions using ARIMA from statsmodels.
        
        Args:
            days_ahead: Number of days to predict
            historical_days: Days of historical data to use
            
        Returns:
            Dictionary with predictions
        """
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            df = self._prepare_time_series_data(historical_days)
            
            if len(df) < 14:
                return {
                    "success": False,
                    "error": "Insufficient historical data (need at least 14 days)"
                }
            
            # Fit ARIMA model
            model = ARIMA(df['y'], order=(1, 1, 1))
            fitted = model.fit()
            
            # Generate forecast
            forecast = fitted.forecast(steps=days_ahead)
            
            # Ensure no negative predictions
            forecast = np.maximum(forecast, 0)
            
            total_predicted = forecast.sum()
            avg_daily_predicted = forecast.mean()
            
            return {
                "success": True,
                "method": "ARIMA",
                "summary": {
                    "total_predicted_bookings": round(total_predicted, 0),
                    "average_daily_bookings": round(avg_daily_predicted, 2),
                    "prediction_period_days": days_ahead,
                    "historical_data_days": len(df)
                }
            }
        except ImportError:
            logger.warning("Statsmodels not available, falling back to simple method")
            return self._simple_moving_average_prediction(days_ahead, historical_days)
        except Exception as e:
            logger.error(f"Error in ARIMA prediction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _simple_moving_average_prediction(
        self,
        days_ahead: int = 30,
        historical_days: int = 30
    ) -> Dict[str, Any]:
        """
        Simple moving average prediction as fallback.
        
        Args:
            days_ahead: Number of days to predict
            historical_days: Days of historical data to use
            
        Returns:
            Dictionary with predictions
        """
        try:
            df = self._prepare_time_series_data(historical_days)
            
            if len(df) == 0:
                return {
                    "success": False,
                    "error": "No historical data available"
                }
            
            # Calculate average daily bookings
            avg_daily = df['y'].mean()
            
            # Simple prediction: extend average forward
            total_predicted = avg_daily * days_ahead
            
            return {
                "success": True,
                "method": "Moving Average (Fallback)",
                "summary": {
                    "total_predicted_bookings": round(total_predicted, 0),
                    "average_daily_bookings": round(avg_daily, 2),
                    "prediction_period_days": days_ahead,
                    "historical_data_days": len(df)
                }
            }
        except Exception as e:
            logger.error(f"Error in simple prediction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def predict_with_ai_insights(
        self,
        days_ahead: int = 30,
        statistical_prediction: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered prediction insights using LLM.
        
        Args:
            days_ahead: Number of days to predict
            statistical_prediction: Optional statistical prediction to enhance
            
        Returns:
            Dictionary with AI insights and predictions
        """
        if not self.llm_client:
            return {
                "success": False,
                "error": "LLM client not configured"
            }
        
        try:
            # Get historical data for context
            monthly_data = get_monthly_trend_data(self.session, months=12)
            
            # Create context for LLM
            context = {
                "historical_data": monthly_data,
                "statistical_prediction": statistical_prediction,
                "days_ahead": days_ahead
            }
            
            # Get AI analysis
            ai_response = await self.llm_client.analyze_booking_trends(context)
            
            return {
                "success": True,
                "method": "AI Analysis",
                "ai_insights": ai_response,
                "statistical_baseline": statistical_prediction
            }
        except Exception as e:
            logger.error(f"Error in AI prediction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_hybrid_prediction(
        self,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Generate hybrid prediction combining statistical models and AI.
        
        Args:
            days_ahead: Number of days to predict
            
        Returns:
            Dictionary with comprehensive prediction
        """
        # Get statistical prediction (try Prophet first, fallback to simpler methods)
        statistical = self.predict_with_prophet(days_ahead)
        
        if not statistical.get("success"):
            statistical = self._simple_moving_average_prediction(days_ahead)
        
        # Get AI insights if available
        ai_insights = None
        if self.llm_client:
            ai_insights = await self.predict_with_ai_insights(days_ahead, statistical)
        
        return {
            "statistical_prediction": statistical,
            "ai_insights": ai_insights,
            "recommendation": self._generate_recommendation(statistical, ai_insights)
        }
    
    def _generate_recommendation(
        self,
        statistical: Dict[str, Any],
        ai_insights: Optional[Dict[str, Any]]
    ) -> str:
        """Generate actionable recommendation from predictions."""
        if not statistical.get("success"):
            return "Unable to generate predictions due to insufficient data."
        
        summary = statistical.get("summary", {})
        total = summary.get("total_predicted_bookings", 0)
        
        base_recommendation = f"Based on statistical analysis, expect approximately {int(total)} bookings in the next {summary.get('prediction_period_days', 0)} days."
        
        if ai_insights and ai_insights.get("success"):
            return f"{base_recommendation}\n\nAI Insights: {ai_insights.get('ai_insights', {}).get('summary', '')}"
        
        return base_recommendation
