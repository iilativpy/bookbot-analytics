"""
Telegram bot message handlers.
Supports both command-based and natural language interactions.
"""

import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from sqlalchemy.orm import Session

from config import get_config
from src.database import get_session
from src.services import StatisticsService, AnalyticsService, PredictionService
from src.ai import OpenRouterClient, BookingAnalyticsAgent
from src.utils import TelegramFormatter, QueryValidator
from .keyboards import KeyboardFactory
from .commands import BotCommands

logger = logging.getLogger(__name__)


class BotHandlers:
    """
    Telegram bot handlers for commands and natural language queries.
    Integrates with services and AI components.
    """
    
    def __init__(self):
        """Initialize bot handlers."""
        self.config = get_config()
        self.formatter = TelegramFormatter()
        self.validator = QueryValidator()
        self.keyboards = KeyboardFactory()
        
        # Initialize OpenRouter client
        self.llm_client = OpenRouterClient()
        
        logger.info("BotHandlers initialized")
    
    def _get_services(self, session: Session):
        """
        Get service instances with session.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (stats, analytics, prediction) services
        """
        stats = StatisticsService(session)
        analytics = AnalyticsService(session)
        prediction = PredictionService(session, self.llm_client)
        return stats, analytics, prediction
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome = self.config.get_welcome_message()
        await update.message.reply_text(
            welcome,
            reply_markup=self.keyboards.get_main_menu()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = self.formatter.format_help()
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=self.keyboards.get_back_button()
        )
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command."""
        await update.message.reply_text(
            "📊 *Main Menu*\n\nChoose an option:",
            parse_mode='Markdown',
            reply_markup=self.keyboards.get_main_menu()
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        try:
            # Send processing message
            processing_msg = await update.message.reply_text("📊 Fetching statistics...")
            
            with next(get_session()) as session:
                stats_service, _, _ = self._get_services(session)
                stats = stats_service.get_current_month_stats()
            
            message = self.formatter.format_statistics(stats)
            
            await processing_msg.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=self.keyboards.get_back_button()
            )
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await update.message.reply_text(
                self.formatter.format_error(str(e)),
                parse_mode='Markdown'
            )
    
    async def compare_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /compare command."""
        await update.message.reply_text(
            "📊 *Choose Comparison Type*",
            parse_mode='Markdown',
            reply_markup=self.keyboards.get_comparison_menu()
        )
    
    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /predict command."""
        await update.message.reply_text(
            "🔮 *Select Prediction Period*",
            parse_mode='Markdown',
            reply_markup=self.keyboards.get_prediction_menu()
        )
    
    async def trends_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trends command."""
        await update.message.reply_text(
            "📈 *Select Analysis Period*",
            parse_mode='Markdown',
            reply_markup=self.keyboards.get_trends_menu()
        )
    
    async def cancellations_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancellations command."""
        try:
            processing_msg = await update.message.reply_text("❌ Fetching cancellation data...")
            
            with next(get_session()) as session:
                stats_service, _, _ = self._get_services(session)
                cancellations = stats_service.get_cancellation_stats()
            
            message = self.formatter.format_cancellations(cancellations)
            
            await processing_msg.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=self.keyboards.get_back_button()
            )
        except Exception as e:
            logger.error(f"Error in cancellations command: {e}")
            await update.message.reply_text(
                self.formatter.format_error(str(e)),
                parse_mode='Markdown'
            )
    
    async def returns_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /returns command."""
        try:
            processing_msg = await update.message.reply_text("🔄 Fetching return customer data...")
            
            with next(get_session()) as session:
                stats_service, _, _ = self._get_services(session)
                stats = stats_service.get_current_month_stats()
            
            message = f"""🔄 *Return Customer Statistics*

📊 *Current Month:*
• Total Customers: {stats.get('total_customers', 0)}
• Return Customers: {stats.get('return_customers', 0)}
• New Customers: {stats.get('new_customers', 0)}
• Return Rate: {stats.get('return_rate', 0):.1f}%

💡 *Insight:*
"""
            
            if stats.get('return_rate', 0) > 30:
                message += "Excellent customer retention! 🎉"
            elif stats.get('return_rate', 0) > 15:
                message += "Good retention rate. Consider loyalty programs to improve."
            else:
                message += "Focus on customer retention strategies needed."
            
            await processing_msg.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=self.keyboards.get_back_button()
            )
        except Exception as e:
            logger.error(f"Error in returns command: {e}")
            await update.message.reply_text(
                self.formatter.format_error(str(e)),
                parse_mode='Markdown'
            )
    
    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button callbacks."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        try:
            # Main menu
            if data == "main_menu":
                await query.edit_message_text(
                    "📊 *Main Menu*\n\nChoose an option:",
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_main_menu()
                )
            
            # Stats
            elif data == "stats_current":
                await query.edit_message_text("📊 Fetching statistics...")
                with next(get_session()) as session:
                    stats_service, _, _ = self._get_services(session)
                    stats = stats_service.get_current_month_stats()
                message = self.formatter.format_statistics(stats)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            elif data == "stats_last":
                await query.edit_message_text("📊 Fetching statistics...")
                with next(get_session()) as session:
                    stats_service, _, _ = self._get_services(session)
                    stats = stats_service.get_last_month_stats()
                message = self.formatter.format_statistics(stats)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            elif data == "stats_ytd":
                await query.edit_message_text("📊 Fetching statistics...")
                with next(get_session()) as session:
                    stats_service, _, _ = self._get_services(session)
                    stats = stats_service.get_year_to_date_stats()
                message = self.formatter.format_statistics(stats)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            # Comparisons
            elif data == "compare_menu":
                await query.edit_message_text(
                    "📊 *Choose Comparison Type*",
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_comparison_menu()
                )
            
            elif data == "compare_last_month":
                await query.edit_message_text("⚖️ Comparing periods...")
                with next(get_session()) as session:
                    _, analytics, _ = self._get_services(session)
                    comparison = analytics.compare_with_last_month()
                message = self.formatter.format_comparison(comparison)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            elif data == "compare_last_year":
                await query.edit_message_text("⚖️ Comparing periods...")
                with next(get_session()) as session:
                    _, analytics, _ = self._get_services(session)
                    comparison = analytics.compare_with_last_year()
                message = self.formatter.format_comparison(comparison)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            elif data == "compare_ytd":
                await query.edit_message_text("⚖️ Comparing periods...")
                with next(get_session()) as session:
                    _, analytics, _ = self._get_services(session)
                    comparison = analytics.compare_year_to_date()
                message = self.formatter.format_comparison(comparison)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            # Predictions
            elif data == "predict":
                await query.edit_message_text(
                    "🔮 *Select Prediction Period*",
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_prediction_menu()
                )
            
            elif data.startswith("predict_"):
                days = int(data.split("_")[1])
                await query.edit_message_text(f"🔮 Generating {days}-day prediction...")
                with next(get_session()) as session:
                    _, _, prediction_service = self._get_services(session)
                    prediction = prediction_service.predict_with_prophet(days_ahead=days)
                message = self.formatter.format_prediction(prediction)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            # Trends
            elif data == "trends":
                await query.edit_message_text(
                    "📈 *Select Analysis Period*",
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_trends_menu()
                )
            
            elif data.startswith("trends_"):
                months = int(data.split("_")[1])
                await query.edit_message_text(f"📈 Analyzing {months}-month trends...")
                with next(get_session()) as session:
                    _, analytics, _ = self._get_services(session)
                    trends = analytics.identify_trends(months=months)
                message = self.formatter.format_trends(trends)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            # Cancellations and Returns
            elif data == "cancellations":
                await query.edit_message_text("❌ Fetching cancellation data...")
                with next(get_session()) as session:
                    stats_service, _, _ = self._get_services(session)
                    cancellations = stats_service.get_cancellation_stats()
                message = self.formatter.format_cancellations(cancellations)
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            elif data == "returns":
                await query.edit_message_text("🔄 Fetching return customer data...")
                with next(get_session()) as session:
                    stats_service, _, _ = self._get_services(session)
                    stats = stats_service.get_current_month_stats()
                
                message = f"""🔄 *Return Customer Statistics*

📊 *Current Month:*
• Total Customers: {stats.get('total_customers', 0)}
• Return Customers: {stats.get('return_customers', 0)}
• New Customers: {stats.get('new_customers', 0)}
• Return Rate: {stats.get('return_rate', 0):.1f}%"""
                
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
            
            # Help
            elif data == "help":
                help_text = self.formatter.format_help()
                await query.edit_message_text(
                    help_text,
                    parse_mode='Markdown',
                    reply_markup=self.keyboards.get_back_button()
                )
        
        except Exception as e:
            logger.error(f"Error in callback query handler: {e}")
            await query.edit_message_text(
                self.formatter.format_error(str(e)),
                parse_mode='Markdown'
            )
    
    async def natural_language_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language queries using LangChain agent."""
        try:
            user_query = update.message.text
            
            # Sanitize input
            user_query = self.validator.sanitize_input(user_query)
            
            # Send processing message
            processing_msg = await update.message.reply_text("🤔 Analyzing your query...")
            
            # Use LangChain agent for natural language processing
            with next(get_session()) as session:
                agent = BookingAnalyticsAgent(session)
                response = await agent.process_query(user_query)
            
            await processing_msg.edit_text(
                response,
                parse_mode='Markdown',
                reply_markup=self.keyboards.get_back_button()
            )
        
        except Exception as e:
            logger.error(f"Error in natural language handler: {e}")
            await update.message.reply_text(
                self.formatter.format_error(
                    "I couldn't process that query. Please try rephrasing or use a command."
                ),
                parse_mode='Markdown'
            )
    
    def setup_application(self, token: str) -> Application:
        """
        Setup and configure the Telegram application.
        
        Args:
            token: Telegram bot token
            
        Returns:
            Configured Application instance
        """
        # Create application
        application = Application.builder().token(token).build()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("menu", self.menu_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("compare", self.compare_command))
        application.add_handler(CommandHandler("predict", self.predict_command))
        application.add_handler(CommandHandler("trends", self.trends_command))
        application.add_handler(CommandHandler("cancellations", self.cancellations_command))
        application.add_handler(CommandHandler("returns", self.returns_command))
        
        # Register callback query handler
        application.add_handler(CallbackQueryHandler(self.callback_query_handler))
        
        # Register natural language handler (for non-command messages)
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.natural_language_handler
            )
        )
        
        logger.info("Telegram application configured")
        return application
    
    @staticmethod
    async def setup_bot_commands(application: Application):
        """
        Set up bot commands for the Telegram UI.
        
        Args:
            application: Telegram Application instance
        """
        commands = [
            BotCommand(cmd, desc)
            for cmd, desc in BotCommands.get_bot_commands()
        ]
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands set up")
