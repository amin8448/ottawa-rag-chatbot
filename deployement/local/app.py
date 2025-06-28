"""
Local deployment with complete RAG system
This showcases the full technical implementation
"""

import gradio as gr
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from rag_pipeline import OttawaRAGPipeline

class FullOttawaDemo:
    """
    Complete Ottawa RAG demonstration
    Uses the full 133 documents and 1,410 chunks
    """
    
    def __init__(self):
        self.pipeline = None
        self.is_initialized = False
        self.stats = {}
        
    def initialize_system(self):
        """Initialize the complete RAG system"""
        try:
            print("🚀 Initializing complete Ottawa RAG system...")
            
            # Initialize pipeline
            self.pipeline = OttawaRAGPipeline(
                data_path="../../data/processed/ottawa_chunks.json",
                groq_api_key=os.getenv("GROQ_API_KEY")
            )
            
            # Load full dataset
            success = self.pipeline.load_full_dataset()
            if not success:
                return False
            
            # Initialize vector database
            success = self.pipeline.initialize_vector_database()
            if not success:
                return False
            
            # Get system stats
            self.stats = self.pipeline.get_system_stats()
            self.is_initialized = True
            
            print("✅ System initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def answer_question(self, question: str) -> str:
        """Process question through complete RAG pipeline"""
        if not self.is_initialized:
            return "❌ System not initialized. Please restart the application."
        
        try:
            # Get complete response
            response = self.pipeline.answer_question(question)
            
            # Format response
            answer = response['answer']
            sources = response.get('sources', [])
            confidence = response.get('confidence', 0.0)
            chunks_used = response.get('chunks_used', 0)
            
            # Add metadata
            formatted_response = f"{answer}\n\n"
            formatted_response += f"**📊 Response Metadata:**\n"
            formatted_response += f"• Confidence: {confidence:.2f}\n"
            formatted_response += f"• Chunks analyzed: {chunks_used}\n"
            formatted_response += f"• Sources found: {len(sources)}\n\n"
            
            if sources:
                formatted_response += "**📚 Sources:**\n"
                for i, source in enumerate(sources[:3], 1):
                    formatted_response += f"{i}. [{source['source_file']}]({source['url']}) (similarity: {source['similarity']:.2f})\n"
            
            return formatted_response
            
        except Exception as e:
            return f"❌ Error processing question: {str(e)}"

# Initialize demo
demo_app = FullOttawaDemo()
initialization_success = demo_app.initialize_system()

# Create Gradio interface
def chat_interface(message, history):
    """Chat interface for complete RAG system"""
    response = demo_app.answer_question(message)
    history.append([message, response])
    return history, ""

# Build interface
with gr.Blocks(title="Ottawa RAG - Complete Implementation") as demo:
    gr.Markdown(f"""
    # 🏛️ Ottawa City Services RAG - Complete Implementation
    
    This demonstrates the **full technical implementation** with:
    
    ## 📊 System Statistics
    - **Documents**: {demo_app.stats.get('documents_loaded', 'Loading...')} Ottawa city pages
    - **Text Chunks**: {demo_app.stats.get('chunks_available', 'Loading...')} processed chunks
    - **Embedding Model**: {demo_app.stats.get('embedding_model', 'all-MiniLM-L6-v2')}
    - **Vector Dimension**: {demo_app.stats.get('embedding_dimension', 384)}
    - **LLM**: Groq API (Llama 3-8B)
    
    ## 🔧 Technical Features
    - ✅ Complete web scraping pipeline (Scrapy)
    - ✅ Intelligent text chunking (LangChain)
    - ✅ Semantic embeddings (SentenceTransformers)
    - ✅ Vector search (ChromaDB)
    - ✅ LLM generation (Groq API)
    - ✅ Source attribution and confidence scoring
    """)
    
    if initialization_success:
        chatbot = gr.Chatbot([], height=500)
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask about Ottawa city services...",
                scale=4
            )
            send_btn = gr.Button("Send", scale=1, variant="primary")
        
        gr.Examples([
            "How do I apply for a marriage license in Ottawa?",
            "What are the detailed rules for backyard fires?",
            "What items can and cannot go in my green bin?",
            "What are the complete requirements for a business license?",
            "What are all the parking regulations in downtown Ottawa?"
        ], inputs=msg)
        
        # Event handlers
        msg.submit(chat_interface, [msg, chatbot], [chatbot, msg])
        send_btn.click(chat_interface, [msg, chatbot], [chatbot, msg])
        
    else:
        gr.Markdown("❌ **System initialization failed.** Please check the data files and API configuration.")
    
    gr.Markdown("""
    ---
    
    ## 🏗️ Architecture Overview
    
    **Data Pipeline**: Web Scraping → Text Processing → Embedding Generation → Vector Storage  
    **Query Pipeline**: Question → Embedding → Vector Search → Context Retrieval → LLM Generation → Response  
    **Technology Stack**: Python • Scrapy • LangChain • SentenceTransformers • ChromaDB • Groq • Gradio  
    
    **💻 [View Complete Source Code on GitHub](https://github.com/yourusername/ottawa-rag-chatbot)**
    """)

if __name__ == "__main__":
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860
    )