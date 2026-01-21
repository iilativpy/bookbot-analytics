"""
Main entry point for the Telegram Booking Statistics Bot.
"""

import asyncio
import logging
import sys
from config import get_config
from src.database import init_db
from src.bot.handlers import BotHandlers


# Configure logging
def setup_logging():
    """Configure application logging."""
    config = get_config()
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, config.log_level),
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('bot.log')
        ]
    )
    
    # Reduce noise from some libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.INFO)


async def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = get_config()
        logger.info(f"Starting {config.site_name} Booking Bot")
        logger.info(f"Using LLM model: {config.openrouter_model}")
        
        # Initialize database
        logger.info("Initializing database connection...")
        init_db()
        logger.info("Database initialized")
        
        # Create bot handlers
        logger.info("Setting up bot handlers...")
        handlers = BotHandlers()
        
        # Setup application
        application = handlers.setup_application(config.telegram_bot_token)
        
        # Set up bot commands
        await handlers.setup_bot_commands(application)
        
        # Start the bot
        logger.info("Starting bot polling...")
        logger.info("Bot is ready! Press Ctrl+C to stop.")
        
        # Run the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if 'application' in locals():
            logger.info("Stopping bot...")
            await application.stop()
            await application.shutdown()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
