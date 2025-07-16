// Add as JS query in ToolJet workflow
async function fullSync() {
  const endpoints = ['deals', 'contacts', 'accounts', 'products', 'sales_activities'];
  const baseUrl = appsmith.store.FRESHWORKS_DOMAIN ? `https://${appsmith.store.FRESHWORKS_DOMAIN}.freshworks.com/crm/sales/api/` : '';
  if (!baseUrl) throw new Error('Missing Freshworks domain');

  for (let endpoint of endpoints) {
    let page = 1;
    let allData = [];
    while (true) {
      const response = await queries[`fetch${endpoint.charAt(0).toUpperCase() + endpoint.slice(1)}`].run({ page });
      if (response.error) throw new Error(`API error for ${endpoint}`);
      allData = allData.concat(response[endpoint] || []);
      if (!response.links || !response.links.next) break;
      page++;
      await new Promise(r => setTimeout(r, 1000)); // Delay for rate limits
    }
    const transformed = allData.map(item => ({
      // Adjust mapping per API docs
      id: item.id,
      // Example for deals
      ...(endpoint === 'deals' ? { name: item.name, amount: parseFloat(item.amount), close_date: new Date(item.expected_close_on), product_id: item.products?.[0]?.id, account_id: item.sales_account?.id, contact_id: item.contacts?.[0]?.id } : {}),
      // Add similar for other endpoints
      ...(endpoint === 'contacts' ? { first_name: item.first_name, last_name: item.last_name, email: item.email } : {}),
      ...(endpoint === 'accounts' ? { name: item.name, industry: item.industry } : {}),
      ...(endpoint === 'products' ? { name: item.name, price: parseFloat(item.price) } : {}),
      ...(endpoint === 'sales_activities' ? { deal_id: item.targetable_id, activity_type: item.activity_type, date: new Date(item.scheduled_at), outcome: item.outcome } : {})
    }));
    await queries[`upsert${endpoint.charAt(0).toUpperCase() + endpoint.slice(1)}`].run({ data: transformed });
  }
  // Log success (e.g., to ToolJet DB or file)
  console.log('Sync completed');
  return { status: 'success' };
} 