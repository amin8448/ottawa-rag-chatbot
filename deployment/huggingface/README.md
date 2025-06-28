# 🤗 HuggingFace Spaces Deployment Guide

Deploy your Ottawa RAG Chatbot to HuggingFace Spaces for public access.

## 🚀 Quick Deployment

### Step 1: Create a New Space

1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure:
   - **Space name**: `OttawaCityServicesChatbot` (or your preference)
   - **License**: `MIT`
   - **SDK**: `Gradio`
   - **Hardware**: `CPU basic` (free tier)
   - **Visibility**: `Public`

### Step 2: Upload Files

Upload these files to your Space:

```
📁 Your Space Repository
├── app.py                    # Copy from deployment/huggingface/app.py
├── requirements.txt          # Copy from project root
├── README.md                 # Space description
├── 📁 src/                   # Copy entire src folder
│   ├── chatbot.py
│   ├── rag_pipeline.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── llm_interface.py
│   ├── data_processor.py
│   └── scraper.py
└── 📁 data/                  # Copy processed data (optional)
    └── processed/
        └── ottawa_chunks.json
```

### Step 3: Set API Key Secret

1. Go to your Space **Settings**
2. Click **Repository secrets**
3. Add new secret:
   - **Name**: `GROQ_API_KEY`
   - **Value**: Your actual Groq API key
4. Save the secret

### Step 4: Deploy

1. Commit and push files to your Space
2. Space will automatically build and deploy
3. Check build logs for any errors
4. Your chatbot will be live at: `https://huggingface.co/spaces/yourusername/spacename`

## 🛠️ Advanced Configuration

### Custom Space README

Create a `README.md` in your Space root:

```markdown
---
title: Ottawa City Services Chatbot
emoji: 🏛️
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: 4.16.0
app_file: app.py
pinned: false
license: mit
---

# 🏛️ Ottawa City Services RAG Chatbot

Intelligent assistant for Ottawa city services using Retrieval-Augmented Generation.

## Features
- 🔍 Real-time search across 133 Ottawa.ca documents
- 🤖 AI-powered responses with source citations
- 📊 Confidence scoring for answer quality
- 🎯 Optimized for Ottawa residents and visitors

## How to Use
1. Ask questions about Ottawa city services
2. Get instant answers with official source citations
3. Explore different service categories using example buttons

## Example Questions
- "How do I apply for a marriage license?"
- "What are the parking rules downtown?"
- "What can I put in my green bin?"

Built with ❤️ using Gradio, SentenceTransformers, ChromaDB, and Groq API.
```

### Hardware Upgrade (Optional)

For better performance:
1. Go to Space **Settings**
2. Under **Hardware**, upgrade to:
   - **CPU Upgrade**: For faster processing
   - **Persistent Storage**: To save embeddings cache

### Environment Variables

You can add additional environment variables in Space settings:

```bash
# Optional configuration
ENABLE_ANALYTICS=true
MAX_CHUNKS=5
TEMPERATURE=0.1
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Space Build Fails
```bash
# Check requirements.txt has all dependencies
# Ensure file paths are correct in app.py
# Check Python version compatibility
```

#### 2. API Key Not Working
```bash
# Verify GROQ_API_KEY is set in Space secrets
# Check API key has sufficient credits
# Restart the Space after adding secrets
```

#### 3. Data Files Missing
```bash
# Upload processed data to data/processed/
# Or let app.py create demo data automatically
# Check file paths match your structure
```

#### 4. Import Errors
```bash
# Ensure all src/ files are uploaded
# Check file names match exactly
# Verify requirements.txt includes all dependencies
```

### Debug Mode

To enable debug mode, modify `app.py`:

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable Gradio debug
demo.launch(debug=True)
```

### Performance Optimization

For production Spaces:

1. **Use GPU**: Upgrade to GPU hardware for embeddings
2. **Cache Embeddings**: Store in persistent storage
3. **Optimize Chunks**: Reduce chunk size for faster retrieval
4. **Batch Processing**: Process multiple queries efficiently

## 📊 Monitoring

### Usage Analytics

Monitor your Space performance:
1. Check **Community** tab for user feedback
2. Monitor **Logs** for errors
3. Use built-in analytics in the chatbot admin panel

### Error Tracking

Common logs to monitor:
```bash
# API rate limits
"Rate limit exceeded"

# Memory issues  
"OutOfMemoryError"

# Model loading errors
"Error loading model"
```

## 🚀 Updates and Maintenance

### Updating Your Space

1. Make changes locally
2. Test with `deployment/local/run_local.py`
3. Upload updated files to Space
4. Monitor build logs

### Data Updates

To update Ottawa data:
1. Run scraper locally: `python src/scraper.py`
2. Process data: `python src/data_processor.py`
3. Upload new `ottawa_chunks.json` to Space

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/amin8448/ottawa-rag-chatbot/issues)
- **Email**: amin8448@gmail.com
- **Documentation**: Check `docs/` folder

---

**Your Space URL**: https://huggingface.co/spaces/aminnabavi/OttawaCityServicesChatbot

🎉 **Congratulations!** Your Ottawa RAG Chatbot is now live on HuggingFace Spaces!
