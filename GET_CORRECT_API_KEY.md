# How to Get Your Correct Freshworks CRM API Key

## 🚨 Current Issue
Your API key is returning **403 Forbidden** - this means:
- ❌ The key doesn't have permission to access CRM data
- ❌ It might be a Freshdesk key instead of Freshsales CRM key
- ❌ API access might not be enabled for your account

## 📋 Step-by-Step to Get Correct API Key

### 1. Login to Freshworks CRM
Go to: https://kambaacrm.myfreshworks.com

### 2. Navigate to API Settings
- Click your **profile icon** (top right)
- Select **Settings**
- Look for **API** or **API Settings** in the left menu

### 3. Check API Access
- Ensure **API Access** is ENABLED
- If not, you may need admin privileges to enable it

### 4. Get Your API Key
There are typically two places to find it:

**Option A: Personal Settings**
- Profile → Settings → API → Your API Key

**Option B: Admin Settings** (if you're an admin)
- Admin Settings → API → API Settings

### 5. Verify It's the Right Key
A valid Freshsales CRM API key should:
- Be 20+ characters long
- Work with format: `Token token=YOUR_API_KEY`
- Have access to `/crm/sales/api/` endpoints

## 🔍 Quick Test Your New Key

Once you have a new key, test it:

1. Update the key in your .env file:
   ```
   FRESHWORKS_API_KEY=your_new_api_key_here
   ```

2. Run the test:
   ```cmd
   python check_freshworks_access.py
   ```

## ⚠️ Common Issues

### "I don't see API Settings"
- Your user role might not have API access
- Contact your Freshworks admin to enable API access for your account

### "API is disabled"
- Only admins can enable API access
- Go to: Admin Settings → Apps & Integrations → API

### "Still getting 403"
Your account might need specific permissions:
- View Contacts permission
- View Deals permission
- API Access permission

## 🎯 Alternative: Use Admin Account

If your account doesn't have API access:
1. Ask your Freshworks admin for an API key
2. Or login with an admin account to generate one

## 📝 What Your API Key Should Access

For the chatbot to work, the API key needs access to:
- Contacts
- Deals
- Accounts (Companies)
- Products
- Sales Activities

## Need Help?

If you're still having issues:
1. Contact your Freshworks administrator
2. Check Freshworks support: https://support.freshworks.com
3. Ensure your Freshworks plan includes API access (some basic plans don't) 