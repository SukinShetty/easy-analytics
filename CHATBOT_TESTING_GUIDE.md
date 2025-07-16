# Easy Analytics Chatbot Testing Guide

## Quick Start

### 1. Prerequisites
- Docker Desktop installed and running
- Python 3.8+ installed
- Valid OpenAI API key

### 2. Setup Environment

```bash
# Copy template and configure
cp env.template .env

# Edit .env file and add your API keys:
# - OPENAI_API_KEY=sk-your-real-key-here
# - FRESHWORKS_API_KEY=your-freshworks-key
# - FRESHWORKS_DOMAIN=your-company.freshworks.com
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose ps
```

### 4. Run Test Suite

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run the test suite
python test_chatbot.py
```

## Testing the Chatbot

### Manual Testing in ToolJet

1. **Access ToolJet**: Open http://localhost:8080 in your browser

2. **Create/Import the App**: 
   - Import the Easy Analytics app if you have the export
   - Or create a new app with:
     - Input component (queryInput)
     - Chat history component (chatHistory)
     - Three queries: generateSQL, executeSQL, summarizeResults

3. **Configure Queries**:

   **generateSQL (OpenAI Query)**:
   ```javascript
   // Resource: OpenAI
   // Model: gpt-3.5-turbo
   // Messages:
   [{
     "role": "user",
     "content": "{{components.queryInput.value}}"
   }]
   ```

   **executeSQL (PostgreSQL Query)**:
   ```sql
   {{queries.generateSQL.data.choices[0].message.content}}
   ```

   **summarizeResults (OpenAI Query)**:
   ```javascript
   // Resource: OpenAI
   // Model: gpt-3.5-turbo
   // Messages:
   [{
     "role": "user", 
     "content": "Summarize these results in natural language: {{JSON.stringify(queries.executeSQL.data)}}"
   }]
   ```

### Sample Test Queries

Try these queries to test different chatbot capabilities:

#### Basic Queries
- "Show me total sales this month"
- "List top 5 deals"
- "Which product sells the most?"

#### Complex Queries
- "Show average deal size by industry"
- "List deals with no activities"
- "What's the conversion rate by product?"

#### Time-based Queries
- "Show deals closing this week"
- "What was last month's revenue?"
- "List activities from the past 7 days"

## Troubleshooting

### Common Issues

1. **ToolJet Not Loading**
   ```bash
   docker-compose logs tooljet
   # Check for port conflicts on 8080
   ```

2. **Database Connection Failed**
   ```bash
   docker-compose logs postgres
   # Ensure PostgreSQL is running on port 5432
   ```

3. **Chatbot Returns Errors**
   - Check OpenAI API key is valid
   - Verify database tables exist
   - Check browser console for JavaScript errors

4. **No Data in Results**
   ```bash
   # Connect to database and check
   docker exec -it postgres psql -U postgres -d tooljet_prod
   \dt  # List tables
   SELECT COUNT(*) FROM deals;  # Check data
   ```

### Debug Mode

Enable debug logging in ToolJet:
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Run queries and watch for errors

### API Key Validation

Test OpenAI API key:
```python
import openai
openai.api_key = "your-key-here"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
print("API key is valid!" if response else "API key invalid")
```

## Performance Testing

### Load Testing
The test script creates 20 deals and 50 activities. To test with more data:

```sql
-- Connect to database
docker exec -it postgres psql -U postgres -d tooljet_prod

-- Insert more test data
INSERT INTO deals (id, name, amount, close_date, product_id, account_id, contact_id)
SELECT 
    generate_series(100, 1000),
    'Deal ' || generate_series(100, 1000),
    (random() * 100000)::numeric(10,2),
    CURRENT_DATE - (random() * 365)::int,
    1 + (random() * 3)::int,
    1 + (random() * 3)::int,
    1 + (random() * 3)::int;
```

### Response Time Monitoring
Monitor query execution time in ToolJet:
- Check the query execution time in the ToolJet query panel
- OpenAI queries should respond in 1-3 seconds
- Database queries should be < 100ms

## Security Considerations

1. **API Keys**: Never commit real API keys to version control
2. **Database Access**: Use read-only database user for chatbot queries in production
3. **Input Validation**: The chatbot should sanitize SQL to prevent injection
4. **Rate Limiting**: Monitor OpenAI API usage to control costs

## Next Steps

1. **Customize Prompts**: Modify the OpenAI prompts for better SQL generation
2. **Add Error Handling**: Implement better error messages for users
3. **Enhance UI**: Add loading states, error displays, and query history
4. **Add Analytics**: Track query patterns and performance metrics 