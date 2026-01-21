"""
Tests for prediction service.
"""

import pytest
from src.services.predictions import PredictionService


class TestPredictionService:
    """Test cases for PredictionService."""
    
    def test_simple_moving_average_prediction(self, test_session, sample_bookings):
        """Test simple moving average prediction as fallback."""
        service = PredictionService(test_session)
        prediction = service._simple_moving_average_prediction(days_ahead=30)
        
        assert prediction is not None
        assert 'success' in prediction
        assert 'summary' in prediction or 'error' in prediction
    
    def test_predict_with_prophet_insufficient_data(self, test_session, sample_bookings):
        """Test Prophet prediction with insufficient data."""
        service = PredictionService(test_session)
        prediction = service.predict_with_prophet(days_ahead=30, historical_days=7)
        
        assert prediction is not None
        # With limited sample data, might not have enough for Prophet
        if not prediction.get('success'):
            assert 'error' in prediction
    
    def test_prediction_days_validation(self, test_session):
        """Test prediction with different day ranges."""
        service = PredictionService(test_session)
        
        # Test valid ranges
        for days in [7, 14, 30, 60, 90]:
            prediction = service._simple_moving_average_prediction(days_ahead=days)
            assert prediction is not None
    
    @pytest.mark.asyncio
    async def test_hybrid_prediction_no_llm(self, test_session, sample_bookings):
        """Test hybrid prediction without LLM client."""
        service = PredictionService(test_session, llm_client=None)
        prediction = await service.get_hybrid_prediction(days_ahead=30)
        
        assert prediction is not None
        assert 'statistical_prediction' in prediction
        assert 'recommendation' in prediction


class TestPredictionHelpers:
    """Test helper functions in prediction service."""
    
    def test_prepare_time_series_data(self, test_session, sample_bookings):
        """Test time series data preparation."""
        service = PredictionService(test_session)
        df = service._prepare_time_series_data(days_back=90)
        
        assert df is not None
        assert 'ds' in df.columns
        assert 'y' in df.columns
    
    def test_generate_recommendation(self, test_session):
        """Test recommendation generation."""
        service = PredictionService(test_session)
        
        statistical = {
            'success': True,
            'summary': {
                'total_predicted_bookings': 100,
                'prediction_period_days': 30
            }
        }
        
        recommendation = service._generate_recommendation(statistical, None)
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
