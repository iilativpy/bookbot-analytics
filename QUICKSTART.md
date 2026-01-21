# Quick Start Guide

Get your Telegram Booking Statistics Bot running in 5 minutes!

## ⚡ Fast Setup

### 1. Get API Keys

**Telegram Bot Token:**
- Message [@BotFather](https://t.me/botfather) on Telegram
- Send `/newbot` and follow instructions
- Copy the token

**OpenRouter API Key:**
- Sign up at [openrouter.ai](https://openrouter.ai)
- Add $5-10 credits
- Get API key from [openrouter.ai/keys](https://openrouter.ai/keys)

### 2. Install

```bash
cd telegram-booking-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env` with your details:
```env
SITE_NAME=My Booking Site
TELEGRAM_BOT_TOKEN=your_token_here
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=deepseek/deepseek-v3
MYSQL_HOST=localhost
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

### 4. Adapt Database Models

Edit `src/database/models.py`:
- Change `__tablename__` to match your tables
- Update column names to match your schema

### 5. Run

```bash
python main.py
```

### 6. Test

Open Telegram, find your bot, and send:
```
/start
```

## 🎯 Available Commands

- `/start` - Welcome message
- `/stats` - Current month statistics
- `/compare` - Compare periods
- `/predict` - Generate predictions
- `/trends` - Analyze trends
- `/cancellations` - Cancellation stats
- `/returns` - Return customer analysis
- `/menu` - Interactive menu
- `/help` - Show help

## 💬 Natural Language Examples

Ask questions naturally:
- "How many bookings last month?"
- "Compare this month with last year"
- "Predict bookings for next 30 days"
- "What's our cancellation rate?"

## 🔧 Key Features

✅ **Dual Interface**: Commands + Natural Language  
✅ **AI-Powered**: Uses DeepSeek v3 by default (very cost-effective)  
✅ **Universal**: Easy to configure for any booking site  
✅ **Hybrid Predictions**: Statistical models + AI insights  
✅ **Comprehensive Analytics**: All key booking metrics  
✅ **MySQL Integration**: Works with existing databases  

## 📊 What You Get

**Statistics:**
- Total bookings, revenue, averages
- Booking rate, cancellation rate
- Return customer percentage

**Comparisons:**
- Month-over-month
- Year-over-year
- Custom periods

**Predictions:**
- 7-90 day forecasts
- Statistical models (Prophet/ARIMA)
- AI insights and recommendations

**Trends:**
- Pattern identification
- Best/worst periods
- Growth analysis

## 🔄 Reuse for Another Site

Change these settings in `.env`:
```env
SITE_NAME=Another Booking Platform
# ... same API keys work for multiple bots
```

Adapt `src/database/models.py` to new database schema.

Deploy a new bot instance - done!

## 🚀 Model Options

Change AI model in `.env`:

**Cost-Effective (Recommended):**
```env
OPENROUTER_MODEL=deepseek/deepseek-v3  # Very cheap, great quality
```

**High Performance:**
```env
OPENROUTER_MODEL=openai/gpt-4
OPENROUTER_MODEL=anthropic/claude-opus-4.5
OPENROUTER_MODEL=google/gemini-pro
```

See all models: [openrouter.ai/models](https://openrouter.ai/models)

## 📝 Next Steps

1. ✅ Bot running? Test all commands
2. 📊 Verify data shows correctly
3. 🎨 Customize for your brand
4. 📈 Monitor usage and costs
5. 🚀 Deploy to production server

## 🆘 Troubleshooting

**Bot not responding?**
- Check bot token in `.env`
- Verify bot is running: `ps aux | grep main.py`
- Send `/start` first

**Database errors?**
- Test connection: `mysql -u user -p -h host database`
- Check credentials in `.env`
- Adapt models.py to your schema

**AI not working?**
- Check API key at openrouter.ai
- Verify credits balance
- Try different model

**No data showing?**
- Check database has records
- Verify table names in models.py
- Check date ranges

## 📚 Full Documentation

- `README.md` - Complete documentation
- `SETUP_GUIDE.md` - Detailed setup instructions
- `src/` - Code with inline comments
- `tests/` - Test examples

## 💰 Cost Estimate

With DeepSeek v3 (default):
- ~$0.27 per million tokens
- Average query: ~500 tokens
- **~$0.00014 per query**
- 1000 queries = ~$0.14

Very affordable! 🎉

## 🎉 You're Ready!

Your intelligent booking analytics bot is now operational.

Ask it anything about your bookings! 

---

**Need Help?** Check the full `README.md` and `SETUP_GUIDE.md`
