# AI Service Proxy

High-performance reverse proxy for ai.megallm.io built with FastAPI and async HTTPX. Production-ready with comprehensive middleware, logging, and error handling.

## Features

- Async FastAPI with HTTP/2 support via HTTPX
- Streaming responses for large payloads
- Request/response logging middleware
- Global error handling with custom exceptions
- Configurable via environment variables or .env file
- CORS support with fine-grained control
- Health check and monitoring endpoints
- Colored console logging for development
- Production-ready with Uvicorn workers
- Security hardened Docker container
- Comprehensive test suite

## Quick Start

### Local Development

```bash
python3 -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Access:
- Proxy: http://localhost:8080
- Health: http://localhost:8080/api/health
- Docs: http://localhost:8080/api/docs

### Docker

```bash
docker-compose up -d
curl http://localhost:8080/api/health
```

### Run Tests

```bash
pytest -v
```

## Deployment

### Railway

```bash
railway login
railway init
railway up
```

Set in Railway dashboard:
- `TARGET_URL=https://ai.megallm.io`
- `PORT=8080` (auto-set)

### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-proxy
gcloud run deploy ai-proxy \
  --image gcr.io/PROJECT_ID/ai-proxy \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars TARGET_URL=https://ai.megallm.io
```

### AWS ECS/Fargate

```bash
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ECR_URL
docker build -t ai-proxy .
docker tag ai-proxy:latest ECR_URL/ai-proxy:latest
docker push ECR_URL/ai-proxy:latest
```

### DigitalOcean App Platform

1. Connect GitHub repository
2. Select Dockerfile build method
3. Set `TARGET_URL=https://ai.megallm.io`
4. Deploy

### Heroku

```bash
heroku login
heroku create app-name
heroku stack:set container
git push heroku main
heroku config:set TARGET_URL=https://ai.megallm.io
```

### VPS (Ubuntu/Debian)

```bash
curl -fsSL https://get.docker.com | sh
git clone YOUR_REPO
cd Proxy
docker-compose up -d
```

Optional nginx reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGET_URL` | `https://ai.megallm.io` | Target server URL |
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8080` | Bind port |
| `REQUEST_TIMEOUT` | `300` | Request timeout (seconds) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_WORKERS` | `4` | Uvicorn workers |
| `ENABLE_CORS` | `true` | Enable CORS |
| `CORS_ORIGINS` | `["*"]` | Allowed origins |
| `CORS_METHODS` | `["*"]` | Allowed methods |
| `CORS_HEADERS` | `["*"]` | Allowed headers |
| `PROXY_BUFFER_SIZE` | `8192` | Streaming buffer size |
| `MAX_RETRIES` | `3` | Connection retries |
| `RETRY_BACKOFF_FACTOR` | `0.5` | Retry backoff multiplier |
| `SSL_VERIFY` | `true` | Verify SSL certificates |

### Example .env

```bash
TARGET_URL=https://ai.megallm.io
PORT=8080
HOST=0.0.0.0
REQUEST_TIMEOUT=300
LOG_LEVEL=INFO
ENABLE_CORS=true
SSL_VERIFY=true
```

## Usage

Replace `ai.megallm.io` with your proxy URL:

Before:
```
https://ai.megallm.io/api/chat
```

After:
```
https://your-proxy.railway.app/api/chat
```

All HTTP methods, headers, query params, and request bodies are proxied transparently.

## API Endpoints

### Proxy Endpoints

- `GET/POST/PUT/DELETE/PATCH/OPTIONS/HEAD /{path:path}` - Proxy all requests

### Health & Monitoring

- `GET /api/health` - Health check with target info
- `GET /api/ping` - Simple ping/pong
- `GET /api/docs` - Swagger UI documentation
- `GET /api/redoc` - ReDoc documentation

### Health Response

```json
{
  "status": "healthy",
  "target_url": "https://ai.megallm.io",
  "timeout": 300,
  "ssl_verify": true
}
```

## Monitoring

### Request Logging

Every request logs:
- Method and path
- Client IP
- Request ID
- Processing time
- Response status

Example:
```
2025-11-21 10:30:45 - ai_proxy - INFO - Request started: POST /api/chat [Client: 192.168.1.1] [ID: 1700567445000]
2025-11-21 10:30:46 - ai_proxy - INFO - Response 200 from https://ai.megallm.io/api/chat
2025-11-21 10:30:46 - ai_proxy - INFO - Request completed: POST /api/chat [Status: 200] [Time: 0.823s] [ID: 1700567445000]
```

### Response Headers

Every response includes:
- `X-Process-Time` - Processing duration
- `X-Request-ID` - Unique request identifier
- `X-Proxy-By` - Proxy identifier

### Docker Health Checks

Automatic health checks every 30 seconds:
```bash
docker ps
docker inspect ai-proxy
```

## Performance

### Scaling

Horizontal scaling (stateless):
```bash
docker-compose up --scale proxy=3
```

Vertical scaling (adjust workers):
```bash
uvicorn app.main:app --workers 8
```

Worker formula: `(2 × CPU cores) + 1`

### Optimizations

- HTTP/2 support for multiplexing
- Connection pooling (max 100 connections)
- Keep-alive connections (max 20)
- Streaming responses (8KB chunks)
- Async I/O throughout

### Resource Limits

Docker Compose includes:
- CPU limit: 2 cores
- Memory limit: 1GB
- Reservations: 0.5 CPU, 256MB

## Security

- Non-root user in container (UID 1000)
- Minimal Docker image (Python 3.11 slim)
- Excluded sensitive headers from proxying
- Configurable SSL verification
- Request timeout protection
- Connection limits
- CORS configuration

## Troubleshooting

### Check Logs

```bash
docker logs ai-proxy
railway logs
heroku logs --tail
```

### Test Connectivity

```bash
curl -v https://ai.megallm.io
curl http://localhost:8080/api/health
```

### Common Issues

**502 Bad Gateway**: Target server unreachable
- Check TARGET_URL is correct
- Verify target server is online
- Check firewall rules

**504 Gateway Timeout**: Request took too long
- Increase REQUEST_TIMEOUT
- Check target server performance

**High Memory**: Too many workers
- Reduce MAX_WORKERS
- Set Docker memory limits

**Port in Use**: Port already bound
- Change PORT environment variable
- Kill existing process on port

### Testing

```bash
pytest
pytest --cov=app
pytest -v -s
```

### Local Development with Hot Reload

```bash
uvicorn app.main:app --reload --log-level debug
```

## License

MIT License