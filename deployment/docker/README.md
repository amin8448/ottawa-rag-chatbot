# 🐳 Docker Deployment Guide

Deploy your Ottawa RAG Chatbot using Docker for production-ready, scalable deployment.

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- Groq API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/amin8448/ottawa-rag-chatbot.git
cd ottawa-rag-chatbot

# Ensure .env file exists with your API key
echo "GROQ_API_KEY=your_actual_groq_api_key_here" > .env
```

### 2. Build and Run

```bash
# Build and start the application
docker-compose -f deployment/docker/docker-compose.yml up --build

# Or run in background
docker-compose -f deployment/docker/docker-compose.yml up -d --build
```

### 3. Access Your Chatbot

- **Main Interface**: http://localhost:7860
- **Health Check**: http://localhost:8080/health
- **Logs**: `docker-compose logs -f ottawa-chatbot`

## 🛠️ Deployment Options

### Production Deployment

```bash
# Production build with optimizations
docker-compose -f deployment/docker/docker-compose.yml up -d

# Check status
docker-compose -f deployment/docker/docker-compose.yml ps

# View logs
docker-compose -f deployment/docker/docker-compose.yml logs -f
```

### Development Deployment

```bash
# Development mode with live code reloading
docker-compose -f deployment/docker/docker-compose.yml --profile development up ottawa-chatbot-dev

# Access development instance
# Interface: http://localhost:7861
# Health: http://localhost:8081/health
```

### Custom Configuration

Create `docker-compose.override.yml`:

```yaml
version: '3.8'
services:
  ottawa-chatbot:
    environment:
      - MAX_CHUNKS=10
      - TEMPERATURE=0.2
    ports:
      - "8000:7860"  # Custom port
```

Then run:
```bash
docker-compose -f deployment/docker/docker-compose.yml -f docker-compose.override.yml up
```

## 📊 Monitoring and Management

### Health Checks

```bash
# Check application health
curl http://localhost:8080/health

# Container health status
docker-compose ps
```

### Resource Monitoring

```bash
# Monitor resource usage
docker stats ottawa-chatbot-app

# View detailed container info
docker inspect ottawa-chatbot-app
```

### Log Management

```bash
# View live logs
docker-compose logs -f ottawa-chatbot

# View last 100 lines
docker-compose logs --tail=100 ottawa-chatbot

# Export logs
docker-compose logs ottawa-chatbot > chatbot.log
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | Required | Your Groq API key |
| `ENABLE_ANALYTICS` | `true` | Enable usage analytics |
| `ENABLE_ADMIN` | `true` | Enable admin panel |
| `MAX_CHUNKS` | `5` | Max chunks for retrieval |
| `TEMPERATURE` | `0.1` | LLM temperature |
| `DEBUG` | `false` | Enable debug mode |

### Volume Mounts

```yaml
volumes:
  # Persistent data storage
  - chatbot_data:/app/data
  
  # Log persistence
  - chatbot_logs:/app/logs
  
  # Custom data mount (optional)
  - ./my_data:/app/data/processed:ro
```

### Port Configuration

```yaml
ports:
  - "7860:7860"  # Main Gradio interface
  - "8080:8080"  # Health check endpoint
  
  # Custom ports
  - "80:7860"    # HTTP
  - "443:7860"   # HTTPS (with reverse proxy)
```

## 🚀 Production Optimization

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      memory: 4G      # Increase for larger datasets
      cpus: '2.0'     # Increase for better performance
    reservations:
      memory: 2G
      cpus: '1.0'
```

### Performance Tuning

1. **GPU Support** (if available):
```dockerfile
# Add to Dockerfile
FROM nvidia/cuda:11.8-runtime-ubuntu20.04
# Install CUDA-enabled PyTorch
```

2. **Caching Layer**:
```yaml
# Uncomment Redis in docker-compose.yml
redis:
  image: redis:7-alpine
  # ... configuration
```

3. **Load Balancing**:
```yaml
# Multiple instances
ottawa-chatbot-1:
  extends: ottawa-chatbot
  ports:
    - "7861:7860"

ottawa-chatbot-2:
  extends: ottawa-chatbot
  ports:
    - "7862:7860"
```

### Reverse Proxy Setup

Create `nginx.conf`:

```nginx
upstream ottawa_backend {
    server ottawa-chatbot:7860;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://ottawa_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🔒 Security

### Security Best Practices

1. **Non-root User**: Container runs as `ottawa` user
2. **Read-only Filesystem**: Data volumes are properly isolated
3. **No New Privileges**: Security opt prevents privilege escalation
4. **Resource Limits**: Prevents resource exhaustion

### API Key Security

```bash
# Use Docker secrets (Docker Swarm)
echo "your_groq_api_key" | docker secret create groq_api_key -

# Reference in compose file
secrets:
  - groq_api_key
```

### Network Security

```yaml
networks:
  ottawa-network:
    driver: bridge
    internal: true  # Internal network only
```

## 🧪 Testing

### Container Testing

```bash
# Test container build
docker build -f deployment/docker/Dockerfile -t ottawa-test .

# Test run
docker run --rm -p 7860:7860 -e GROQ_API_KEY=test ottawa-test

# Integration testing
docker-compose -f deployment/docker/docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
```

### Load Testing

```bash
# Install artillery for load testing
npm install -g artillery

# Create test config
artillery quick --count 10 --num 5 http://localhost:7860
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f deployment/docker/docker-compose.yml up --build -d

# Clean up old images
docker image prune -f
```

### Database Updates

```bash
# Update data files
docker-compose exec ottawa-chatbot python src/scraper.py
docker-compose exec ottawa-chatbot python src/data_processor.py

# Restart to reload data
docker-compose restart ottawa-chatbot
```

### Backup and Restore

```bash
# Backup data volume
docker run --rm -v chatbot_data:/data -v $(pwd):/backup alpine tar czf /backup/chatbot_backup.tar.gz -C /data .

# Restore data volume
docker run --rm -v chatbot_data:/data -v $(pwd):/backup alpine tar xzf /backup/chatbot_backup.tar.gz -C /data
```

## 🐛 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs ottawa-chatbot

# Check container status
docker-compose ps

# Inspect container
docker inspect ottawa-chatbot-app
```

#### Out of Memory
```bash
# Increase memory limits
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

#### Port Conflicts
```bash
# Change ports in docker-compose.yml
ports:
  - "8000:7860"  # Use different external port
```

#### API Key Issues
```bash
# Verify API key is set
docker-compose exec ottawa-chatbot env | grep GROQ

# Update API key
docker-compose down
echo "GROQ_API_KEY=new_key" > .env
docker-compose up -d
```

### Debug Mode

```bash
# Run with debug enabled
docker-compose -f deployment/docker/docker-compose.yml run --rm ottawa-chatbot python app.py --debug

# Interactive shell
docker-compose exec ottawa-chatbot bash
```

## 📞 Support

- **GitHub Issues**: [Report problems](https://github.com/amin8448/ottawa-rag-chatbot/issues)
- **Email**: amin8448@gmail.com
- **Documentation**: Check `docs/` folder for detailed guides

---

## 🎉 Success!

Your Ottawa RAG Chatbot is now running in Docker! 

- **Production**: http://localhost:7860
- **Health**: http://localhost:8080/health
- **Logs**: `docker-compose logs -f`

For production deployment, consider:
- Setting up SSL/TLS with Let's Encrypt
- Using a reverse proxy (Nginx/Traefik)
- Monitoring with Prometheus/Grafana
- Auto-scaling with Docker Swarm/Kubernetes