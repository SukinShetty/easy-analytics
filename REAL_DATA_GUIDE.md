# Easy Analytics - Using REAL Freshworks Data

## 🎯 Quick Start with Your Real CRM Data

### Step 1: Configure Your Credentials

Edit your `.env` file with your ACTUAL credentials:

```env
# Your actual Freshworks domain (without https://)
FRESHWORKS_DOMAIN=yourcompany.freshworks.com

# Your Freshworks API key from Settings → API Settings
FRESHWORKS_API_KEY=your_actual_api_key_here

# Your OpenAI API key
OPENAI_API_KEY=sk-your_actual_openai_key_here
```

### Step 2: Run the Sync

**Windows:**
```cmd
sync_real_data.bat
```

**Python:**
```bash
python run_real_chatbot.py
```

### Step 3: What Happens

The sync script will:
1. ✅ Connect to YOUR Freshworks account
2. ✅ Pull YOUR real data:
   - Contacts
   - Accounts/Companies
   - Products
   - Deals
   - Sales Activities
3. ✅ Store it in local PostgreSQL
4. ✅ Make it queryable via chatbot

## 📊 Your Real Data Questions

Once synced, you can ask about YOUR ACTUAL data:

### Deal Questions
- "What are my top 10 deals by value?"
- "Show me deals closing this month"
- "Which deals have no activities?"
- "What's my pipeline value?"

### Contact Questions
- "List all contacts from [Company Name]"
- "Show me contacts without email addresses"
- "Who are my contacts in the technology industry?"

### Product Performance
- "Which products are selling the most?"
- "What's the average deal size by product?"
- "Show products with no recent deals"

### Sales Activity
- "What activities happened this week?"
- "Which deals have the most activities?"
- "Show me overdue follow-ups"

### Analytics
- "What's my total revenue this quarter?"
- "Compare this month to last month"
- "What's my average deal size?"
- "Show conversion rates by product"

## 🔍 Finding Your Freshworks API Key

1. Log into Freshworks CRM
2. Click your profile icon → Settings
3. Go to **API Settings**
4. Click **API Key** tab
5. Copy your API key

## 🛠️ Troubleshooting

### "Authentication Failed"
- Check your API key is correct
- Ensure your Freshworks plan includes API access
- Verify the domain format (should be: company.freshworks.com)

### "No Data Found"
- Check if you have data in Freshworks
- Try logging into Freshworks directly to verify
- Check API permissions for your user

### "Connection Error"
- Verify your internet connection
- Check if Freshworks is accessible
- Try the domain in browser: https://yourdomain.freshworks.com

## 🔄 Keeping Data Fresh

### Manual Sync
Run the sync script whenever you want fresh data:
```cmd
python sync_freshworks_data.py
```

### Scheduled Sync (Windows Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/hourly)
4. Action: Start `sync_real_data.bat`

### Scheduled Sync (Cron - Linux/Mac)
```bash
# Run every hour
0 * * * * cd /path/to/easy-analytics && python sync_freshworks_data.py
```

## 🔐 Security Notes

- Your Freshworks data stays in YOUR local database
- Only questions go to OpenAI, not your actual data
- API keys are stored locally in .env
- Database runs in Docker container

## 📈 Advanced Queries

### Multi-Table Joins
"Show me all deals with their contact emails and company names"

### Time-Based Analysis
"What's the trend of deal closures over the last 6 months?"

### Comparative Analysis
"Compare product performance between Q1 and Q2"

### Predictive Questions
"Based on current pipeline, what's my projected revenue this quarter?"

## 💡 Tips

1. **First Sync**: May take 5-10 minutes depending on data volume
2. **API Limits**: Freshworks has rate limits - sync handles this automatically
3. **Data Freshness**: Sync as often as needed (hourly/daily)
4. **Query Natural**: Ask questions as you would to a colleague

## 🚀 Next Steps

1. Complete the sync of your real data
2. Set up the chatbot UI in ToolJet (see CLIENT_DEMO_GUIDE.md)
3. Start asking questions about YOUR business
4. Share with your team!

## 📞 Getting Help

If you encounter issues with your specific Freshworks setup:
1. Check Freshworks API documentation
2. Verify your API permissions
3. Check the sync logs for specific errors
4. Ensure your Freshworks plan includes API access 