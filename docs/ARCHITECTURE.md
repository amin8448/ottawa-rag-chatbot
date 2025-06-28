# System Architecture

## 🏗️ Overview

The Ottawa City Services RAG Chatbot follows a modern, scalable architecture designed for production deployment and easy maintenance.

## 📊 High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Processing     │    │   Retrieval     │
│                 │    │   Pipeline      │    │    System       │
│  • Ottawa.ca    │───▶│  • Web Scraper  │───▶│  • Vector DB    │
│  • City Docs    │    │  • Text Chunker │    │  • Embeddings   │
│  • PDFs         │    │  • Embeddings   │    │  • Search       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐           │
│  User Interface │    │  Generation     │           │
│                 │    │    System       │           │
│  • Gradio Web   │◀───│  • Groq LLM     │◀──────────┘
│  • REST API     │    │  • Prompt Eng   │
│  • Mobile       │    │  • Response Gen │
└─────────────────┘    └─────────────────┘
```

## 🔄 Data Flow

### 1. Data Ingestion Pipeline
```
Ottawa.ca → Scrapy Spider → Raw HTML → BeautifulSoup → Clean Text → JSON Storage
```

### 2. Processing Pipeline
```
Raw Text → Text Chunking → Sentence Transformers → Vector Embeddings → ChromaDB
```

### 3. Query Pipeline
```
User Query → Embedding → Vector Search → Context Retrieval → LLM Generation → Response
```

## 🧩 Component Architecture

### Core Components

#### 1. **Web Scraper** (`src/scraper.py`)
- **Technology**: Scrapy + BeautifulSoup
- **Purpose**: Extract content from Ottawa.ca
- **Features**:
  - Respectful crawling with delays
  - Content quality filtering
  - Metadata preservation
  - Error handling and retries

#### 2. **Data Processor** (`src/data_processor.py`)
- **Technology**: LangChain + Custom Logic
- **Purpose**: Transform raw text into optimal chunks
- **Features**:
  - Intelligent text chunking
  - Overlap strategy for context preservation
  - Metadata enrichment
  - Quality validation

#### 3. **Vector Store** (`src/vector_store.py`)
- **Technology**: ChromaDB + SentenceTransformers
- **Purpose**: Store and search semantic embeddings
- **Features**:
  - 384-dimensional embeddings
  - Cosine similarity search
  - Metadata filtering
  - Persistent storage

#### 4. **RAG Pipeline** (`src/rag_pipeline.py`)
- **Technology**: Custom orchestration
- **Purpose**: Coordinate retrieval and generation
- **Features**:
  - Query processing
  - Context assembly
  - Response generation
  - Source attribution

#### 5. **LLM Interface** (`src/llm_interface.py`)
- **Technology**: Groq API + Llama 3-8B
- **Purpose**: Generate natural language responses
- **Features**:
  - Prompt engineering
  - Temperature control
  - Token management
  - Error handling

#### 6. **Chatbot Orchestrator** (`src/chatbot.py`)
- **Technology**: Gradio + FastAPI
- **Purpose**: User interface and API endpoints
- **Features**:
  - Web interface
  - REST API
  - Session management
  - Response formatting

## 🗄️ Data Architecture

### Storage Layers

#### 1. **Raw Data Layer**
```
data/raw/
├── ottawa_pages/           # Scraped HTML content
├── pdfs/                   # Downloaded PDF documents
└── metadata/               # Crawl metadata and logs
```

#### 2. **Processed Data Layer**
```
data/processed/
├── chunks.json            # Text chunks with metadata
├── embeddings.pkl         # Precomputed embeddings
└── index.json             # Search index mapping
```

#### 3. **Vector Database Layer**
```
data/vector_store/
├── chroma.sqlite3         # ChromaDB database
├── embeddings/            # Vector storage
└── metadata/              # Collection metadata
```

### Data Models

#### Document Schema
```python
{
    "id": "doc_123",
    "title": "Marriage Licenses",
    "content": "To apply for a marriage license...",
    "url": "https://ottawa.ca/...",
    "last_updated": "2024-01-15",
    "section": "marriage",
    "chunk_index": 0,
    "metadata": {
        "word_count": 245,
        "language": "en",
        "confidence": 0.95
    }
}
```

#### Query Schema
```python
{
    "query": "How do I get married in Ottawa?",
    "embedding": [0.1, 0.2, ...],  # 384-dim vector
    "filters": {
        "section": "marriage",
        "language": "en"
    },
    "k": 5,  # Number of results
    "threshold": 0.7  # Similarity threshold
}
```

## ⚡ Performance Architecture

### Optimization Strategies

#### 1. **Embedding Optimization**
- **Model**: all-MiniLM-L6-v2 (384-dim, fast inference)
- **Batch Processing**: Process multiple queries simultaneously
- **Caching**: Store frequent query embeddings
- **Precomputation**: Generate embeddings during data processing

#### 2. **Vector Search Optimization**
- **Indexing**: HNSW algorithm for approximate search
- **Filtering**: Metadata pre-filtering before vector search
- **Pagination**: Limit result sets for performance
- **Parallelization**: Concurrent similarity calculations

#### 3. **LLM Optimization**
- **Model Selection**: Groq for fast inference
- **Prompt Optimization**: Minimal, focused prompts
- **Token Management**: Efficient context window usage
- **Caching**: Cache responses for identical queries

### Scalability Patterns

#### 1. **Horizontal Scaling**
```
Load Balancer
├── App Instance 1 (Gradio + RAG)
├── App Instance 2 (Gradio + RAG)
└── App Instance N (Gradio + RAG)
           │
    Shared Vector DB
```

#### 2. **Service Decomposition**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │  RAG API    │    │ Vector API  │
│   Service   │───▶│   Service   │───▶│   Service   │
│  (Gradio)   │    │ (FastAPI)   │    │ (ChromaDB)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🔒 Security Architecture

### Security Layers

#### 1. **API Security**
- Rate limiting
- API key validation
- Input sanitization
- CORS configuration

#### 2. **Data Security**
- No PII storage
- Public data only
- Secure environment variables
- Audit logging

#### 3. **Infrastructure Security**
- HTTPS enforcement
- Container security
- Network isolation
- Dependency scanning

## 🚀 Deployment Architecture

### Deployment Options

#### 1. **Local Development**
```
localhost:7860 (Gradio) → RAG Pipeline → Local ChromaDB
```

#### 2. **Hugging Face Spaces**
```
HF Spaces → Gradio App → Embedded RAG → Cloud Storage
```

#### 3. **Container Deployment**
```
Docker Container → App + Dependencies → External Vector DB
```

#### 4. **Microservices (Future)**
```
API Gateway → [Frontend, RAG, Vector, LLM] Services → Shared Database
```

## 📊 Monitoring Architecture

### Observability Stack

#### 1. **Metrics**
- Response times
- Query success rates
- Vector search performance
- LLM token usage

#### 2. **Logging**
- Structured JSON logs
- Query and response logging
- Error tracking
- Performance metrics

#### 3. **Health Checks**
- API endpoint health
- Database connectivity
- LLM service availability
- Vector search performance

## 🔄 Update Architecture

### Data Refresh Pipeline

#### 1. **Scheduled Updates**
```
Cron Job → Web Scraper → Data Processor → Vector Store Update → Cache Invalidation
```

#### 2. **Incremental Updates**
```
Change Detection → Delta Scraping → Partial Reprocessing → Index Updates
```

#### 3. **Manual Updates**
```
Admin Interface → Upload Content → Process & Index → Deployment
```

## 🧪 Testing Architecture

### Testing Layers

#### 1. **Unit Tests**
- Component isolation
- Mock external dependencies
- Fast execution
- High coverage

#### 2. **Integration Tests**
- End-to-end workflows
- Real database connections
- API contract testing
- Performance validation

#### 3. **System Tests**
- Full deployment testing
- Load testing
- User acceptance testing
- Regression testing

---

## 📈 Future Architecture Considerations

### Planned Enhancements

1. **Multi-language Support**: Separate embeddings per language
2. **Real-time Updates**: WebSocket for live data refresh
3. **Advanced RAG**: Query expansion and re-ranking
4. **Analytics**: User behavior and query analytics
5. **Federation**: Multi-city data federation

### Scaling Roadmap

1. **Phase 1**: Single-city optimization
2. **Phase 2**: Multi-city support
3. **Phase 3**: Government partnership integration
4. **Phase 4**: Enterprise-grade platform

---

*This architecture document is updated with each major release. For implementation details, see the source code and API documentation.*
