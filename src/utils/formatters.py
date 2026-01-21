"""
Formatters for displaying data in Telegram messages.
"""

from datetime import datetime
from typing import Dict, Any, List


class TelegramFormatter:
    """Format data for Telegram messages with proper markdown/HTML."""
    
    @staticmethod
    def format_statistics(stats: Dict[str, Any]) -> str:
        """
        Format statistics for Telegram display.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Formatted string with markdown
        """
        period = stats.get('period_label', 'Statistics')
        
        message = f"📊 *{period}*\n\n"
        
        # Booking counts
        message += f"📈 *Bookings Overview:*\n"
        message += f"• Total: {stats.get('total_bookings', 0)}\n"
        message += f"• Confirmed: {stats.get('confirmed', 0)} ✅\n"
        message += f"• Cancelled: {stats.get('cancelled', 0)} ❌\n"
        message += f"• Completed: {stats.get('completed', 0)} ✔️\n"
        message += f"• Pending: {stats.get('pending', 0)} ⏳\n\n"
        
        # Financial
        message += f"💰 *Revenue:*\n"
        message += f"• Total: ${stats.get('total_revenue', 0):,.2f}\n"
        message += f"• Avg per Booking: ${stats.get('average_booking_value', 0):,.2f}\n\n"
        
        # Rates
        message += f"📊 *Key Metrics:*\n"
        message += f"• Booking Rate: {stats.get('booking_rate', 0):.1f}%\n"
        message += f"• Cancellation Rate: {stats.get('cancellation_rate', 0):.1f}%\n"
        
        if 'return_rate' in stats:
            message += f"• Return Customer Rate: {stats.get('return_rate', 0):.1f}%\n"
        
        return message
    
    @staticmethod
    def format_comparison(comparison: Dict[str, Any]) -> str:
        """
        Format period comparison for Telegram.
        
        Args:
            comparison: Comparison dictionary
            
        Returns:
            Formatted string with markdown
        """
        labels = comparison.get('labels', {})
        period1 = labels.get('period1', 'Period 1')
        period2 = labels.get('period2', 'Period 2')
        changes = comparison.get('changes', {})
        
        message = f"📊 *Comparison: {period1} vs {period2}*\n\n"
        
        # Bookings change
        bookings_change = changes.get('bookings_change', 0)
        bookings_emoji = "📈" if bookings_change > 0 else "📉" if bookings_change < 0 else "➡️"
        message += f"{bookings_emoji} *Bookings:* {bookings_change:+.1f}%\n"
        
        # Revenue change
        revenue_change = changes.get('revenue_change', 0)
        revenue_emoji = "💹" if revenue_change > 0 else "💸" if revenue_change < 0 else "➡️"
        message += f"{revenue_emoji} *Revenue:* {revenue_change:+.1f}%\n"
        
        # Rate changes
        booking_rate_change = changes.get('booking_rate_change', 0)
        rate_emoji = "⬆️" if booking_rate_change > 0 else "⬇️" if booking_rate_change < 0 else "➡️"
        message += f"{rate_emoji} *Booking Rate:* {booking_rate_change:+.1f} pp\n"
        
        cancel_rate_change = changes.get('cancellation_rate_change', 0)
        # For cancellation, lower is better
        cancel_emoji = "✅" if cancel_rate_change < 0 else "⚠️" if cancel_rate_change > 0 else "➡️"
        message += f"{cancel_emoji} *Cancellation Rate:* {cancel_rate_change:+.1f} pp\n"
        
        # Add interpretation
        message += "\n💡 *Interpretation:*\n"
        if bookings_change > 5:
            message += "Strong growth in bookings! 🎉\n"
        elif bookings_change < -5:
            message += "Bookings are declining. Consider promotional activities.\n"
        
        if revenue_change > 5:
            message += "Revenue is increasing nicely! 💰\n"
        elif revenue_change < -5:
            message += "Revenue needs attention. Review pricing strategy.\n"
        
        return message
    
    @staticmethod
    def format_prediction(prediction: Dict[str, Any]) -> str:
        """
        Format prediction results for Telegram.
        
        Args:
            prediction: Prediction dictionary
            
        Returns:
            Formatted string with markdown
        """
        if not prediction.get('success'):
            return f"❌ *Prediction Error:*\n{prediction.get('error', 'Unknown error')}"
        
        summary = prediction.get('summary', {})
        method = prediction.get('method', 'Statistical Model')
        
        message = f"🔮 *Booking Prediction*\n\n"
        message += f"📊 *Method:* {method}\n\n"
        
        days = summary.get('prediction_period_days', 0)
        total = summary.get('total_predicted_bookings', 0)
        daily = summary.get('average_daily_bookings', 0)
        
        message += f"📅 *Next {days} Days:*\n"
        message += f"• Expected Bookings: {total:.0f}\n"
        message += f"• Daily Average: {daily:.1f}\n"
        message += f"• Based on: {summary.get('historical_data_days', 0)} days of data\n\n"
        
        message += "💡 *Note:* Predictions are estimates based on historical patterns. "
        message += "Actual results may vary due to seasonality, marketing, and external factors."
        
        return message
    
    @staticmethod
    def format_trends(trends: Dict[str, Any]) -> str:
        """
        Format trend analysis for Telegram.
        
        Args:
            trends: Trends dictionary
            
        Returns:
            Formatted string with markdown
        """
        if trends.get('trend') == 'insufficient_data':
            return f"❌ {trends.get('message', 'Insufficient data for trend analysis')}"
        
        trend = trends.get('trend', 'unknown')
        trend_pct = trends.get('trend_percentage', 0)
        
        trend_emoji = "📈" if trend == "increasing" else "📉"
        
        message = f"{trend_emoji} *Trend Analysis*\n\n"
        message += f"*Overall Trend:* {trend.title()} by {trend_pct:.1f}%\n\n"
        
        message += f"📊 *Period Comparison:*\n"
        message += f"• First Half Avg: {trends.get('average_first_half', 0):.1f} bookings/month\n"
        message += f"• Second Half Avg: {trends.get('average_second_half', 0):.1f} bookings/month\n\n"
        
        best = trends.get('best_month', {})
        worst = trends.get('worst_month', {})
        
        message += f"🏆 *Best Month:*\n"
        message += f"{best.get('year', '')}-{best.get('month', ''):02d}: "
        message += f"{best.get('bookings', 0)} bookings, ${best.get('revenue', 0):,.2f}\n\n"
        
        message += f"📊 *Lowest Month:*\n"
        message += f"{worst.get('year', '')}-{worst.get('month', ''):02d}: "
        message += f"{worst.get('bookings', 0)} bookings, ${worst.get('revenue', 0):,.2f}\n\n"
        
        message += f"📅 *Analysis Period:* {trends.get('total_months_analyzed', 0)} months"
        
        return message
    
    @staticmethod
    def format_cancellations(cancellations: Dict[str, Any]) -> str:
        """
        Format cancellation statistics for Telegram.
        
        Args:
            cancellations: Cancellation statistics
            
        Returns:
            Formatted string with markdown
        """
        message = "❌ *Cancellation Statistics*\n\n"
        
        message += f"📊 *Overview:*\n"
        message += f"• Total Cancelled: {cancellations.get('total_cancelled', 0)}\n"
        message += f"• Lost Revenue: ${cancellations.get('lost_revenue', 0):,.2f}\n"
        message += f"• Avg Days to Cancel: {cancellations.get('average_days_to_cancel', 0):.1f} days\n\n"
        
        reasons = cancellations.get('cancellation_reasons', {})
        if reasons:
            message += "📋 *Top Cancellation Reasons:*\n"
            sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)
            for reason, count in sorted_reasons[:5]:
                message += f"• {reason}: {count}\n"
        
        return message
    
    @staticmethod
    def format_help() -> str:
        """
        Format help message.
        
        Returns:
            Formatted help string
        """
        message = "ℹ️ *Available Commands*\n\n"
        
        message += "📊 *Statistics:*\n"
        message += "/stats - Current month statistics\n"
        message += "/compare - Compare time periods\n\n"
        
        message += "🔮 *Predictions & Trends:*\n"
        message += "/predict - Generate booking predictions\n"
        message += "/trends - Analyze trends\n\n"
        
        message += "📈 *Detailed Analysis:*\n"
        message += "/cancellations - Cancellation statistics\n"
        message += "/returns - Return customer analysis\n\n"
        
        message += "💬 *Natural Language:*\n"
        message += "You can also ask questions naturally, like:\n"
        message += "• \"How many bookings last month?\"\n"
        message += "• \"Compare this month with last year\"\n"
        message += "• \"What's our cancellation rate?\"\n"
        message += "• \"Predict bookings for next week\"\n\n"
        
        message += "/help - Show this help message"
        
        return message
    
    @staticmethod
    def format_error(error: str) -> str:
        """
        Format error message.
        
        Args:
            error: Error description
            
        Returns:
            Formatted error string
        """
        return f"❌ *Error*\n\n{error}\n\nPlease try again or use /help for guidance."
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """
        Escape special characters for Telegram markdown.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
