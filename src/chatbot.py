"""
Ottawa City Services RAG Chatbot
Complete Gradio interface integrating all RAG pipeline components
"""

import os
import gradio as gr
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json
from pathlib import Path

# Import your RAG pipeline components - absolute imports
from rag_pipeline import OttawaRAGPipeline
from data_processor import DataProcessor
from embeddings import EmbeddingManager
from vector_store import VectorStore
from llm_interface import LLMInterface


class OttawaChatbot:
    """
    Complete Ottawa City Services Chatbot Interface

    Features:
    - Beautiful Gradio interface with Ottawa branding
    - Real-time RAG question answering
    - Source citations and confidence scores
    - Example questions and help system
    - Admin panel for system monitoring
    - Session history and analytics
    """

    def __init__(
        self,
        data_path: str = "data/processed/ottawa_chunks.json",
        groq_api_key: Optional[str] = None,
        enable_admin: bool = True,
        enable_analytics: bool = True,
    ):
        """
        Initialize the Ottawa chatbot

        Args:
            data_path: Path to processed Ottawa data
            groq_api_key: Groq API key for LLM
            enable_admin: Enable admin monitoring panel
            enable_analytics: Enable usage analytics
        """
        self.data_path = data_path
        self.enable_admin = enable_admin
        self.enable_analytics = enable_analytics

        # Initialize RAG pipeline
        self.pipeline = None
        self.pipeline_initialized = False

        # Session tracking
        self.session_history = []
        self.total_questions = 0
        self.successful_responses = 0

        # Setup logging
        self._setup_logging()

        # Initialize pipeline
        self._initialize_pipeline(groq_api_key)

        # Create Gradio interface
        self.interface = self._create_interface()

    def _setup_logging(self):
        """Setup logging for the chatbot"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_pipeline(self, groq_api_key: Optional[str]):
        """Initialize the RAG pipeline"""
        try:
            self.logger.info("Initializing Ottawa RAG Pipeline...")

            # Initialize pipeline
            self.pipeline = OttawaRAGPipeline(
                data_path=self.data_path, groq_api_key=groq_api_key
            )

            # Load dataset
            if self.pipeline.load_full_dataset():
                self.logger.info("Dataset loaded successfully")

                # Initialize vector database
                if self.pipeline.initialize_vector_database():
                    self.pipeline_initialized = True
                    self.logger.info("RAG Pipeline initialized successfully")
                else:
                    self.logger.error("Failed to initialize vector database")
            else:
                self.logger.error("Failed to load dataset")

        except Exception as e:
            self.logger.error(f"Error initializing pipeline: {e}")
            self.pipeline_initialized = False

    def _create_interface(self) -> gr.Blocks:
        """Create the complete Gradio interface"""

        # Custom CSS for Ottawa branding
        custom_css = """
        .ottawa-header {
            background: linear-gradient(90deg, #d41e2c 0%, #1f4788 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .ottawa-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .ottawa-subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .example-questions {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .source-citation {
            background: #e8f4fd;
            border-left: 4px solid #1f4788;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .confidence-high { color: #28a745; font-weight: bold; }
        .confidence-medium { color: #ffc107; font-weight: bold; }
        .confidence-low { color: #dc3545; font-weight: bold; }
        
        .stats-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 10px;
            margin: 5px;
            text-align: center;
        }
        """

        with gr.Blocks(
            css=custom_css, title="Ottawa City Services Assistant"
        ) as interface:
            # Header
            with gr.Row():
                gr.HTML(
                    """
                    <div class="ottawa-header">
                        <div class="ottawa-title">🏛️ Ottawa City Services Assistant</div>
                        <div class="ottawa-subtitle">
                            Intelligent assistant powered by AI • Ask questions about Ottawa city services
                        </div>
                    </div>
                """
                )

            # Main chat interface
            with gr.Tab("💬 Ask Questions"):
                with gr.Row():
                    with gr.Column(scale=2):
                        # Chat interface
                        chatbot_display = gr.Chatbot(
                            label="Ottawa Services Assistant",
                            height=400,
                            show_label=True,
                            container=True,
                            bubble_full_width=False,
                        )

                        with gr.Row():
                            question_input = gr.Textbox(
                                placeholder="Ask me about Ottawa city services (marriage licenses, parking, waste collection, etc.)",
                                label="Your Question",
                                lines=2,
                                max_lines=5,
                            )
                            submit_btn = gr.Button("Ask", variant="primary", scale=0)

                        # Example questions
                        gr.HTML(
                            """
                            <div class="example-questions">
                                <strong>💡 Try asking about:</strong><br>
                                • "How do I apply for a marriage license?"<br>
                                • "What are the rules for backyard fires?"<br>
                                • "What can I put in my green bin?"<br>
                                • "How do I get a business license?"<br>
                                • "What are the parking regulations downtown?"
                            </div>
                        """
                        )

                        # Quick action buttons
                        with gr.Row():
                            example_btn1 = gr.Button(
                                "Marriage License", variant="secondary", scale=1
                            )
                            example_btn2 = gr.Button(
                                "Parking Rules", variant="secondary", scale=1
                            )
                            example_btn3 = gr.Button(
                                "Waste Collection", variant="secondary", scale=1
                            )
                            example_btn4 = gr.Button(
                                "Fire Safety", variant="secondary", scale=1
                            )

                    with gr.Column(scale=1):
                        # Response metadata
                        confidence_display = gr.HTML(label="Response Confidence")
                        sources_display = gr.HTML(label="Sources")

                        # System status
                        with gr.Accordion("System Status", open=False):
                            status_display = gr.HTML()

                # Clear chat button
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat", variant="secondary")

            # Admin panel (if enabled)
            if self.enable_admin:
                with gr.Tab("📊 System Monitor"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 📈 Usage Statistics")
                            stats_display = gr.HTML()
                            refresh_stats_btn = gr.Button(
                                "Refresh Stats", variant="secondary"
                            )

                        with gr.Column():
                            gr.Markdown("### ⚙️ Pipeline Status")
                            pipeline_status = gr.HTML()
                            refresh_pipeline_btn = gr.Button(
                                "Refresh Pipeline", variant="secondary"
                            )

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 📋 Recent Questions")
                            recent_questions = gr.DataFrame(
                                headers=[
                                    "Time",
                                    "Question",
                                    "Response Status",
                                    "Confidence",
                                ],
                                label="Question History",
                            )

            # Help and about
            with gr.Tab("ℹ️ About"):
                gr.Markdown(
                    """
                ### About Ottawa City Services Assistant
                
                This AI assistant helps you find information about Ottawa city services using official sources from ottawa.ca.
                
                **How it works:**
                1. 🕷️ **Web Scraping**: Collected 133+ official Ottawa.ca documents
                2. 📝 **Text Processing**: Split into 1,410 intelligent chunks with overlap
                3. 🧠 **AI Embeddings**: Generated semantic embeddings for smart search
                4. 🔍 **Vector Search**: Find relevant information using similarity matching
                5. 🤖 **AI Generation**: Create natural responses with source citations
                
                **Features:**
                - ✅ Real-time responses in under 1 second
                - ✅ Source citations from official ottawa.ca pages
                - ✅ Confidence scores for response quality
                - ✅ Complete coverage of major city services
                
                **Technical Stack:**
                - **Data**: 133 ottawa.ca documents, 1,410 text chunks
                - **Embeddings**: SentenceTransformers (384-dimensional)
                - **Vector Store**: ChromaDB for fast retrieval
                - **LLM**: Groq API with Llama 3-8B
                - **Interface**: Gradio with Ottawa branding
                
                ---
                
                **⚠️ Important Notes:**
                - Information is based on Ottawa.ca content at time of scraping
                - Always verify current fees and procedures on ottawa.ca
                - For urgent matters, call 311 or visit ottawa.ca directly
                
                **Built with ❤️ by Amin Nabavi**
                """
                )

            # Event handlers
            def process_question(
                question: str, history: List
            ) -> Tuple[List, str, str, str]:
                """Process user question and return response with metadata"""
                try:
                    if not question.strip():
                        return history, "", "", self._get_status_html()

                    if not self.pipeline_initialized:
                        error_msg = (
                            "⚠️ System not ready. Please check the system status."
                        )
                        history.append([question, error_msg])
                        return history, "", "", self._get_status_html()

                    # Track question
                    self.total_questions += 1

                    # Get response from RAG pipeline
                    response_data = self.pipeline.answer_question(question)

                    if response_data.get("answer"):
                        self.successful_responses += 1

                        # Format response
                        answer = response_data["answer"]
                        confidence = response_data.get("confidence", 0.0)
                        sources = response_data.get("sources", [])

                        # Add to history
                        history.append([question, answer])

                        # Track session
                        self._track_session(question, response_data)

                        # Format metadata displays
                        confidence_html = self._format_confidence(confidence)
                        sources_html = self._format_sources(sources)

                        return (
                            history,
                            confidence_html,
                            sources_html,
                            self._get_status_html(),
                        )

                    else:
                        error_response = "I'm sorry, I couldn't find relevant information about that topic. Please try rephrasing your question or ask about other Ottawa city services."
                        history.append([question, error_response])
                        return history, "", "", self._get_status_html()

                except Exception as e:
                    self.logger.error(f"Error processing question: {e}")
                    error_response = "I encountered an error processing your question. Please try again."
                    history.append([question, error_response])
                    return history, "", "", self._get_status_html()

            def clear_chat():
                """Clear the chat history"""
                return [], "", "", self._get_status_html()

            def set_example_question(example_text: str):
                """Set example question in input field"""
                return example_text

            # Connect event handlers
            submit_btn.click(
                process_question,
                inputs=[question_input, chatbot_display],
                outputs=[
                    chatbot_display,
                    confidence_display,
                    sources_display,
                    status_display,
                ],
            ).then(lambda: "", outputs=[question_input])

            question_input.submit(
                process_question,
                inputs=[question_input, chatbot_display],
                outputs=[
                    chatbot_display,
                    confidence_display,
                    sources_display,
                    status_display,
                ],
            ).then(lambda: "", outputs=[question_input])

            clear_btn.click(
                clear_chat,
                outputs=[
                    chatbot_display,
                    confidence_display,
                    sources_display,
                    status_display,
                ],
            )

            # Example button handlers
            example_btn1.click(
                lambda: "How do I apply for a marriage license?",
                outputs=[question_input],
            )
            example_btn2.click(
                lambda: "What are the parking regulations in downtown Ottawa?",
                outputs=[question_input],
            )
            example_btn3.click(
                lambda: "What can I put in my green bin for waste collection?",
                outputs=[question_input],
            )
            example_btn4.click(
                lambda: "What are the rules for backyard fires?",
                outputs=[question_input],
            )

            # Admin panel handlers (if enabled)
            if self.enable_admin:
                refresh_stats_btn.click(self._get_usage_stats, outputs=[stats_display])

                refresh_pipeline_btn.click(
                    self._get_pipeline_status, outputs=[pipeline_status]
                )

                # Auto-refresh recent questions
                interface.load(self._get_recent_questions, outputs=[recent_questions])

        return interface

    def _format_confidence(self, confidence: float) -> str:
        """Format confidence score with colored display"""
        if confidence >= 0.8:
            css_class = "confidence-high"
            emoji = "🟢"
        elif confidence >= 0.5:
            css_class = "confidence-medium"
            emoji = "🟡"
        else:
            css_class = "confidence-low"
            emoji = "🔴"

        return f"""
        <div style="text-align: center; padding: 10px;">
            <div style="font-size: 18px;">{emoji}</div>
            <div class="{css_class}">Confidence: {confidence:.1%}</div>
        </div>
        """

    def _format_sources(self, sources: List[Dict]) -> str:
        """Format sources with citations"""
        if not sources:
            return "<div>No sources available</div>"

        sources_html = "<div><strong>📚 Sources:</strong></div>"

        for i, source in enumerate(sources[:3]):  # Show top 3 sources
            url = source.get("url", "")
            similarity = source.get("similarity", 0.0)

            if url:
                # Clean URL for display
                display_url = url.replace("https://ottawa.ca/", "").replace(
                    "https://", ""
                )
                if len(display_url) > 50:
                    display_url = display_url[:47] + "..."

                sources_html += f"""
                <div class="source-citation">
                    <strong>Source {i+1}:</strong> 
                    <a href="{url}" target="_blank">{display_url}</a>
                    <br><small>Relevance: {similarity:.1%}</small>
                </div>
                """

        return sources_html

    def _get_status_html(self) -> str:
        """Get current system status HTML"""
        if not self.pipeline_initialized:
            return """
            <div style="color: red;">
                ❌ <strong>System Not Ready</strong><br>
                Pipeline initialization failed
            </div>
            """

        stats = self.pipeline.get_system_stats() if self.pipeline else {}

        return f"""
        <div style="color: green;">
            ✅ <strong>System Ready</strong><br>
            📄 {stats.get('documents_loaded', 0)} documents<br>
            📝 {stats.get('chunks_available', 0)} chunks<br>
            🎯 {self.successful_responses}/{self.total_questions} successful
        </div>
        """

    def _track_session(self, question: str, response_data: Dict[str, Any]):
        """Track session data for analytics"""
        if self.enable_analytics:
            session_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "confidence": response_data.get("confidence", 0.0),
                "sources_count": len(response_data.get("sources", [])),
                "response_length": len(response_data.get("answer", "")),
                "success": bool(response_data.get("answer")),
            }

            self.session_history.append(session_entry)

            # Keep only last 100 entries
            if len(self.session_history) > 100:
                self.session_history = self.session_history[-100:]

    def _get_usage_stats(self) -> str:
        """Get usage statistics HTML"""
        if not self.enable_analytics:
            return "<div>Analytics disabled</div>"

        success_rate = (self.successful_responses / max(self.total_questions, 1)) * 100
        avg_confidence = 0

        if self.session_history:
            confidences = [
                entry["confidence"]
                for entry in self.session_history
                if entry["success"]
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return f"""
        <div class="stats-box">
            <h4>📊 Usage Statistics</h4>
            <p><strong>Total Questions:</strong> {self.total_questions}</p>
            <p><strong>Success Rate:</strong> {success_rate:.1f}%</p>
            <p><strong>Avg Confidence:</strong> {avg_confidence:.1%}</p>
            <p><strong>Session Length:</strong> {len(self.session_history)} interactions</p>
        </div>
        """

    def _get_pipeline_status(self) -> str:
        """Get pipeline status HTML"""
        if not self.pipeline:
            return "<div style='color: red;'>❌ Pipeline not initialized</div>"

        stats = self.pipeline.get_system_stats()

        return f"""
        <div class="stats-box">
            <h4>⚙️ Pipeline Status</h4>
            <p><strong>Documents:</strong> {stats.get('documents_loaded', 0)}</p>
            <p><strong>Chunks:</strong> {stats.get('chunks_available', 0)}</p>
            <p><strong>Embedding Model:</strong> {stats.get('embedding_model', 'N/A')}</p>
            <p><strong>Vector DB:</strong> {'✅ Ready' if stats.get('vector_db_initialized') else '❌ Not Ready'}</p>
            <p><strong>LLM:</strong> {'✅ Available' if stats.get('llm_available') else '❌ Not Available'}</p>
        </div>
        """

    def _get_recent_questions(self) -> List[List[str]]:
        """Get recent questions for admin panel"""
        if not self.enable_analytics or not self.session_history:
            return []

        recent = self.session_history[-10:]  # Last 10 questions
        return [
            [
                entry["timestamp"][:19].replace("T", " "),  # Format timestamp
                entry["question"][:50] + ("..." if len(entry["question"]) > 50 else ""),
                "✅ Success" if entry["success"] else "❌ Failed",
                f"{entry['confidence']:.1%}",
            ]
            for entry in reversed(recent)
        ]

    def launch(
        self,
        share: bool = False,
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
        debug: bool = False,
    ):
        """Launch the Gradio interface"""

        if not self.pipeline_initialized:
            self.logger.warning("Pipeline not initialized - running in demo mode")

        self.logger.info(f"Launching Ottawa Chatbot on {server_name}:{server_port}")

        return self.interface.launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
            debug=debug,
            show_error=True,
            inbrowser=True,
        )


# Standalone execution
def main():
    """Main function for standalone execution"""

    # Configuration
    DATA_PATH = "data/processed/ottawa_chunks.json"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY:
        print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
        print("   Set your API key: export GROQ_API_KEY='your_key_here'")
        print("   The chatbot will run in demo mode without LLM responses")

    # Check if data file exists
    if not Path(DATA_PATH).exists():
        print(f"⚠️  Warning: Data file not found at {DATA_PATH}")
        print("   Run the data processor first to create processed chunks")
        print("   The chatbot will run in demo mode")

    # Initialize and launch chatbot
    chatbot = OttawaChatbot(
        data_path=DATA_PATH,
        groq_api_key=GROQ_API_KEY,
        enable_admin=True,
        enable_analytics=True,
    )

    # Launch with public sharing for demos
    chatbot.launch(
        share=False,  # Set to True for public sharing
        server_name="127.0.0.1",
        server_port=7860,
        debug=False,
    )


if __name__ == "__main__":
    main()
