#!/usr/bin/env python3
"""
Simple CRM Chatbot using Real Kambaa Data
A standalone Flask app that queries your actual CRM data
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from datetime import datetime
import openai

# Initialize Flask app
app = Flask(__name__)

# OpenAI configuration
openai.api_key = "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"

class KambaaCRMData:
    def __init__(self):
        self.data = {}
        self.load_data()
    
    def load_data(self):
        """Load the real Kambaa CRM data from CSV files"""
        
        # Find the data directory
        data_dir = None
        for item in os.listdir('.'):
            if item.startswith('kambaa_crm_data_'):
                data_dir = item
                break
        
        if not data_dir:
            print("❌ No CRM data directory found")
            return
        
        print(f"📁 Loading data from: {data_dir}")
        
        # Load each data type
        data_files = {
            'sales_team': f'{data_dir}/sales_team.csv',
            'appointments': f'{data_dir}/appointments.csv',
            'contact_statuses': f'{data_dir}/contact_statuses.csv',
            'contact_filters': f'{data_dir}/contact_filters.csv'
        }
        
        for data_type, file_path in data_files.items():
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    self.data[data_type] = df
                    print(f"✅ Loaded {len(df)} {data_type} records")
                except Exception as e:
                    print(f"❌ Error loading {data_type}: {e}")
        
        print(f"🎉 Loaded {len(self.data)} data types successfully!")
    
    def get_sales_team(self):
        """Get active sales team members"""
        if 'sales_team' in self.data:
            team = self.data['sales_team']
            active_team = team[team['is_active'] == True] if 'is_active' in team.columns else team
            # Convert to dict and handle NaN values
            records = active_team.fillna('').to_dict('records')
            return records
        return []
    
    def get_appointments(self, limit=None):
        """Get appointments data"""
        if 'appointments' in self.data:
            appointments = self.data['appointments']
            if limit:
                appointments = appointments.head(limit)
            # Convert to dict and handle NaN values
            records = appointments.fillna('').to_dict('records')
            return records
        return []
    
    def search_appointments(self, query):
        """Search appointments by title or description"""
        if 'appointments' in self.data:
            appointments = self.data['appointments']
            
            # Search in title and description
            title_matches = appointments[appointments['title'].str.contains(query, case=False, na=False)]
            desc_matches = appointments[appointments['description'].str.contains(query, case=False, na=False)]
            
            # Combine and remove duplicates
            matches = pd.concat([title_matches, desc_matches]).drop_duplicates()
            # Convert to dict and handle NaN values
            records = matches.fillna('').to_dict('records')
            return records
        return []
    
    def get_stats(self):
        """Get basic statistics"""
        stats = {}
        
        if 'sales_team' in self.data:
            team = self.data['sales_team']
            stats['total_team'] = len(team)
            stats['active_team'] = len(team[team['is_active'] == True]) if 'is_active' in team.columns else len(team)
        
        if 'appointments' in self.data:
            stats['total_appointments'] = len(self.data['appointments'])
        
        if 'contact_statuses' in self.data:
            stats['pipeline_stages'] = len(self.data['contact_statuses'])
        
        return stats

# Initialize data loader
crm_data = KambaaCRMData()

def generate_ai_response(query, context_data):
    """Generate AI response using OpenAI with real CRM context"""
    
    try:
        # Prepare a clean context without complex data structures
        data_summary = ""
        
        if 'sales_team' in context_data:
            team_data = context_data['sales_team']
            if team_data:
                names = [member.get('display_name', 'Unknown') for member in team_data]
                data_summary += f"Active Sales Team: {', '.join(names)}. "
        
        if 'appointments' in context_data:
            appt_data = context_data['appointments']
            if appt_data:
                recent_titles = [appt.get('title', 'Untitled')[:50] for appt in appt_data[:5]]
                data_summary += f"Recent Appointments: {', '.join(recent_titles)}. "
        
        if 'relevant_appointments' in context_data:
            rel_appts = context_data['relevant_appointments']
            if rel_appts:
                rel_titles = [appt.get('title', 'Untitled')[:50] for appt in rel_appts]
                data_summary += f"Matching Appointments: {', '.join(rel_titles)}. "
        
        if 'stats' in context_data:
            stats = context_data['stats']
            data_summary += f"CRM Stats: {stats.get('active_team', 0)} active team members, {stats.get('total_appointments', 0)} total appointments. "
        
        # Create a clean context for OpenAI
        context = f"""You are a CRM analytics assistant for Kambaa business. 

User Question: {query}

Available Data: {data_summary}

Provide a helpful, professional response based on this actual CRM data. Be specific and mention the real data points when relevant."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful CRM analytics assistant for Kambaa business. Provide clear, actionable insights based on the real data provided."},
                {"role": "user", "content": context}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"🔴 OpenAI API Error: {e}")  # For debugging
        print(f"🔴 Error type: {type(e)}")
        import traceback
        print(f"🔴 Full traceback: {traceback.format_exc()}")
        
        # Provide intelligent fallback response using the data
        if 'sales_team' in context_data and context_data['sales_team']:
            team_names = [member.get('display_name', 'Unknown') for member in context_data['sales_team']]
            fallback = f"Based on your CRM data, your active sales team includes: {', '.join(team_names)}. "
        elif 'appointments' in context_data and context_data['appointments']:
            appt_count = len(context_data['appointments'])
            fallback = f"You have {appt_count} appointments in your CRM system. "
        elif 'stats' in context_data:
            stats = context_data['stats']
            fallback = f"Your CRM contains {stats.get('total_appointments', 0)} appointments and {stats.get('active_team', 0)} active team members. "
        else:
            fallback = "I have access to your real CRM data including sales team information and appointment details. "
        
        return f"{fallback}(Note: OpenAI API temporarily unavailable, but I can still access your real Kambaa CRM data. Error: {str(e)[:100]})"

@app.route('/')
def index():
    """Main chatbot interface"""
    stats = crm_data.get_stats()
    return render_template('chatbot.html', stats=stats)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    
    user_message = request.json.get('message', '').lower()
    print(f"📨 Received chat request: '{user_message}'")
    
    # Determine what data to provide based on the query
    context_data = {}
    
    if any(word in user_message for word in ['team', 'sales', 'members', 'people']):
        context_data['sales_team'] = crm_data.get_sales_team()
    
    if any(word in user_message for word in ['meeting', 'appointment', 'schedule']):
        context_data['appointments'] = crm_data.get_appointments(10)
    
    if any(word in user_message for word in ['nestle', 'brigade', 'super mn']):
        # Search for specific companies
        search_terms = ['nestle', 'brigade', 'super mn auto']
        for term in search_terms:
            if term in user_message:
                context_data['relevant_appointments'] = crm_data.search_appointments(term)
    
    if any(word in user_message for word in ['stats', 'summary', 'overview', 'how many']):
        context_data['stats'] = crm_data.get_stats()
    
    # If no specific context, provide general stats
    if not context_data:
        context_data['stats'] = crm_data.get_stats()
        context_data['recent_appointments'] = crm_data.get_appointments(5)
    
    # Generate AI response
    print(f"🧠 Generating AI response with context: {list(context_data.keys())}")
    ai_response = generate_ai_response(user_message, context_data)
    print(f"✅ AI response generated: {ai_response[:100]}...")
    
    return jsonify({
        'response': ai_response,
        'context_data': context_data
    })

@app.route('/api/data/<data_type>')
def get_data(data_type):
    """API endpoint to get specific data types"""
    
    if data_type == 'sales_team':
        return jsonify(crm_data.get_sales_team())
    elif data_type == 'appointments':
        return jsonify(crm_data.get_appointments())
    elif data_type == 'stats':
        return jsonify(crm_data.get_stats())
    else:
        return jsonify({'error': 'Data type not found'}), 404

# Create the HTML template
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kambaa CRM Analytics Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 800px;
            max-width: 90vw;
            height: 600px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            margin-bottom: 10px;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            font-size: 14px;
            opacity: 0.9;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .bot-message {
            background: white;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .send-button:hover {
            background: #5a6fd8;
        }
        
        .example-queries {
            padding: 10px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            font-size: 12px;
            color: #6c757d;
        }
        
        .example-queries span {
            cursor: pointer;
            color: #667eea;
            margin-right: 15px;
        }
        
        .example-queries span:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🎯 Kambaa CRM Analytics</h1>
            <div class="stats">
                <span>👥 {{stats.active_team}} Active Team Members</span>
                <span>📅 {{stats.total_appointments}} Appointments</span>
                <span>📊 {{stats.pipeline_stages}} Pipeline Stages</span>
            </div>
        </div>
        
        <div class="chat-messages" id="chat-messages">
            <div class="message bot-message">
                👋 Welcome to Kambaa CRM Analytics! I can help you analyze your real business data. 
                Ask me about your sales team, appointments, meetings with clients like Nestle, or any CRM insights you need.
            </div>
        </div>
        
        <div class="example-queries">
            <strong>Try asking:</strong>
            <span onclick="sendMessage('Who are our active sales team members?')">Who are our active sales team members?</span>
            <span onclick="sendMessage('Show me meetings with Nestle')">Show me meetings with Nestle</span>
            <span onclick="sendMessage('What appointments do we have?')">What appointments do we have?</span>
        </div>
        
        <div class="chat-input-container">
            <input type="text" class="chat-input" id="chat-input" placeholder="Ask about your CRM data..." onkeypress="handleKeyPress(event)">
            <button class="send-button" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        function addMessage(message, isUser = false) {
            const chatMessages = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            messageDiv.textContent = message;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function sendMessage(predefinedMessage = null) {
            const input = document.getElementById('chat-input');
            const message = predefinedMessage || input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, true);
            
            // Clear input
            if (!predefinedMessage) {
                input.value = '';
            }
            
            // Send to backend
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response);
            })
            .catch(error => {
                addMessage('Sorry, I encountered an error. Please try again.');
                console.error('Error:', error);
            });
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Focus on input when page loads
        document.getElementById('chat-input').focus();
    </script>
</body>
</html>
'''

# Save the HTML template
template_dir = 'templates'
if not os.path.exists(template_dir):
    os.makedirs(template_dir)

with open(f'{template_dir}/chatbot.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

if __name__ == '__main__':
    print("🚀 Starting Kambaa CRM Chatbot...")
    print("=" * 50)
    print("📊 Real data loaded successfully!")
    print("🌐 Open: http://localhost:5000")
    print("💬 Chat with your real CRM data!")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 