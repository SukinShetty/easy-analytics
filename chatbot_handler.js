// Add as JS query in ToolJet app
async function handleQuery() {
  const userInput = components.queryInput.value;
  if (!userInput) return 'Please enter a query';
  try {
    await queries.generateSQL.run({ prompt: `Generate SQL for: ${userInput}. Tables: deals(id,name,amount,close_date,product_id,account_id,contact_id), contacts(id,first_name,last_name,email), accounts(id,name,industry), products(id,name,price), sales_activities(id,deal_id,activity_type,date,outcome). Use joins/aggregations. Output only SQL.` });
    const sql = queries.generateSQL.data.choices[0].message.content.trim();
    await queries.executeSQL.run({ sql });
    await queries.summarizeResults.run({ prompt: `Summarize in natural language: ${JSON.stringify(queries.executeSQL.data)}` });
    const summary = queries.summarizeResults.data.choices[0].message.content;
    // Append to chat history
    components.chatHistory.value += `User: ${userInput}\nAI: ${summary}\n`;
    return summary;
  } catch (error) {
    return `Error: ${error.message}. Try rephrasing.`;
  }
} 