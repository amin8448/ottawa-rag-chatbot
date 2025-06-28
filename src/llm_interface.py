"""
Simple LLM Interface for Ottawa RAG Pipeline
Fixed version that handles Groq client compatibility issues
"""

import os
from typing import Dict, Any, Optional, List
import logging
import time
from datetime import datetime

class LLMInterface:
    """
    Simple LLM interface that handles Groq API compatibility issues
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "llama3-8b-8192",
        max_tokens: int = 1000,
        temperature: float = 0.1,
        timeout: int = 30
    ):
        """Initialize the LLM interface"""
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        
        # Initialize client
        self._setup_logging()
        self._initialize_client()
        
        # Response statistics
        self.total_requests = 0
        self.total_tokens_used = 0
        self.avg_response_time = 0.0
        
    def _setup_logging(self):
        """Setup logging for LLM operations"""
        self.logger = logging.getLogger(__name__)
        
    def _initialize_client(self):
        """Initialize Groq client with multiple fallback methods"""
        try:
            if not self.api_key:
                self.logger.warning("No Groq API key provided - running in demo mode")
                self.client = None
                return
            
            # Try to import and initialize Groq client
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                self.logger.info(f"Groq client initialized with model: {self.model_name}")
                
            except Exception as e:
                self.logger.error(f"Error initializing Groq client: {e}")
                self.logger.warning("Running in demo mode without LLM")
                self.client = None
                
        except ImportError:
            self.logger.error("Groq package not available")
            self.client = None
    
    def generate_response(
        self,
        query: str,
        context: str,
        use_ottawa_prompt: bool = True,
        custom_prompt: Optional[str] = None,
        max_retries: int = 3
    ) -> str:
        """Generate response using LLM with context"""
        
        if not self.client:
            return self._get_fallback_response(query)
        
        try:
            # Build the prompt
            if custom_prompt:
                prompt = custom_prompt.format(query=query, context=context)
            elif use_ottawa_prompt:
                prompt = self._build_ottawa_prompt(query, context)
            else:
                prompt = self._build_generic_prompt(query, context)
            
            # Generate response with retries
            for attempt in range(max_retries):
                try:
                    start_time = time.time()
                    
                    completion = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant for Ottawa city services. Provide accurate, helpful information based on official sources."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                    )
                    
                    response_time = time.time() - start_time
                    
                    # Extract response
                    response = completion.choices[0].message.content
                    
                    # Update statistics
                    self._update_statistics(completion, response_time)
                    
                    self.logger.info(f"Generated response in {response_time:.2f}s")
                    return response.strip()
                    
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        return self._get_fallback_response(query)
                    time.sleep(2 ** attempt)  # Exponential backoff
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(query)
    
    def _build_ottawa_prompt(self, query: str, context: str) -> str:
        """Build optimized prompt for Ottawa city services"""
        prompt = f"""Based on the following official Ottawa city information, please answer the user's question accurately and helpfully.

CONTEXT FROM OTTAWA.CA:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Provide a clear, accurate answer based on the context above
2. If the context contains specific procedures, list them step by step
3. Include relevant fees, locations, or contact information when available
4. If the context doesn't fully answer the question, say so clearly
5. Always prioritize official Ottawa information over general knowledge
6. Be helpful and conversational while remaining factual
7. If mentioning fees or procedures, note that information should be verified on ottawa.ca as it may change

RESPONSE:"""
        
        return prompt
    
    def _build_generic_prompt(self, query: str, context: str) -> str:
        """Build generic prompt for general questions"""
        return f"""Context: {context}

Question: {query}

Please provide a helpful and accurate answer based on the context above. If the context doesn't contain enough information to answer the question, please say so clearly.

Answer:"""
    
    def _get_fallback_response(self, query: str) -> str:
        """Generate fallback response when LLM fails"""
        fallback_responses = {
            "marriage": "For marriage license information, please visit ottawa.ca or call 311.",
            "parking": "For parking information and regulations, please visit ottawa.ca or call 311.",
            "garbage": "For waste collection information, please visit ottawa.ca or call 311.",
            "fire": "For fire safety information, please visit ottawa.ca or contact Ottawa Fire Services.",
            "business": "For business licensing information, please visit ottawa.ca or call 311."
        }
        
        query_lower = query.lower()
        for keyword, response in fallback_responses.items():
            if keyword in query_lower:
                return f"I apologize, but I'm experiencing technical difficulties. {response}"
        
        return "I apologize, but I'm unable to process your request at the moment. Please visit ottawa.ca or call 311 for assistance with Ottawa city services."
    
    def _update_statistics(self, completion: Any, response_time: float):
        """Update usage statistics"""
        try:
            self.total_requests += 1
            
            # Update response time (moving average)
            self.avg_response_time = (
                (self.avg_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
            
            # Update token usage if available
            if hasattr(completion, 'usage') and completion.usage:
                if hasattr(completion.usage, 'total_tokens'):
                    self.total_tokens_used += completion.usage.total_tokens
            
        except Exception as e:
            self.logger.warning(f"Error updating statistics: {e}")
    
    def is_available(self) -> bool:
        """Check if the LLM service is available"""
        if not self.client:
            return False
        
        try:
            # Make a simple test request
            test_completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "Test"
                    }
                ],
                max_tokens=5,
                temperature=0.1
            )
            
            return bool(test_completion.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"LLM availability check failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration"""
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "api_available": self.is_available(),
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "avg_response_time": round(self.avg_response_time, 2)
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the LLM interface
    llm = LLMInterface(api_key=os.getenv("GROQ_API_KEY"))
    
    if llm.is_available():
        print("✅ LLM service is available")
        
        # Test response generation
        test_query = "How do I apply for a marriage license?"
        test_context = """To apply for a marriage license in Ottawa:
        1. Both parties must appear in person at City Hall
        2. Bring valid government-issued photo ID
        3. Bring birth certificate or equivalent
        4. Fee is $145 (cash, debit, or credit card)
        5. License is valid for 90 days"""
        
        response = llm.generate_response(test_query, test_context)
        print(f"Response: {response}")
        
    else:
        print("❌ LLM service is not available - running in demo mode")