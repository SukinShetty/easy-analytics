# Easy Analytics Chatbot - Demo Script

## 🎬 Demo Overview
**Duration:** 5-7 minutes  
**Objective:** Show a working AI chatbot analyzing real CRM data

## Pre-Demo Setup
1. Run `./quick_start.ps1` (Windows) or `python setup_complete_test.py`
2. Open ToolJet at http://localhost:8080
3. Have the chatbot app ready with sample data loaded

## Demo Flow

### 1. Introduction (30 seconds)
"Welcome to Easy Analytics - an AI-powered chatbot that lets you analyze your CRM data using natural language. No SQL knowledge required!"

*Show the clean chatbot interface*

### 2. Simple Query Demo (1 minute)

**Type:** "What is our total revenue this month?"

*Wait for response*

**Highlight:**
- Natural language understanding
- Real-time SQL generation
- Conversational response with actual numbers

**Expected output:** 
"Your total revenue for December 2024 is $234,567.00 from 12 closed deals."

### 3. Top Performers Query (1 minute)

**Type:** "Show me the top 5 deals by amount"

**Highlight:**
- Automatic sorting and limiting
- Formatted list output
- Deal names and amounts

**Expected output:**
```
Here are your top 5 deals by amount:
1. Deal 15 - $48,920
2. Deal 7 - $45,230
3. Deal 19 - $42,100
4. Deal 3 - $38,450
5. Deal 11 - $35,200
```

### 4. Product Analysis (1 minute)

**Type:** "Which product is selling the most?"

**Highlight:**
- Multi-table joins (products + deals)
- Aggregation and grouping
- Business insights

**Expected output:**
"Analytics Suite is your top-selling product with 7 deals totaling $234,500 in revenue."

### 5. Customer Insights (1 minute)

**Type:** "List all contacts from technology companies"

**Highlight:**
- Complex joins (contacts + accounts)
- Industry filtering
- Contact details

**Expected output:**
"I found 2 contacts from technology companies:
- John Doe (john.doe@acme.com) from Acme Corp
- Sarah Johnson (sarah@techstartup.com) from Tech Startup Inc"

### 6. Time-Based Analysis (1 minute)

**Type:** "How many deals are closing this week?"

**Highlight:**
- Date calculations
- Current week filtering
- Predictive insights

**Expected output:**
"You have 3 deals closing this week with a total value of $87,450. The largest is Deal 8 for $45,000 closing on Friday."

### 7. Advanced Query (1 minute)

**Type:** "What's the average deal size by industry?"

**Highlight:**
- Complex aggregations
- Multiple joins
- Business intelligence

**Expected output:**
```
Average deal size by industry:
- Technology: $35,420
- Manufacturing: $28,900
- Retail: $22,350
- Software: $41,200
```

### 8. Error Handling Demo (30 seconds)

**Type:** "Show me the weather forecast"

**Highlight:**
- Graceful error handling
- Helpful error messages
- System boundaries

**Expected output:**
"I can only help with queries about your CRM data including deals, contacts, accounts, products, and sales activities. Please ask about your sales data."

### 9. Conclusion (30 seconds)

"Easy Analytics transforms how you interact with your CRM data:
- No SQL knowledge needed
- Instant insights from natural language
- Secure and scalable
- Works with your existing CRM"

## Key Talking Points

### During Simple Queries:
- "Notice how it understands context - 'this month' automatically uses current date"
- "The AI generates optimized SQL behind the scenes"
- "Results are presented in conversational format"

### During Complex Queries:
- "It handles multiple table joins automatically"
- "Aggregations and calculations are done in real-time"
- "The system understands business terminology"

### Performance:
- "Responses typically come back in 2-3 seconds"
- "Can handle databases with millions of records"
- "Uses OpenAI for natural language, your data stays secure"

## Common Questions & Answers

**Q: How secure is this?**
A: Your data never leaves your infrastructure. Only the question goes to OpenAI, not your actual data.

**Q: Can it handle complex queries?**
A: Yes! It can do joins, aggregations, date calculations, and more.

**Q: What if it makes a mistake?**
A: Users can see the generated SQL and results are always validated against your actual data.

**Q: How much does it cost?**
A: Only the OpenAI API usage (typically pennies per query) plus your infrastructure costs.

## Troubleshooting Tips

If something goes wrong during demo:

1. **Slow response:** "The AI is processing a complex query..."
2. **Error message:** "Let me rephrase that question..."
3. **No data:** "Let's check if we have data for that time period..."
4. **Connection issue:** "Let me refresh the connection..."

## Post-Demo Actions

1. Share the GitHub repository
2. Provide the setup guide
3. Offer a trial period
4. Schedule follow-up for production deployment

## Demo Variations

### For Technical Audience:
- Show the generated SQL
- Explain the architecture
- Discuss API integration

### For Business Audience:
- Focus on insights
- Show ROI calculations
- Emphasize ease of use

### For Sales Teams:
- Query about sales performance
- Show activity tracking
- Demonstrate pipeline analysis 