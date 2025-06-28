#!/usr/bin/env python3
"""
Fix Groq client initialization in llm_interface.py
Replace the _initialize_client method to handle the proxies error
"""

from pathlib import Path
import re

def fix_groq_initialization():
    """Fix the Groq client initialization issue"""
    
    file_path = Path("src/llm_interface.py")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🔧 Fixing Groq initialization in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the _initialize_client method and replace it
    old_method_pattern = r'def _initialize_client\(self\):.*?except Exception as e:.*?self\.client = None.*?self\.logger\.warning\("Running in demo mode without LLM"\)'
    
    new_method = '''def _initialize_client(self):
        """Initialize Groq client with proper error handling"""
        try:
            if not self.api_key:
                self.logger.warning("No Groq API key - demo mode")
                self.client = None
                return
            
            from groq import Groq
            
            # Try basic initialization first
            try:
                self.client = Groq(api_key=self.api_key)
                
                # Test the client with a simple request
                test_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                
                self.logger.info(f"✅ Groq client initialized successfully with model: {self.model_name}")
                
            except Exception as init_error:
                if "proxies" in str(init_error):
                    self.logger.warning("Groq client proxies issue detected, trying workaround...")
                    # Try with minimal parameters
                    self.client = Groq(api_key=self.api_key)
                    self.logger.info(f"✅ Groq client initialized with workaround")
                else:
                    raise init_error
                    
        except Exception as e:
            self.logger.error(f"❌ Error initializing Groq client: {e}")
            self.client = None
            self.logger.warning("⚠️  Running in demo mode without LLM")'''
    
    # Replace the method
    new_content = re.sub(old_method_pattern, new_method, content, flags=re.DOTALL)
    
    # If the regex didn't work, try a simpler approach
    if new_content == content:
        print("🔄 Trying alternative replacement...")
        
        # Split by lines and replace the method manually
        lines = content.split('\n')
        new_lines = []
        in_method = False
        method_indent = ""
        
        for line in lines:
            if 'def _initialize_client(self):' in line:
                in_method = True
                method_indent = line[:len(line) - len(line.lstrip())]
                
                # Add the new method
                new_lines.append(line)
                new_lines.extend([
                    f'{method_indent}    """Initialize Groq client with proper error handling"""',
                    f'{method_indent}    try:',
                    f'{method_indent}        if not self.api_key:',
                    f'{method_indent}            self.logger.warning("No Groq API key - demo mode")',
                    f'{method_indent}            self.client = None',
                    f'{method_indent}            return',
                    f'{method_indent}        ',
                    f'{method_indent}        from groq import Groq',
                    f'{method_indent}        ',
                    f'{method_indent}        # Initialize Groq client',
                    f'{method_indent}        self.client = Groq(api_key=self.api_key)',
                    f'{method_indent}        ',
                    f'{method_indent}        # Test the client',
                    f'{method_indent}        test_response = self.client.chat.completions.create(',
                    f'{method_indent}            model=self.model_name,',
                    f'{method_indent}            messages=[{{"role": "user", "content": "test"}}],',
                    f'{method_indent}            max_tokens=1',
                    f'{method_indent}        )',
                    f'{method_indent}        ',
                    f'{method_indent}        self.logger.info(f"✅ Groq client initialized successfully with model: {{self.model_name}}")',
                    f'{method_indent}        ',
                    f'{method_indent}    except Exception as e:',
                    f'{method_indent}        self.logger.error(f"❌ Error initializing Groq client: {{e}}")',
                    f'{method_indent}        self.client = None',
                    f'{method_indent}        self.logger.warning("⚠️  Running in demo mode without LLM")'
                ])
                continue
            
            if in_method:
                # Skip lines until we reach the next method
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    in_method = False
                    new_lines.append(line)
                elif line.strip().startswith('def ') and line.find('def ') <= len(method_indent):
                    in_method = False
                    new_lines.append(line)
                # Skip old method lines
                continue
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed Groq client initialization")
    return True

def main():
    """Main function"""
    
    print("🔧 Fixing Groq Client for Ottawa RAG Chatbot")
    print("=" * 50)
    
    success = fix_groq_initialization()
    
    if success:
        print("\n✅ Groq client fix applied!")
        print("\n🚀 Restart your chatbot:")
        print("   python launch_chatbot.py")
        print("\n💡 The LLM should now show as '✅ Available' in the status")
        return 0
    else:
        print("\n❌ Fix failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())