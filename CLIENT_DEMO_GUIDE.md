# Easy Analytics - Client Demo & Testing Guide

## 🚀 Complete Setup in 5 Minutes

### Step 1: Run the Complete Setup Script

```bash
python setup_complete_test.py
```

This automated script will:
- ✅ Check prerequisites (Docker, Python)
- ✅ Configure your environment (.env file)
- ✅ Start all services (ToolJet, PostgreSQL)
- ✅ Create database schema
- ✅ Load realistic test data
- ✅ Generate app configuration files

### Step 2: Access ToolJet

After setup completes, ToolJet will open automatically at http://localhost:8080

**First Time Setup:**
1. Click "Sign up" 
2. Create an account with any email/password
3. You'll be taken to the ToolJet dashboard

## 🛠️ Setting Up the Chatbot App

### 1. Configure Data Sources

#### PostgreSQL Database
1. Click **"Data Sources"** in the left sidebar
2. Click **"+ Add datasource"**
3. Select **"PostgreSQL"**
4. Configure:
   ```
   Name: Analytics DB
   Host: postgres
   Port: 5432
   Database: tooljet_prod
   Username: postgres
   Password: tooljet
   SSL: Disable
   ```
5. Click **"Test connection"** → Should show "Connection Successful"
6. Click **"Save"**

#### OpenAI API
1. Click **"+ Add datasource"** again
2. Select **"OpenAI"**
3. Configure:
   ```
   Name: OpenAI
   API Key: [Your OpenAI API key from .env file]
   ```
4. Click **"Test connection"**
5. Click **"Save"**

### 2. Create the Chatbot App

1. Go to **"Apps"** in the left sidebar
2. Click **"Create new app"**
3. Name it **"Easy Analytics Chatbot"**

### 3. Design the UI

#### Add Title
1. Drag a **Text** component from the right panel
2. Properties:
   - Text: `🤖 Easy Analytics Chatbot`
   - Font size: 24
   - Font weight: Bold

#### Add Input Field
1. Drag a **TextInput** component
2. Properties:
   - Name: `queryInput`
   - Label: `Your Question`
   - Placeholder: `Ask me about your sales data...`

#### Add Submit Button
1. Drag a **Button** component
2. Properties:
   - Name: `submitButton`
   - Button text: `Ask`
   - Background color: `#4F46E5`

#### Add Chat Display
1. Drag a **TextArea** component
2. Properties:
   - Name: `chatHistory`
   - Placeholder: `Chat history will appear here...`
   - Number of rows: 15
   - Disabled: Yes

#### Add Sample Queries
1. Drag another **Text** component
2. Properties:
   - Text: 
   ```
   Sample queries:
   • What is the total revenue this month?
   • Show me top 5 deals
   • Which product sells the most?
   • List contacts from technology companies
   ```
   - Font size: 12

### 4. Configure Queries

#### Query 1: generateSQL
1. Click **"+ New Query"** at the bottom
2. Select **"OpenAI"** as data source
3. Name: `generateSQL`
4. Configuration:
   ```
   Operation: Chat
   Model: gpt-3.5-turbo
   Messages: 
   [
     {
       "role": "system",
       "content": "You are a SQL expert. Generate PostgreSQL queries based on this schema: deals(id,name,amount,close_date,product_id,account_id,contact_id), contacts(id,first_name,last_name,email), accounts(id,name,industry), products(id,name,price), sales_activities(id,deal_id,activity_type,date,outcome). Return ONLY the SQL query, no explanations."
     },
     {
       "role": "user",
       "content": "{{components.queryInput.value}}"
     }
   ]
   ```

#### Query 2: executeSQL
1. Click **"+ New Query"**
2. Select **"Analytics DB"** as data source
3. Name: `executeSQL`
4. Query:
   ```sql
   {{queries.generateSQL.data.choices[0].message.content}}
   ```

#### Query 3: summarizeResults
1. Click **"+ New Query"**
2. Select **"OpenAI"** as data source
3. Name: `summarizeResults`
4. Configuration:
   ```
   Operation: Chat
   Model: gpt-3.5-turbo
   Messages:
   [
     {
       "role": "system", 
       "content": "Summarize the SQL query results in a friendly, conversational way. Be specific with numbers and names."
     },
     {
       "role": "user",
       "content": "Query: {{components.queryInput.value}}\nResults: {{JSON.stringify(queries.executeSQL.data)}}"
     }
   ]
   ```

#### Query 4: handleChatbotQuery
1. Click **"+ New Query"**
2. Select **"Run JavaScript Code"**
3. Name: `handleChatbotQuery`
4. Code:
```javascript
const userInput = components.queryInput.value;
if (!userInput) {
  await actions.showAlert('error', 'Please enter a question');
  return;
}

// Add user message to chat
const currentChat = components.chatHistory.value || '';
components.chatHistory.value = currentChat + `\n\nYou: ${userInput}\n`;

try {
  // Show loading
  components.submitButton.setText('Thinking...');
  components.submitButton.disable(true);
  
  // Generate SQL
  await queries.generateSQL.run();
  
  // Execute SQL
  await queries.executeSQL.run();
  
  // Summarize results  
  await queries.summarizeResults.run();
  
  // Add AI response to chat
  const summary = queries.summarizeResults.data.choices[0].message.content;
  components.chatHistory.value += `\nAssistant: ${summary}`;
  
  // Clear input
  components.queryInput.setValue('');
  
} catch (error) {
  components.chatHistory.value += `\nError: ${error.message}. Please try rephrasing your question.`;
} finally {
  // Reset button
  components.submitButton.setText('Ask');
  components.submitButton.disable(false);
}
```

### 5. Connect Button Event
1. Click on the **Ask** button
2. In properties panel, go to **Events**
3. Add event:
   - Event: On click
   - Action: Run Query
   - Query: handleChatbotQuery

## 🎯 Live Demo Scenarios

### Scenario 1: Sales Overview
**User asks:** "What is our total revenue this month?"

**Expected behavior:**
1. Chatbot generates SQL to sum deals for current month
2. Executes query against real data
3. Returns conversational response like: "Your total revenue for December 2024 is $125,450.00 from 8 closed deals."

### Scenario 2: Top Performers
**User asks:** "Show me the top 5 deals by amount"

**Expected response:**
```
Here are your top 5 deals by amount:
1. Deal 15 - $48,920
2. Deal 7 - $45,230  
3. Deal 19 - $42,100
4. Deal 3 - $38,450
5. Deal 11 - $35,200
```

### Scenario 3: Product Analysis
**User asks:** "Which product is selling the most?"

**Expected response:**
```
Analytics Suite is your top-selling product with 7 deals totaling $234,500 in revenue. It's followed by CRM Pro with 5 deals worth $178,300.
```

### Scenario 4: Customer Insights
**User asks:** "List all contacts from technology companies"

**Expected response:**
```
I found 2 contacts from technology companies:
- John Doe (john.doe@acme.com) from Acme Corp
- Another contact if exists...
```

### Scenario 5: Activity Tracking
**User asks:** "How many sales activities happened this week?"

**Expected response:**
```
You had 12 sales activities this week:
- 4 Calls
- 3 Emails
- 3 Meetings
- 2 Demos
The success rate was 58% (7 successful outcomes).
```

## 📊 Advanced Testing

### Test Complex Queries
1. **Time-based aggregations:**
   - "Compare this month's revenue to last month"
   - "Show me deal trends over the past 3 months"

2. **Multi-table joins:**
   - "Which account has the most deals?"
   - "Show deals by industry"

3. **Calculations:**
   - "What's the average deal size?"
   - "Calculate conversion rate by product"

### Monitor Performance
1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Watch API calls and response times
4. Expected performance:
   - OpenAI calls: 1-3 seconds
   - Database queries: <100ms

## 🐛 Troubleshooting

### If chatbot doesn't respond:
1. Check browser console for errors (F12)
2. Verify API keys in Data Sources
3. Test queries individually in ToolJet

### If results are empty:
1. Connect to database:
   ```bash
   docker exec -it easy-analytics_postgres_1 psql -U postgres -d tooljet_prod
   ```
2. Check data exists:
   ```sql
   SELECT COUNT(*) FROM deals;
   SELECT COUNT(*) FROM contacts;
   ```

### If OpenAI errors occur:
1. Verify API key is valid
2. Check OpenAI API limits/quotas
3. Try simpler queries first

## 📈 Success Metrics

Your chatbot is working correctly when:
- ✅ Responds to natural language queries in 2-5 seconds
- ✅ Generates accurate SQL for the schema
- ✅ Returns real data from the database
- ✅ Provides conversational, easy-to-understand summaries
- ✅ Handles errors gracefully

## 🎥 Demo Recording Tips

1. **Prepare your environment:**
   - Clear chat history before starting
   - Have sample queries ready
   - Ensure stable internet connection

2. **Show the full flow:**
   - Type queries naturally
   - Show the thinking/loading state
   - Highlight the conversational responses

3. **Demonstrate variety:**
   - Simple queries (counts, sums)
   - Complex queries (joins, calculations)
   - Time-based queries
   - Error handling

## 🚀 Next Steps

Once testing is complete:
1. Export your ToolJet app for production deployment
2. Configure production database with real CRM data
3. Set up proper authentication and access controls
4. Add more sophisticated error handling
5. Implement query caching for better performance 