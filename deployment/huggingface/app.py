"""
HuggingFace Spaces Deployment for Ottawa RAG Chatbot
Optimized for Spaces environment with space-specific configurations
"""

import os
import sys
import logging
from pathlib import Path

# HuggingFace Spaces specific setup
SPACES_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SPACES_ROOT / "src"))

# Configure logging for Spaces
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_spaces_config():
    """Get configuration optimized for HuggingFace Spaces"""
    
    # HuggingFace Spaces automatically provides GROQ_API_KEY as a secret
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        logger.warning("GROQ_API_KEY not found - running in demo mode")
        logger.info("To enable full functionality:")
        logger.info("1. Go to your Space settings")
        logger.info("2. Add GROQ_API_KEY to Repository secrets")
        logger.info("3. Restart the Space")
    
    return {
        "data_path": str(SPACES_ROOT / "data" / "processed" / "ottawa_chunks.json"),
        "groq_api_key": groq_api_key,
        "enable_admin": True,  # Enable for demos
        "enable_analytics": True,  # Track usage in Spaces
    }

def create_demo_data():
    """Create demo data if processed data doesn't exist"""
    data_dir = SPACES_ROOT / "data" / "processed"
    data_file = data_dir / "ottawa_chunks.json"
    
    if not data_file.exists():
        logger.warning("Processed data not found - creating demo dataset")
        
        # Create directories
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal demo dataset
        demo_data = {
            "metadata": {
                "processing_date": "2024-01-01T00:00:00",
                "chunk_size": 800,
                "chunk_overlap": 100,
                "statistics": {
                    "documents_processed": 10,
                    "chunks_created": 50,
                    "total_characters": 40000,
                    "avg_chunk_length": 800
                }
            },
            "documents": [
                {
                    "url": "https://ottawa.ca/en/residents/marriage-licenses",
                    "title": "Marriage Licenses - City of Ottawa",
                    "content": "Information about marriage license applications in Ottawa...",
                    "scraped_at": "2024-01-01T00:00:00"
                }
            ],
            "chunks": [
                {
                    "id": "chunk_000001",
                    "document_id": "doc_000001",
                    "chunk_index": 0,
                    "content": "To apply for a marriage license in Ottawa, both parties must appear in person at City Hall. You need to bring valid government-issued photo ID and birth certificate. The fee is $145 and can be paid by cash, debit, or credit card. The license is valid for 90 days.",
                    "content_length": 280,
                    "url": "https://ottawa.ca/en/residents/marriage-licenses",
                    "title": "Marriage Licenses",
                    "keywords": ["marriage", "license", "ottawa", "city hall", "fee"],
                    "processed_at": "2024-01-01T00:00:00"
                },
                {
                    "id": "chunk_000002", 
                    "document_id": "doc_000001",
                    "chunk_index": 1,
                    "content": "For parking in downtown Ottawa, you can use the ParkByPhone app or pay at parking meters. Rates vary by zone and time of day. Monday to Saturday parking enforcement is from 7 AM to 6 PM. Sunday is free parking on most streets.",
                    "content_length": 250,
                    "url": "https://ottawa.ca/en/parking-transit-and-streets/parking",
                    "title": "Parking Information",
                    "keywords": ["parking", "downtown", "ottawa", "rates", "enforcement"],
                    "processed_at": "2024-01-01T00:00:00"
                }
            ]
        }
        
        import json
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(demo_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created demo data at {data_file}")
        return True
    
    return False

def main():
    """Main function for HuggingFace Spaces deployment"""
    
    logger.info("🏛️ Ottawa City Services Chatbot - HuggingFace Spaces")
    logger.info("Starting deployment...")
    
    # Create demo data if needed
    demo_created = create_demo_data()
    if demo_created:
        logger.info("Running with demo data - limited functionality")
    
    # Get configuration
    config = get_spaces_config()
    
    try:
        # Import and initialize chatbot
        from chatbot import OttawaChatbot
        
        logger.info("Initializing chatbot...")
        chatbot = OttawaChatbot(**config)
        
        # Launch for Spaces (different config than local)
        logger.info("Launching Gradio interface for HuggingFace Spaces...")
        
        # HuggingFace Spaces specific launch configuration
        demo = chatbot.interface
        
        # Spaces expects the interface to be available as 'demo'
        return demo
        
    except Exception as e:
        logger.error(f"Error launching chatbot: {e}")
        
        # Fallback: create a simple error interface
        import gradio as gr
        
        def error_interface():
            with gr.Blocks(title="Ottawa Chatbot - Error") as demo:
                gr.HTML(f"""
                    <div style="text-align: center; padding: 20px; color: red;">
                        <h2>🚨 Deployment Error</h2>
                        <p>There was an error initializing the chatbot.</p>
                        <p><strong>Error:</strong> {str(e)}</p>
                        <p>Please check the Space logs for more details.</p>
                    </div>
                """)
                
                with gr.Row():
                    gr.Markdown("""
                    ### Troubleshooting Steps:
                    1. **Check API Key**: Ensure GROQ_API_KEY is set in Space secrets
                    2. **Check Data**: Verify processed data files exist
                    3. **Check Dependencies**: Ensure all requirements are installed
                    4. **Check Logs**: Review Space logs for detailed error messages
                    
                    ### Contact Information:
                    - **GitHub**: [amin8448/ottawa-rag-chatbot](https://github.com/amin8448/ottawa-rag-chatbot)
                    - **Email**: amin8448@gmail.com
                    """)
            
            return demo
        
        return error_interface()

# For HuggingFace Spaces compatibility
if __name__ == "__main__":
    demo = main()
    if hasattr(demo, 'launch'):
        demo.launch()
else:
    # When imported by Spaces
    demo = main()