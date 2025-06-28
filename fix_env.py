#!/usr/bin/env python3
"""
Fix environment setup for Ottawa RAG Chatbot
"""

import os
from pathlib import Path

def fix_environment():
    """Fix environment file and setup"""
    
    print("🔧 Fixing environment setup...")
    
    project_root = Path(__file__).parent
    env_file = project_root / '.env'
    
    # Check current .env content
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read().strip()
        
        print(f"📄 Current .env content:")
        print(f"   {content}")
        
        # Check if API key is properly set
        if 'GROQ_API_KEY=' in content:
            # Extract the API key value
            for line in content.split('\n'):
                if line.startswith('GROQ_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    
                    if api_key and api_key != 'your_groq_api_key_here' and len(api_key) > 10:
                        print("✅ Groq API key appears to be properly set")
                        return True
                    else:
                        print("⚠️  API key is empty or using placeholder")
                        break
        
        print("❌ API key not properly configured")
        
        # Ask user to input their API key
        print("\n🔑 Please enter your Groq API key:")
        print("   (You can get one from: https://console.groq.com/keys)")
        
        try:
            new_api_key = input("API Key: ").strip()
            
            if new_api_key and len(new_api_key) > 10:
                # Update .env file
                new_content = f"GROQ_API_KEY={new_api_key}\n"
                
                with open(env_file, 'w') as f:
                    f.write(new_content)
                
                print("✅ API key updated successfully!")
                return True
            else:
                print("❌ Invalid API key provided")
                return False
                
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled")
            return False
    
    else:
        print("❌ .env file not found")
        
        # Create .env file
        try:
            api_key = input("Enter your Groq API key: ").strip()
            
            if api_key and len(api_key) > 10:
                with open(env_file, 'w') as f:
                    f.write(f"GROQ_API_KEY={api_key}\n")
                
                print("✅ Created .env file with API key!")
                return True
            else:
                print("❌ Invalid API key")
                return False
                
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled")
            return False

def main():
    """Main function"""
    
    success = fix_environment()
    
    if success:
        print("\n🎉 Environment setup completed!")
        print("\n🚀 Next steps:")
        print("1. Run: python create_demo_data.py")
        print("2. Run: python test_setup.py")
        print("3. Run: python deployment/local/run_local.py")
    else:
        print("\n❌ Environment setup failed")
        print("Please manually edit the .env file and add:")
        print("GROQ_API_KEY=your_actual_groq_api_key")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())