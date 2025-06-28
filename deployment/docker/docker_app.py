"""
Docker-optimized application for Ottawa RAG Chatbot
Handles container-specific configuration and health checks
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path
from typing import Optional
import argparse

# Add src to path
sys.path.insert(0, '/app/src')

# Configure logging for container environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/chatbot.log')
    ]
)
logger = logging.getLogger(__name__)

class DockerChatbot:
    """Docker-optimized chatbot wrapper"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.chatbot = None
        self.shutdown_requested = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    def check_environment(self) -> dict:
        """Check Docker environment and configuration"""
        status = {
            "container_ready": True,
            "api_key_configured": bool(os.getenv("GROQ_API_KEY")),
            "data_available": False,
            "disk_space": "Unknown",
            "memory_available": "Unknown"
        }
        
        # Check data availability
        data_path = Path("/app/data/processed/ottawa_chunks.json")
        status["data_available"] = data_path.exists()
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage("/app")
            status["disk_space"] = f"{free // (2**30)}GB free"
        except Exception:
            pass
        
        # Check memory (if psutil available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            status["memory_available"] = f"{memory.available // (2**30)}GB available"
        except ImportError:
            pass
        
        return status
    
    def create_health_endpoint(self):
        """Create health check endpoint for Docker"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading
        import json
        
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    # Health check logic
                    status = self.server.chatbot_instance.check_environment()
                    
                    if status["container_ready"]:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "status": "healthy",
                            "timestamp": time.time(),
                            **status
                        }).encode())
                    else:
                        self.send_response(503)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "status": "unhealthy",
                            "timestamp": time.time(),
                            **status
                        }).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress default HTTP logging
                pass
        
        # Start health check server in background
        def run_health_server():
            server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
            server.chatbot_instance = self
            server.serve_forever()
        
        health_thread = threading.Thread(target=run_health_server, daemon=True)
        health_thread.start()
        logger.info("Health check endpoint started on port 8080")
    
    def initialize_chatbot(self) -> bool:
        """Initialize the chatbot with Docker-specific config"""
        try:
            logger.info("Initializing Ottawa RAG Chatbot for Docker deployment...")
            
            # Check environment
            env_status = self.check_environment()
            logger.info(f"Environment status: {env_status}")
            
            # Configuration for Docker
            config = {
                "data_path": "/app/data/processed/ottawa_chunks.json",
                "groq_api_key": os.getenv("GROQ_API_KEY"),
                "enable_admin": True,
                "enable_analytics": True
            }
            
            # Import and initialize chatbot
            from chatbot import OttawaChatbot
            self.chatbot = OttawaChatbot(**config)
            
            logger.info("Chatbot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            return False
    
    def run(self):
        """Main run method for Docker container"""
        logger.info("🏛️ Ottawa RAG Chatbot - Docker Deployment")
        logger.info("=" * 50)
        
        # Create health endpoint
        self.create_health_endpoint()
        
        # Initialize chatbot
        if not self.initialize_chatbot():
            logger.error("Failed to initialize chatbot, exiting...")
            return 1
        
        try:
            # Launch Gradio interface
            logger.info("Starting Gradio interface...")
            
            # Configure for Docker environment
            launch_kwargs = {
                "server_name": "0.0.0.0",  # Listen on all interfaces
                "server_port": 7860,
                "share": False,
                "debug": self.debug,
                "show_error": True,
                "quiet": not self.debug,
                "inbrowser": False  # No browser in container
            }
            
            if self.chatbot:
                # Start the interface
                logger.info("Chatbot ready and accessible on port 7860")
                self.chatbot.interface.launch(**launch_kwargs)
            else:
                logger.error("Chatbot not initialized")
                return 1
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Error running chatbot: {e}")
            return 1
        finally:
            logger.info("Shutting down chatbot...")
        
        return 0

def create_demo_data():
    """Create demo data if processed data doesn't exist"""
    data_dir = Path("/app/data/processed")
    data_file = data_dir / "ottawa_chunks.json"
    
    if not data_file.exists():
        logger.info("Creating demo data for Docker deployment...")
        
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Import and use demo data creation from HF deployment
        demo_data = {
            "metadata": {
                "processing_date": "2024-01-01T00:00:00",
                "chunk_size": 800,
                "chunk_overlap": 100,
                "statistics": {
                    "documents_processed": 5,
                    "chunks_created": 25,
                    "total_characters": 20000,
                    "avg_chunk_length": 800
                }
            },
            "documents": [
                {
                    "url": "https://ottawa.ca/en/residents/marriage-licenses",
                    "title": "Marriage Licenses - City of Ottawa",
                    "content": "Marriage license information for Ottawa residents...",
                    "scraped_at": "2024-01-01T00:00:00"
                }
            ],
            "chunks": [
                {
                    "id": "chunk_000001",
                    "document_id": "doc_000001",
                    "chunk_index": 0,
                    "content": "To apply for a marriage license in Ottawa, both parties must appear in person at City Hall located at 110 Laurier Avenue West. You need to bring valid government-issued photo ID and birth certificate. The fee is $145 and can be paid by cash, debit, or credit card. The license is valid for 90 days from the date of issue.",
                    "content_length": 320,
                    "url": "https://ottawa.ca/en/residents/marriage-licenses",
                    "title": "Marriage Licenses",
                    "keywords": ["marriage", "license", "ottawa", "city hall", "fee", "ID", "birth certificate"],
                    "processed_at": "2024-01-01T00:00:00"
                },
                {
                    "id": "chunk_000002",
                    "document_id": "doc_000002", 
                    "chunk_index": 0,
                    "content": "Parking in downtown Ottawa is managed through various methods. You can use the ParkByPhone app or pay at parking meters. Rates vary by zone and time of day. Monday to Saturday parking enforcement is from 7 AM to 6 PM. Sunday is free parking on most streets, except for special event areas.",
                    "content_length": 290,
                    "url": "https://ottawa.ca/en/parking-transit-and-streets/parking",
                    "title": "Parking Information",
                    "keywords": ["parking", "downtown", "ottawa", "rates", "enforcement", "ParkByPhone"],
                    "processed_at": "2024-01-01T00:00:00"
                }
            ]
        }
        
        import json
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(demo_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Demo data created at {data_file}")

def main():
    """Main entry point for Docker deployment"""
    
    parser = argparse.ArgumentParser(description='Ottawa RAG Chatbot - Docker Deployment')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Create demo data if needed
    create_demo_data()
    
    # Initialize and run chatbot
    docker_chatbot = DockerChatbot(debug=args.debug)
    
    try:
        exit_code = docker_chatbot.run()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()