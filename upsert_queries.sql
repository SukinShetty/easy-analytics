-- Example for deals (adapt for others in ToolJet DB queries)
INSERT INTO deals (id, name, amount, close_date, product_id, account_id, contact_id)
SELECT * FROM jsonb_to_recordset({{data}}) AS x(id bigint, name text, amount decimal, close_date date, product_id bigint, account_id bigint, contact_id bigint)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  amount = EXCLUDED.amount,
  close_date = EXCLUDED.close_date,
  product_id = EXCLUDED.product_id,
  account_id = EXCLUDED.account_id,
  contact_id = EXCLUDED.contact_id;

-- Repeat pattern for contacts, accounts, products, sales_activities 