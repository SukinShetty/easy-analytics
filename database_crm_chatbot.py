#!/usr/bin/env python3
"""
Database-Connected CRM Chatbot
A Flask app that queries your CRM data directly from PostgreSQL database
"""

from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras
import json
import os
from datetime import datetime
import openai

# Initialize Flask app
app = Flask(__name__)

# OpenAI configuration
openai.api_key = "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"

class DatabaseCRMData:
    def __init__(self):
        # Database configuration
        self.db_config = {
            "host": "localhost",
            "port": "5432", 
            "database": "tooljet_prod",
            "user": "postgres",
            "password": "tooljet"
        }
        self.test_connection()
    
    def test_connection(self):
        """Test database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.close()
            print("✅ Database connection successful!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def get_sales_team(self):
        """Get active sales team members"""
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cur.execute("""
                SELECT id, display_name, email, is_active, work_number, mobile_number
                FROM sales_team 
                WHERE is_active = true
                ORDER BY display_name
            """)
            
            results = cur.fetchall()
            team_data = [dict(row) for row in results]
            
            cur.close()
            conn.close()
            return team_data
            
        except Exception as e:
            print(f"Error fetching sales team: {e}")
            return []
    
    def get_appointments(self, limit=10):
        """Get recent appointments"""
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cur.execute("""
                SELECT id, title, description, location, from_date, end_date, 
                       is_allday, time_zone, provider, creater_id
                FROM appointments 
                ORDER BY from_date DESC 
                LIMIT %s
            """, (limit,))
            
            results = cur.fetchall()
            appointments_data = []
            
            for row in results:
                appointment = dict(row)
                # Convert datetime objects to strings for JSON serialization
                if appointment['from_date']:
                    appointment['from_date'] = appointment['from_date'].isoformat()
                if appointment['end_date']:
                    appointment['end_date'] = appointment['end_date'].isoformat()
                appointments_data.append(appointment)
            
            cur.close()
            conn.close()
            return appointments_data
            
        except Exception as e:
            print(f"Error fetching appointments: {e}")
            return []
    
    def search_appointments(self, query):
        """Search appointments by title or description"""
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cur.execute("""
                SELECT id, title, description, location, from_date, end_date,
                       is_allday, time_zone, provider, creater_id
                FROM appointments 
                WHERE title ILIKE %s OR description ILIKE %s
                ORDER BY from_date DESC
                LIMIT 20
            """, (f'%{query}%', f'%{query}%'))
            
            results = cur.fetchall()
            appointments_data = []
            
            for row in results:
                appointment = dict(row)
                # Convert datetime objects to strings
                if appointment['from_date']:
                    appointment['from_date'] = appointment['from_date'].isoformat()
                if appointment['end_date']:
                    appointment['end_date'] = appointment['end_date'].isoformat()
                appointments_data.append(appointment)
            
            cur.close()
            conn.close()
            return appointments_data
            
        except Exception as e:
            print(f"Error searching appointments: {e}")
            return []
    
    def get_contact_statuses(self):
        """Get contact statuses/pipeline stages"""
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cur.execute("""
                SELECT id, name, position, forecast_type
                FROM contact_statuses 
                ORDER BY position
            """)
            
            results = cur.fetchall()
            statuses_data = [dict(row) for row in results]
            
            cur.close()
            conn.close()
            return statuses_data
            
        except Exception as e:
            print(f"Error fetching contact statuses: {e}")
            return []
    
    def get_tasks(self, limit=10):
        """Get recent tasks"""
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cur.execute("""
                SELECT id, title, description, due_date, is_completed, priority
                FROM tasks 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            results = cur.fetchall()
            tasks_data = []
            
            for row in results:
                task = dict(row)
                # Convert datetime objects to strings
                if task['due_date']:
                    task['due_date'] = task['due_date'].isoformat()
                tasks_data.append(task)
            
            cur.close()
            conn.close()
            return tasks_data
            
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []
    
    def get_deals(self, limit=10):
        """Get recent deals"""
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cur.execute("""
                SELECT id, name, amount, close_date, product_id, account_id, contact_id
                FROM deals 
                ORDER BY id DESC 
                LIMIT %s
            """, (limit,))
            
            results = cur.fetchall()
            deals_data = []
            
            for row in results:
                deal = dict(row)
                # Convert date objects to strings
                if deal['close_date']:
                    deal['close_date'] = deal['close_date'].isoformat()
                deals_data.append(deal)
            
            cur.close()
            conn.close()
            return deals_data
            
        except Exception as e:
            print(f"Error fetching deals: {e}")
            return []
    
    def get_stats(self):
        """Get basic statistics from database"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            stats = {}
            
            # Count active team members
            cur.execute("SELECT COUNT(*) FROM sales_team WHERE is_active = true")
            stats['active_team'] = cur.fetchone()[0]
            
            # Count total appointments
            cur.execute("SELECT COUNT(*) FROM appointments")
            stats['total_appointments'] = cur.fetchone()[0]
            
            # Count pipeline stages
            cur.execute("SELECT COUNT(*) FROM contact_statuses")
            stats['pipeline_stages'] = cur.fetchone()[0]
            
            # Count deals
            cur.execute("SELECT COUNT(*) FROM deals")
            stats['total_deals'] = cur.fetchone()[0]
            
            # Count pending tasks
            cur.execute("SELECT COUNT(*) FROM tasks WHERE is_completed = false")
            stats['pending_tasks'] = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {}

# Initialize data loader
crm_data = DatabaseCRMData()

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
        
        if 'deals' in context_data:
            deals_data = context_data['deals']
            if deals_data:
                deal_names = [deal.get('name', 'Unnamed Deal')[:50] for deal in deals_data[:3]]
                data_summary += f"Recent Deals: {', '.join(deal_names)}. "
        
        if 'tasks' in context_data:
            tasks_data = context_data['tasks']
            if tasks_data:
                task_titles = [task.get('title', 'Untitled Task')[:50] for task in tasks_data[:3]]
                data_summary += f"Recent Tasks: {', '.join(task_titles)}. "
        
        if 'stats' in context_data:
            stats = context_data['stats']
            data_summary += f"Database Stats: {stats.get('active_team', 0)} active team members, {stats.get('total_appointments', 0)} appointments, {stats.get('total_deals', 0)} deals, {stats.get('pending_tasks', 0)} pending tasks. "
        
        # Create a clean context for OpenAI
        context = f"""You are a CRM analytics assistant for Kambaa business. 

User Question: {query}

Available Data: {data_summary}

Provide a helpful, professional response based on this actual CRM database data. Be specific and mention the real data points when relevant."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful CRM analytics assistant for Kambaa business. Provide clear, actionable insights based on the real database data provided."},
                {"role": "user", "content": context}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"🔴 OpenAI API Error: {e}")
        
        # Provide intelligent fallback response using the database data
        if 'sales_team' in context_data and context_data['sales_team']:
            team_names = [member.get('display_name', 'Unknown') for member in context_data['sales_team']]
            fallback = f"Based on your CRM database, your active sales team includes: {', '.join(team_names)}. "
        elif 'appointments' in context_data and context_data['appointments']:
            appt_count = len(context_data['appointments'])
            fallback = f"You have {appt_count} appointments in your CRM database. "
        elif 'stats' in context_data:
            stats = context_data['stats']
            fallback = f"Your CRM database contains {stats.get('total_appointments', 0)} appointments, {stats.get('total_deals', 0)} deals, and {stats.get('active_team', 0)} active team members. "
        else:
            fallback = "I have access to your real CRM database including sales team, appointments, deals, and task data. "
        
        return f"{fallback}(Note: OpenAI API temporarily unavailable, but I can still access your real Kambaa CRM database. Error: {str(e)[:100]})"

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
    
    if any(word in user_message for word in ['deal', 'deals', 'revenue', 'sales', 'money']):
        context_data['deals'] = crm_data.get_deals(10)
    
    if any(word in user_message for word in ['task', 'tasks', 'todo', 'pending']):
        context_data['tasks'] = crm_data.get_tasks(10)
    
    if any(word in user_message for word in ['nestle', 'brigade', 'super mn']):
        # Search for specific companies
        search_terms = ['nestle', 'brigade', 'super mn auto']
        for term in search_terms:
            if term in user_message:
                context_data['relevant_appointments'] = crm_data.search_appointments(term)
    
    if any(word in user_message for word in ['stats', 'summary', 'overview', 'how many', 'pipeline']):
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
    elif data_type == 'deals':
        return jsonify(crm_data.get_deals())
    elif data_type == 'tasks':
        return jsonify(crm_data.get_tasks())
    elif data_type == 'stats':
        return jsonify(crm_data.get_stats())
    else:
        return jsonify({'error': 'Data type not found'}), 404

if __name__ == '__main__':
    print("🚀 Starting Database-Connected CRM Chatbot...")
    print("=" * 60)
    print("💾 Connected to PostgreSQL database!")
    print("🌐 Open: http://localhost:5001")
    print("💬 Chat with your real CRM database!")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001) 