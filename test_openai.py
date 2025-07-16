#!/usr/bin/env python3
"""
Test OpenAI API Connection for Kambaa CRM Chatbot
"""

import openai

# OpenAI configuration
openai.api_key = "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"

def test_openai_connection():
    """Test basic OpenAI API connection"""
    
    print("🔑 Testing OpenAI API Connection...")
    print("=" * 50)
    
    try:
        # Simple test call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, this is a test. Please respond with 'API working'."}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API Response: {result}")
        print("✅ API connection successful!")
        return True
        
    except openai.error.AuthenticationError:
        print("❌ Authentication Error: Invalid API key")
        return False
    except openai.error.RateLimitError:
        print("❌ Rate Limit Error: Too many requests")
        return False
    except openai.error.APIError as e:
        print(f"❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_connection()
    
    if success:
        print("\n🎉 OpenAI API is working correctly!")
        print("🚀 Ready to start the chatbot!")
    else:
        print("\n⚠️  OpenAI API issue detected.")
        print("📋 Possible solutions:")
        print("   1. Check your API key is valid")
        print("   2. Ensure you have credits in your OpenAI account")
        print("   3. Check your internet connection")
        print("   4. Try again in a few minutes if rate limited") 