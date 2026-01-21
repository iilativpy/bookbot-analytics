# Setup Guide: Step-by-Step Instructions

This guide will walk you through setting up the Telegram Booking Statistics Bot from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting Your Telegram Bot Token](#getting-your-telegram-bot-token)
3. [Getting Your OpenRouter API Key](#getting-your-openrouter-api-key)
4. [Database Setup](#database-setup)
5. [Project Installation](#project-installation)
6. [Configuration](#configuration)
7. [First Run](#first-run)
8. [Verification](#verification)

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.9 or higher
- **MySQL**: Version 5.7 or higher (or compatible database)
- **Internet**: Stable connection for Telegram and API access

### Check Python Version

```bash
python --version
# or
python3 --version
```

If you don't have Python 3.9+, download it from [python.org](https://www.python.org/downloads/)

### Check MySQL

```bash
mysql --version
```

## Getting Your Telegram Bot Token

### Step 1: Find BotFather

1. Open Telegram
2. Search for `@BotFather`
3. Start a chat with BotFather

### Step 2: Create Your Bot

1. Send `/newbot` to BotFather
2. Choose a name for your bot (e.g., "My Booking Stats Bot")
3. Choose a username (must end in 'bot', e.g., "mybookingstats_bot")
4. BotFather will give you a token that looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
5. **Save this token** - you'll need it for configuration

### Step 3: Configure Bot Settings (Optional)

```
/setdescription - Set bot description
/setabouttext - Set about text
/setuserpic - Set bot profile picture
```

## Getting Your OpenRouter API Key

### Step 1: Create Account

1. Go to [openrouter.ai](https://openrouter.ai)
2. Click "Sign Up" or "Get API Key"
3. Sign up with Google, GitHub, or MetaMask

### Step 2: Add Credits

1. Go to your account settings
2. Click "Buy Credits"
3. Add funds (start with $5-10 for testing)
   - DeepSeek v3 is very cost-effective (~$0.27 per million tokens)

### Step 3: Get API Key

1. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
2. Click "Create Key"
3. Name your key (e.g., "Booking Bot")
4. Copy the API key (looks like: `sk-or-v1-...`)
5. **Save this key** - you'll need it for configuration

## Database Setup

### Option 1: Use Existing Database

If you already have a booking database:

1. Note down your connection details:
   - Host (usually `localhost`)
   - Port (usually `3306`)
   - Database name
   - Username
   - Password

2. Ensure your MySQL user has SELECT permissions on booking tables

### Option 2: Create Test Database

For testing purposes:

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE booking_test;

-- Create user
CREATE USER 'booking_bot'@'localhost' IDENTIFIED BY 'secure_password';

-- Grant permissions
GRANT SELECT ON booking_test.* TO 'booking_bot'@'localhost';
FLUSH PRIVILEGES;

-- Use the database
USE booking_test;
```

The bot will create tables on first run if they don't exist.

### Step 3: Test Connection

```bash
mysql -u booking_bot -p -h localhost booking_test
```

If successful, you'll see the MySQL prompt. Type `exit` to leave.

## Project Installation

### Step 1: Navigate to Project Directory

```bash
cd /path/to/telegram-booking-bot
```

### Step 2: Create Virtual Environment

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take a few minutes to install all packages.

### Step 4: Verify Installation

```bash
pip list | grep telegram
pip list | grep langchain
pip list | grep sqlalchemy
```

You should see the installed packages.

## Configuration

### Step 1: Create Environment File

```bash
cp .env.example .env
```

### Step 2: Edit Configuration

Open `.env` in your text editor:

**Linux/Mac:**
```bash
nano .env
# or
vim .env
# or
code .env  # if you have VS Code
```

**Windows:**
```cmd
notepad .env
```

### Step 3: Configure All Settings

```env
# ============================================
# REQUIRED: Site Configuration
# ============================================
SITE_NAME=My Booking Platform

# ============================================
# REQUIRED: Telegram Bot
# ============================================
# Get from @BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# ============================================
# REQUIRED: OpenRouter API
# ============================================
# Get from openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Model to use (default is cost-effective DeepSeek)
OPENROUTER_MODEL=deepseek/deepseek-v3

# Don't change unless using custom endpoint
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# ============================================
# REQUIRED: MySQL Database
# ============================================
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=booking_bot
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=booking_test

# ============================================
# OPTIONAL: Application Settings
# ============================================
TIMEZONE=UTC
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=10

# ============================================
# OPTIONAL: Prediction Settings
# ============================================
PREDICTION_CONFIDENCE_INTERVAL=0.95
MIN_HISTORICAL_DAYS=30
```

### Step 4: Adapt Database Models

Open `src/database/models.py` and adapt to your schema:

1. Change `__tablename__` to match your table names
2. Update column names to match your database
3. Adjust data types if needed
4. Add any custom fields

Example:
```python
class Booking(Base):
    __tablename__ = "reservations"  # Your table name
    
    # Update column names to match yours
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    booking_date = Column(DateTime, default=datetime.utcnow)
    # ... continue adapting
```

## First Run

### Step 1: Test Configuration

```bash
python -c "from config import get_config; c = get_config(); print(f'Site: {c.site_name}')"
```

If successful, you'll see your site name.

### Step 2: Test Database Connection

```bash
python -c "from src.database import init_db; init_db(); print('Database OK')"
```

If successful, you'll see "Database OK".

### Step 3: Start the Bot

```bash
python main.py
```

You should see:
```
INFO - Starting My Booking Platform Booking Bot
INFO - Using LLM model: deepseek/deepseek-v3
INFO - Database initialized
INFO - Setting up bot handlers...
INFO - Telegram application configured
INFO - Bot is ready! Press Ctrl+C to stop.
```

### Step 4: Keep It Running

The bot will now run continuously. To stop it, press `Ctrl+C`.

**To run in background (Linux/Mac):**
```bash
nohup python main.py > bot.log 2>&1 &
```

**To run as service (recommended for production):**
Create a systemd service or use a process manager like `supervisor`.

## Verification

### Step 1: Test Telegram Commands

1. Open Telegram
2. Search for your bot username
3. Start a chat
4. Send `/start`

You should receive a welcome message.

### Step 2: Test Commands

Try these commands:
- `/help` - Should show command list
- `/stats` - Should show statistics (may be empty if no data)
- `/menu` - Should show interactive menu

### Step 3: Test Natural Language

Send a message:
```
How many bookings do we have?
```

The bot should process your query and respond.

### Step 4: Check Logs

```bash
tail -f bot.log
```

You should see the bot processing commands without errors.

### Step 5: Test with Sample Data

If you're using a test database, insert some sample bookings:

```sql
USE booking_test;

INSERT INTO customers (name, email, phone) VALUES
('Test Customer', 'test@example.com', '+1234567890');

INSERT INTO bookings (customer_id, booking_date, check_in, check_out, status, total_price)
VALUES
(1, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), DATE_ADD(NOW(), INTERVAL 10 DAY), 'confirmed', 500.00);
```

Then try `/stats` again - you should see your test booking.

## Troubleshooting

### Bot Not Responding

**Problem**: Bot doesn't respond to commands

**Solutions**:
1. Check bot is running: `ps aux | grep main.py`
2. Verify token in `.env` is correct
3. Check `bot.log` for errors
4. Ensure you've sent `/start` first

### Database Errors

**Problem**: Database connection failed

**Solutions**:
1. Test MySQL: `mysql -u user -p -h host database`
2. Check credentials in `.env`
3. Verify database exists
4. Check user permissions

### OpenRouter Errors

**Problem**: AI responses not working

**Solutions**:
1. Verify API key at [openrouter.ai](https://openrouter.ai)
2. Check credits/balance
3. Try a different model
4. Check internet connection

### Import Errors

**Problem**: ModuleNotFoundError

**Solutions**:
1. Activate virtual environment: `source venv/bin/activate`
2. Reinstall: `pip install -r requirements.txt`
3. Check Python version: `python --version`

### No Data Showing

**Problem**: Commands work but show no data

**Solutions**:
1. Verify database has booking records
2. Check date ranges in queries
3. Ensure table/column names match in `models.py`
4. Check database permissions

## Next Steps

After successful setup:

1. **Customize**: Add your branding and custom metrics
2. **Secure**: Set up proper authentication if needed
3. **Monitor**: Set up logging and monitoring
4. **Scale**: Consider deploying to a server
5. **Backup**: Regular database backups

## Production Deployment

For production use:

1. **Use environment variables** instead of `.env` file
2. **Set up SSL** for database connections
3. **Use process manager** (systemd, supervisor)
4. **Set up monitoring** (logs, alerts)
5. **Regular backups** of configuration and database
6. **Restrict bot access** to authorized users

## Support Resources

- **Telegram Bot API**: [core.telegram.org/bots/api](https://core.telegram.org/bots/api)
- **OpenRouter Docs**: [openrouter.ai/docs](https://openrouter.ai/docs)
- **SQLAlchemy Docs**: [docs.sqlalchemy.org](https://docs.sqlalchemy.org)
- **LangChain Docs**: [python.langchain.com](https://python.langchain.com)

---

**You're all set! 🎉**

Your booking statistics bot is now ready to provide insights and analytics.
