// Enhanced Chatbot Handler for Comprehensive CRM Queries
async function handleQuery() {
  const userInput = components.queryInput.value;
  if (!userInput) return 'Please enter a query';
  
  try {
    // Enhanced prompt with ALL available fields and tables
    const sqlPrompt = `Generate SQL for: ${userInput}

Available tables and their key fields:

1. deals - id, name, amount, base_currency_amount, expected_close_on, closed_on, stage_id, probability, 
   deal_stage, is_won, is_lost, owner_id, sales_account_id, currency_id, created_at, updated_at, 
   last_contacted_at, forecast_category, age, temperature, contacts (JSONB), products (JSONB), 
   custom_fields (JSONB), tags[], recent_note, deal_prediction

2. contacts - id, first_name, last_name, display_name, email, job_title, city, state, country, 
   work_number, mobile_number, lead_score, last_contacted, open_deals_amount, won_deals_amount, 
   owner_id, life_cycle_stage_id, contact_status_id, created_at, updated_at, custom_fields (JSONB), 
   tags[], sales_accounts (JSONB), deals (JSONB), tasks (JSONB), appointments (JSONB)

3. accounts - id, name, address, city, state, country, number_of_employees, annual_revenue, website, 
   phone, industry_type_id, business_type_id, owner_id, open_deals_amount, won_deals_amount, 
   open_deals_count, won_deals_count, created_at, updated_at, custom_fields (JSONB), tags[], 
   contacts (JSONB), deals (JSONB)

4. sales_activities - id, title, notes, start_date, end_date, is_completed, targetable_type, 
   targetable_id, activity_type, activity_sub_type, owner_id, outcome_id, location, deal_ids[], 
   contact_ids[], sales_account_ids[], created_at, updated_at

5. appointments - id, title, description, location, from_date, end_date, is_allday, time_zone, 
   provider, creater_id, outcome_id, conference_id, targetables (JSONB), deal_ids[], contact_ids[], 
   account_ids[], created_at, updated_at

6. tasks - id, title, description, due_date, status, priority, is_completed, completed_date, 
   owner_id, targetable_type, targetable_id, associated_deal_ids[], associated_contact_ids[], 
   created_at, updated_at

7. products - id, name, description, sku_number, unit_price, cost, active, currency_id, 
   product_category_id, created_at, updated_at

8. leads - id, first_name, last_name, email, company_name, lead_source_id, lead_status_id, 
   lead_score, converted, converted_at, converted_contact_id, converted_account_id, 
   converted_deal_id, owner_id, created_at, updated_at

9. sales_team - id, display_name, email, is_active, work_number, mobile_number, job_title, 
   team_id, role_id, created_at, last_login_at

10. contact_statuses - id, name, position, probability, is_won, is_lost, deal_pipeline_id

11. deal_pipelines - id, name, is_active, is_default, stages (JSONB)

12. campaigns - id, name, start_date, end_date, budget, actual_cost, expected_revenue, 
    campaign_type, campaign_status, leads_generated, deals_influenced, revenue_influenced

Common queries patterns:
- Deal queries: closed deals, won/lost deals, deals by stage, deals by amount, pipeline analysis
- Contact queries: contacts by status, lead score, last contacted, lifecycle stage
- Activity queries: activities by type, completed vs pending, activities by date
- Team performance: deals by owner, activities by team member
- Time-based: deals closing this month, overdue tasks, recent activities

Use appropriate JOINs when needed. For JSONB fields, use jsonb operators (->>, @>, etc).
For array fields, use ANY() or array operators.
Output ONLY the SQL query, no explanations.`;

    await queries.generateSQL.run({ prompt: sqlPrompt });
    const sql = queries.generateSQL.data.choices[0].message.content.trim();
    
    // Execute the SQL query
    await queries.executeSQL.run({ sql });
    
    // Enhanced summarization prompt
    const summaryPrompt = `Summarize these CRM query results in natural language:
Query: ${userInput}
SQL: ${sql}
Results: ${JSON.stringify(queries.executeSQL.data)}

Provide a clear, business-friendly summary. Include:
- Direct answer to the question
- Key insights or patterns
- Relevant metrics or counts
- Any notable findings

Format numbers with appropriate units (currency, percentages, etc).`;

    await queries.summarizeResults.run({ prompt: summaryPrompt });
    const summary = queries.summarizeResults.data.choices[0].message.content;
    
    // Append to chat history
    components.chatHistory.value += `User: ${userInput}\nAI: ${summary}\n\n`;
    return summary;
    
  } catch (error) {
    // Enhanced error handling with suggestions
    const errorMessage = `Error: ${error.message}`;
    const suggestions = `

Try queries like:
- How many deals are closed this month?
- Show me all won deals by amount
- Which deals are in negotiation stage?
- List contacts with high lead scores
- What's the pipeline conversion rate?
- Show overdue tasks
- Which team member has the most deals?
- What are the upcoming appointments?
- Show me deals without any activities in the last 30 days
- Which accounts have the highest deal value?`;
    
    return errorMessage + suggestions;
  }
} 