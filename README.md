# Telegram Booking Statistics Bot

An AI-powered Telegram chatbot for analyzing booking statistics, generating predictions, and providing insights for booking platforms. Built with Python, LangChain, OpenRouter, and SQLAlchemy.

## Features

- 📊 **Comprehensive Statistics**: Real-time booking statistics, revenue tracking, and key metrics
- 📈 **Trend Analysis**: Identify booking patterns and trends over time
- 🔮 **Predictions**: AI-powered and statistical booking forecasts
- ⚖️ **Period Comparisons**: Compare performance across different time periods
- 🤖 **Natural Language Interface**: Ask questions in plain English
- 💬 **Command Interface**: Quick access via bot commands
- 🔄 **Universal Design**: Easily configurable for different booking sites
- 🎯 **Flexible AI**: Switch between different LLM models effortlessly

## Architecture

The bot combines multiple technologies:

- **Telegram Bot**: User interface via Telegram
- **LangChain**: AI orchestration and natural language understanding
- **OpenRouter**: Universal LLM API (default: DeepSeek v3)
- **SQLAlchemy**: Database ORM for MySQL
- **Prophet/ARIMA**: Statistical time series forecasting
- **Python**: Core application logic

## Prerequisites

- Python 3.9+
- MySQL database with booking data
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenRouter API Key (from [openrouter.ai](https://openrouter.ai))

## Installation

### 1. Clone or Download the Project

```bash
cd telegram-booking-bot
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate on Linux/Mac:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure your settings:

```env
# Site Configuration
SITE_NAME=Your Booking Site Name

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=deepseek/deepseek-v3

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_db_user
MYSQL_PASSWORD=your_db_password
MYSQL_DATABASE=your_db_name
```

## Database Setup

### Adapt to Your Schema

The bot includes default SQLAlchemy models in `src/database/models.py`. You need to adapt these to match your existing database schema:

1. Open `src/database/models.py`
2. Update the `__tablename__` attributes to match your table names
3. Modify column names and types to match your schema
4. Add any additional fields specific to your booking system

Example adaptation:

```python
class Booking(Base):
    __tablename__ = "your_bookings_table"  # Change to your table name
    
    # Update column names to match your database
    id = Column(Integer, primary_key=True)
    reservation_date = Column(DateTime, ...)  # If you use 'reservation_date' instead of 'booking_date'
    # ... other fields
```

### Required Data

The bot expects the following minimum data structure:

- **Bookings table** with:
  - Unique ID
  - Customer reference
  - Booking/creation date
  - Check-in/check-out dates
  - Status (pending, confirmed, cancelled, completed)
  - Price/revenue amount
  
- **Customers table** (optional but recommended) with:
  - Unique ID
  - Basic contact information
  - Booking history

## Usage

### Start the Bot

```bash
python main.py
```

You should see:
```
INFO - Starting Your Booking Site Booking Bot
INFO - Using LLM model: deepseek/deepseek-v3
INFO - Database initialized
INFO - Bot is ready! Press Ctrl+C to stop.
```

### Telegram Commands

Open your Telegram bot and use these commands:

- `/start` - Initialize the bot and show welcome message
- `/stats` - View current month statistics
- `/compare` - Compare different time periods
- `/predict` - Generate booking predictions
- `/trends` - Analyze booking trends
- `/cancellations` - View cancellation statistics
- `/returns` - Analyze return customer rates
- `/menu` - Show interactive menu
- `/help` - Display help information

### Natural Language Queries

You can also ask questions naturally:

- "How many bookings did we have last month?"
- "Compare this month with last year"
- "What's our cancellation rate?"
- "Predict bookings for next 30 days"
- "Show me booking trends"
- "What's the return customer percentage?"

## Configuration

### Change Site Name

Edit `.env`:
```env
SITE_NAME=My Hotel Booking Platform
```

The site name will appear in welcome messages and bot responses.

### Change AI Model

The bot uses OpenRouter, which supports 300+ models. To change the model, edit `.env`:

```env
# Use OpenAI GPT-4
OPENROUTER_MODEL=openai/gpt-4

# Use Anthropic Claude
OPENROUTER_MODEL=anthropic/claude-opus-4.5

# Use Google Gemini
OPENROUTER_MODEL=google/gemini-pro

# Use DeepSeek (default, cost-effective)
OPENROUTER_MODEL=deepseek/deepseek-v3
```

See available models at [openrouter.ai/models](https://openrouter.ai/models)

### Customize Statistics

Edit `src/services/statistics.py` to add custom metrics specific to your business.

## Project Structure

```
telegram-booking-bot/
├── config/                    # Configuration
│   ├── settings.py           # Settings with site templates
│   └── __init__.py
├── src/
│   ├── ai/                   # AI/LLM integration
│   │   ├── llm_client.py    # OpenRouter client
│   │   ├── langchain_agent.py # LangChain agent
│   │   └── prompts.py       # Prompt templates
│   ├── bot/                  # Telegram bot
│   │   ├── handlers.py      # Message handlers
│   │   ├── commands.py      # Command definitions
│   │   └── keyboards.py     # Inline keyboards
│   ├── database/             # Database layer
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── connection.py    # DB connection
│   │   └── queries.py       # Query functions
│   ├── services/             # Business logic
│   │   ├── statistics.py    # Statistics service
│   │   ├── analytics.py     # Analytics service
│   │   └── predictions.py   # Predictions service
│   └── utils/                # Utilities
│       ├── formatters.py    # Telegram formatters
│       └── validators.py    # Input validators
├── tests/                    # Test suite
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment config
├── main.py                  # Application entry point
└── README.md                # This file
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run specific test file:

```bash
pytest tests/test_statistics.py -v
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Key Metrics Provided

### Statistics
- Total bookings (by status)
- Total revenue
- Average booking value
- Booking rate (confirmed/total)
- Cancellation rate
- Return customer percentage

### Comparisons
- Month-over-month changes
- Year-over-year comparisons
- Year-to-date analysis
- Custom period comparisons

### Predictions
- Statistical forecasts (Prophet/ARIMA)
- AI-powered insights
- Confidence intervals
- Trend projections

### Analytics
- Trend identification
- Best/worst performing periods
- Cancellation analysis with reasons
- Customer retention metrics

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Verify MySQL is running
2. Check credentials in `.env`
3. Ensure database exists and is accessible
4. Test connection: `mysql -u user -p -h host database_name`

### Bot Not Responding

1. Check bot token is correct
2. Verify bot is running (`python main.py`)
3. Check logs in `bot.log`
4. Ensure `/start` command has been sent

### AI Errors

1. Verify OpenRouter API key is valid
2. Check API credits at [openrouter.ai](https://openrouter.ai)
3. Try a different model if one is unavailable
4. Check network connectivity

### Import Errors

If you see import errors:

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify Python version
python --version  # Should be 3.9+
```

## Reusing for Another Site

To adapt this bot for a different booking platform:

1. **Update Site Name**: Change `SITE_NAME` in `.env`
2. **Adapt Database Models**: Modify `src/database/models.py` to match your schema
3. **Update Connection**: Configure MySQL connection in `.env`
4. **Customize Metrics**: Add site-specific calculations in services
5. **Test**: Run with your data to verify compatibility

The bot is designed to be universal and reusable across different booking platforms.

## Performance Considerations

- **Database**: Uses connection pooling for efficiency
- **Caching**: Consider adding Redis for frequently accessed stats
- **Rate Limiting**: OpenRouter handles rate limits automatically
- **Async**: Bot uses async/await for non-blocking operations

## Security

- Store `.env` securely (never commit to version control)
- Use strong database passwords
- Restrict bot access to authorized users if needed
- Keep API keys confidential
- Regular security updates: `pip install --upgrade -r requirements.txt`

## Contributing

To extend the bot:

1. Add new commands in `src/bot/handlers.py`
2. Create new services in `src/services/`
3. Add tests in `tests/`
4. Update documentation

## License

This project is provided as-is for use with your booking platforms.

## Support

For issues:
1. Check logs in `bot.log`
2. Review this README
3. Verify configuration in `.env`
4. Test database connectivity

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [LangChain](https://github.com/langchain-ai/langchain)
- [OpenRouter](https://openrouter.ai)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Facebook Prophet](https://facebook.github.io/prophet/)

---

**Built with ❤️ for booking platform analytics**
