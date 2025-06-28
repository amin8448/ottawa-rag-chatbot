#!/usr/bin/env python3
"""
Ottawa City Services RAG Chatbot - Setup Script
Automated setup for development and deployment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil

class OttawaRAGSetup:
    """Setup manager for Ottawa RAG Chatbot"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.system = platform.system().lower()
        
    def print_banner(self):
        """Print setup banner"""
        print("\n" + "="*60)
        print("🏛️  OTTAWA CITY SERVICES RAG CHATBOT SETUP")
        print("="*60)
        print("🚀 Intelligent Ottawa city services assistant")
        print("📍 Complete RAG pipeline from scratch")
        print("⚡ Production-ready deployment")
        print("="*60 + "\n")
    
    def check_python_version(self):
        """Check Python version compatibility"""
        print("🐍 Checking Python version...")
        
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required. Current:", sys.version)
            return False
        
        print(f"✅ Python {self.python_version} - Compatible!")
        return True
    
    def create_directories(self):
        """Create necessary project directories"""
        print("📁 Creating project directories...")
        
        directories = [
            "data/raw",
            "data/processed", 
            "data/vector_store",
            "logs",
            "tests",
            "docs",
            "deployment/local",
            "deployment/docker",
            "deployment/huggingface",
            "notebooks"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep for empty directories
            gitkeep = dir_path / ".gitkeep"
            if not any(dir_path.iterdir()) and not gitkeep.exists():
                gitkeep.touch()
        
        print("✅ Directories created successfully!")
    
    def setup_virtual_environment(self):
        """Set up Python virtual environment"""
        print("🔧 Setting up virtual environment...")
        
        venv_name = "ottawa-py311-env"
        venv_path = self.project_root / venv_name
        
        if venv_path.exists():
            print(f"✅ Virtual environment '{venv_name}' already exists!")
            return True
        
        try:
            # Create virtual environment
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], check=True)
            
            print(f"✅ Virtual environment '{venv_name}' created!")
            
            # Instructions for activation
            if self.system == "windows":
                activate_cmd = f"{venv_name}\\Scripts\\activate"
            else:
                activate_cmd = f"source {venv_name}/bin/activate"
            
            print(f"💡 Activate with: {activate_cmd}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        
        # Check if we're in a virtual environment
        in_venv = (hasattr(sys, 'real_prefix') or 
                   (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
        
        if not in_venv:
            print("⚠️  Warning: Not in virtual environment!")
            print("   Activate your virtual environment first:")
            if self.system == "windows":
                print("   ottawa-py311-env\\Scripts\\activate")
            else:
                print("   source ottawa-py311-env/bin/activate")
            
            response = input("\nContinue anyway? (y/N): ").lower()
            if response != 'y':
                return False
        
        try:
            # Upgrade pip first
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True)
            
            # Install specific protobuf version first (fix ChromaDB issue)
            subprocess.run([
                sys.executable, "-m", "pip", "install", "protobuf==3.20.3"
            ], check=True)
            
            # Install requirements
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)
            else:
                # Install essential packages manually
                essential_packages = [
                    "gradio==4.8.0",
                    "sentence-transformers==2.2.2", 
                    "chromadb==0.4.15",
                    "groq==0.4.1",
                    "pandas==2.1.3",
                    "python-dotenv==1.0.0",
                    "beautifulsoup4==4.12.2",
                    "requests==2.31.0"
                ]
                
                for package in essential_packages:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], check=True)
            
            print("✅ Dependencies installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_environment_file(self):
        """Set up .env file from template"""
        print("🔐 Setting up environment file...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists():
            print("✅ .env file already exists!")
            return True
        
        if env_example.exists():
            # Copy example to .env
            shutil.copy(env_example, env_file)
            print("✅ Created .env from template!")
            print("💡 Edit .env file and add your GROQ_API_KEY")
        else:
            # Create basic .env file
            basic_env = """# Ottawa RAG Chatbot Environment Variables
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=development
DEBUG=True
VECTOR_DB_PATH=data/chroma_db
LOG_LEVEL=INFO
"""
            with open(env_file, 'w') as f:
                f.write(basic_env)
            
            print("✅ Created basic .env file!")
            print("💡 Add your GROQ_API_KEY to .env file")
        
        return True
    
    def test_installation(self):
        """Test the installation"""
        print("🧪 Testing installation...")
        
        tests = [
            ("Import gradio", "import gradio"),
            ("Import sentence_transformers", "import sentence_transformers"),
            ("Import chromadb", "import chromadb"),
            ("Import groq", "import groq"),
            ("Import pandas", "import pandas"),
            ("Load environment", "from dotenv import load_dotenv; load_dotenv('.env')")
        ]
        
        failed_tests = []
        
        for test_name, test_code in tests:
            try:
                exec(test_code)
                print(f"  ✅ {test_name}")
            except Exception as e:
                print(f"  ❌ {test_name}: {e}")
                failed_tests.append(test_name)
        
        if failed_tests:
            print(f"\n⚠️  {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"    - {test}")
            return False
        else:
            print("\n🎉 All tests passed!")
            return True
    
    def display_next_steps(self):
        """Display next steps for users"""
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        
        print("\n📋 NEXT STEPS:")
        print("1. 🔑 Add your Groq API key to .env file:")
        print("   GROQ_API_KEY=your_actual_api_key_here")
        print("\n2. 📄 Process sample data (optional):")
        print("   python simple_processor.py")
        print("\n3. 🚀 Launch the chatbot:")
        print("   python launch_chatbot.py")
        print("\n4. 🌐 Open browser to:")
        print("   http://localhost:7860")
        
        print("\n🔗 USEFUL LINKS:")
        print("• Groq API: https://console.groq.com/keys")
        print("• Documentation: docs/")
        print("• Issues: GitHub Issues")
        
        print("\n🆘 NEED HELP?")
        print("• Check logs/ directory for error logs")
        print("• Run tests: pytest tests/")
        print("• Read CONTRIBUTING.md for development guide")
        
        print("\n" + "="*60)
        print("Happy coding! 🚀")
        print("="*60 + "\n")
    
    def run_setup(self):
        """Run the complete setup process"""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_python_version():
            return False
        
        # Setup steps
        setup_steps = [
            ("Creating directories", self.create_directories),
            ("Setting up virtual environment", self.setup_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up environment file", self.setup_environment_file),
            ("Testing installation", self.test_installation)
        ]
        
        for step_name, step_function in setup_steps:
            print(f"\n📍 {step_name}...")
            if not step_function():
                print(f"❌ Setup failed at: {step_name}")
                return False
        
        # Show next steps
        self.display_next_steps()
        return True

def main():
    """Main setup function"""
    setup = OttawaRAGSetup()
    
    try:
        success = setup.run_setup()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())