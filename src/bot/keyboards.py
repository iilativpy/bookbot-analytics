"""
Inline keyboard factories for Telegram bot UI.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardFactory:
    """Factory for creating inline keyboards."""
    
    @staticmethod
    def get_main_menu() -> InlineKeyboardMarkup:
        """
        Get main menu keyboard.
        
        Returns:
            InlineKeyboardMarkup with main menu options
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Current Stats", callback_data="stats_current"),
                InlineKeyboardButton("📈 Trends", callback_data="trends")
            ],
            [
                InlineKeyboardButton("🔮 Predictions", callback_data="predict"),
                InlineKeyboardButton("⚖️ Compare", callback_data="compare_menu")
            ],
            [
                InlineKeyboardButton("❌ Cancellations", callback_data="cancellations"),
                InlineKeyboardButton("🔄 Returns", callback_data="returns")
            ],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_comparison_menu() -> InlineKeyboardMarkup:
        """
        Get comparison options keyboard.
        
        Returns:
            InlineKeyboardMarkup with comparison options
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 vs Last Month", callback_data="compare_last_month")
            ],
            [
                InlineKeyboardButton("📆 vs Last Year", callback_data="compare_last_year")
            ],
            [
                InlineKeyboardButton("📊 Year-to-Date", callback_data="compare_ytd")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_prediction_menu() -> InlineKeyboardMarkup:
        """
        Get prediction period selection keyboard.
        
        Returns:
            InlineKeyboardMarkup with prediction period options
        """
        keyboard = [
            [
                InlineKeyboardButton("7 Days", callback_data="predict_7"),
                InlineKeyboardButton("14 Days", callback_data="predict_14")
            ],
            [
                InlineKeyboardButton("30 Days", callback_data="predict_30"),
                InlineKeyboardButton("60 Days", callback_data="predict_60")
            ],
            [
                InlineKeyboardButton("90 Days", callback_data="predict_90")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_stats_menu() -> InlineKeyboardMarkup:
        """
        Get statistics period selection keyboard.
        
        Returns:
            InlineKeyboardMarkup with stats period options
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Current Month", callback_data="stats_current"),
                InlineKeyboardButton("📆 Last Month", callback_data="stats_last")
            ],
            [
                InlineKeyboardButton("📊 Year to Date", callback_data="stats_ytd")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button() -> InlineKeyboardMarkup:
        """
        Get simple back button.
        
        Returns:
            InlineKeyboardMarkup with back button
        """
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_trends_menu() -> InlineKeyboardMarkup:
        """
        Get trends analysis period keyboard.
        
        Returns:
            InlineKeyboardMarkup with trend period options
        """
        keyboard = [
            [
                InlineKeyboardButton("3 Months", callback_data="trends_3"),
                InlineKeyboardButton("6 Months", callback_data="trends_6")
            ],
            [
                InlineKeyboardButton("12 Months", callback_data="trends_12")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
