# ToolJet Cloud Setup (Alternative)

If self-hosting continues to have issues, use ToolJet Cloud:

## 1. Sign Up
- Go to: https://app.tooljet.com
- Sign up with your email

## 2. Configure Data Sources
### Freshworks CRM:
- Type: REST API
- Base URL: `https://kambaacrm.myfreshworks.com`
- Headers: `Authorization: Token token=2IbbXJgW_QJLDOBwl7Znqw`

### OpenAI:
- Type: OpenAI
- API Key: `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`

## 3. Working Endpoints
- `/crm/sales/api/sales_activities`
- `/crm/sales/api/tasks`

## 4. Import Configuration
Use the files we created:
- `easy_analytics_app.json` - Chatbot interface
- `fetch_queries.json` - API queries
- `db_schema.sql` - Database setup

This gives you the same functionality while we fix the self-hosting issue. 