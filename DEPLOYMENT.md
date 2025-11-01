# RIK Deployment Guide

Complete guide for deploying RIK in different environments.

---

## 🚀 Quick Start (Docker - Recommended)

The fastest way to run RIK:

```bash
# 1. Build and start
docker-compose up -d

# 2. Check health
curl http://localhost:8000/health/live

# 3. View logs
docker-compose logs -f rik-api

# 4. Stop
docker-compose down
```

**That's it!** RIK is now running at `http://localhost:8000`

---

## 📦 Deployment Options

### Option 1: Docker Compose (Easiest)
**Best for:** Development, testing, quick deployments

```bash
# Development
docker-compose up

# Production (with proper config)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Option 2: Docker Only
**Best for:** Cloud deployments (AWS ECS, Google Cloud Run)

```bash
# Build image
docker build -t rik-api:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e RIK_ENV=production \
  -e RIK_API_KEY_ENABLED=true \
  -e RIK_API_KEYS=your-key-here \
  --name rik-api \
  rik-api:latest
```

### Option 3: Direct Python
**Best for:** Development, debugging

```bash
# Install dependencies
pip install -r requirements.txt -r requirements-demo.txt

# Set environment
cp config/development.env .env

# Run
python3 rik_api.py
```

### Option 4: Production Server (uvicorn)
**Best for:** Production VPS deployments

```bash
# Install
pip install uvicorn gunicorn

# Run with multiple workers
uvicorn rik_api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --no-access-log
```

---

## 🔧 Configuration

### Environment Variables

All configuration via environment variables or `.env` file.

**Minimal Production Config:**
```bash
RIK_ENV=production
RIK_API_KEY_ENABLED=true
RIK_API_KEYS=your-secure-key-here
RIK_DATABASE_URL=postgresql://user:pass@host:5432/rik
RIK_CORS_ORIGINS=https://yourdomain.com
RIK_LOG_FILE_ENABLED=true
```

**Generate Secure API Key:**
```bash
openssl rand -hex 32
```

### Templates

Use provided templates:
- `config/development.env` - Dev settings
- `config/staging.env` - Staging settings
- `config/production.env` - Production settings + checklist

```bash
# Copy template
cp config/production.env .env

# Edit with your values
nano .env
```

---

## 🐳 Docker Deployment Details

### Build Custom Image

```bash
# Build
docker build -t rik-api:v5.4.0 .

# Tag for registry
docker tag rik-api:v5.4.0 your-registry/rik-api:v5.4.0

# Push
docker push your-registry/rik-api:v5.4.0
```

### Environment Variables in Docker

**Option 1: docker-compose.yml**
```yaml
services:
  rik-api:
    environment:
      - RIK_ENV=production
      - RIK_API_KEYS=key1,key2
```

**Option 2: .env file**
```bash
# Create .env file
cp config/production.env .env

# docker-compose automatically loads .env
docker-compose up
```

**Option 3: docker run**
```bash
docker run \
  -e RIK_ENV=production \
  -e RIK_API_KEYS=your-key \
  rik-api:latest
```

### Volume Mounts

**Persist data:**
```yaml
volumes:
  - ./data:/app/data        # Database files
  - ./logs:/app/logs        # Log files
```

**Development (hot reload):**
```yaml
volumes:
  - ./:/app                 # Mount source code
```

### Health Checks

Docker uses `/health/live` endpoint:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
  interval: 30s
  timeout: 3s
  retries: 3
```

---

## ☸️ Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rik-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rik-api
  template:
    metadata:
      labels:
        app: rik-api
    spec:
      containers:
      - name: rik-api
        image: your-registry/rik-api:v5.4.0
        ports:
        - containerPort: 8000
        env:
        - name: RIK_ENV
          value: "production"
        - name: RIK_API_KEYS
          valueFrom:
            secretKeyRef:
              name: rik-secrets
              key: api-keys
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: rik-api-service
spec:
  selector:
    app: rik-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Secrets

```bash
# Create secret
kubectl create secret generic rik-secrets \
  --from-literal=api-keys=key1,key2,key3

# Verify
kubectl describe secret rik-secrets
```

---

## 🌩️ Cloud Platform Deployments

### AWS ECS

```bash
# 1. Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag rik-api:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/rik-api:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/rik-api:latest

# 2. Create task definition (use AWS Console or CLI)
# 3. Create ECS service

# Health check endpoint: /health/live
```

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy rik-api \
  --image gcr.io/YOUR_PROJECT/rik-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars RIK_ENV=production,RIK_API_KEY_ENABLED=true \
  --set-secrets RIK_API_KEYS=rik-api-keys:latest
```

### Azure Container Instances

```bash
az container create \
  --resource-group rik-rg \
  --name rik-api \
  --image your-registry.azurecr.io/rik-api:latest \
  --dns-name-label rik-api \
  --ports 8000 \
  --environment-variables \
    RIK_ENV=production \
    RIK_API_KEY_ENABLED=true
```

---

## 🔒 Production Checklist

Before deploying to production:

### Security
- [ ] `RIK_API_KEY_ENABLED=true`
- [ ] Strong API keys generated (32+ chars)
- [ ] `RIK_CORS_ORIGINS` restricted to your domains
- [ ] No secrets in code or Docker images
- [ ] Secrets managed via environment variables or secrets manager
- [ ] SSL/TLS termination configured (nginx, load balancer)
- [ ] Firewall rules configured

### Database
- [ ] Using PostgreSQL (not SQLite!)
- [ ] Database backups configured
- [ ] Connection pooling enabled
- [ ] Database credentials secured

### Monitoring
- [ ] Health endpoints monitored
- [ ] Logs forwarded to aggregator (Splunk, DataDog, CloudWatch)
- [ ] Alerts configured (health check failures, error rates)
- [ ] Performance metrics tracked

### Configuration
- [ ] `RIK_ENV=production`
- [ ] `RIK_DEBUG=false`
- [ ] `RIK_LOG_LEVEL=INFO` or `WARNING`
- [ ] `RIK_LOG_FILE_ENABLED=true`
- [ ] Business rules configured (thresholds, trusted vendors)
- [ ] Rate limiting enabled

### Performance
- [ ] Multiple workers configured (`RIK_API_WORKERS=4`)
- [ ] Load tested with expected traffic
- [ ] Resource limits set (CPU, memory)
- [ ] Horizontal scaling configured

---

## 📊 Monitoring

### Health Endpoints

```bash
# Liveness (is service alive?)
curl http://localhost:8000/health/live

# Readiness (can service handle requests?)
curl http://localhost:8000/health/ready

# Version info
curl http://localhost:8000/version
```

### Metrics

Parse structured JSON logs for metrics:

```bash
# Average response time
jq -s 'map(.duration_seconds) | add/length' < logs/rik.log

# P95 latency
jq -s 'map(.duration_seconds) | sort | .[length*0.95|floor]' < logs/rik.log

# Error rate
jq 'select(.level == "ERROR")' < logs/rik.log | wc -l
```

### Log Aggregation

Forward logs to:
- **Splunk:** Use Splunk Universal Forwarder
- **DataDog:** Use DataDog Agent
- **CloudWatch:** Use CloudWatch Agent
- **ELK Stack:** Use Filebeat

---

## 🧪 Testing Deployment

```bash
# 1. Health check
curl http://localhost:8000/health/ready

# 2. Test invoice processing
curl -X POST http://localhost:8000/process_invoice \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d '{
    "pdf_content": "{\"invoice_number\": \"TEST-001\", \"vendor_name\": \"Acme Corporation\", \"amount\": 1000, \"po_number\": \"PO-123\"}",
    "invoice_id": "TEST-001"
  }'

# 3. Check stats
curl http://localhost:8000/invoice_stats

# 4. View API docs
open http://localhost:8000/docs
```

---

## 🔧 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs rik-api

# Common issues:
# - Port 8000 already in use
# - Invalid environment variables
# - Database connection failed
```

### Health check failing

```bash
# Check API is responding
curl http://localhost:8000/health/live

# Check database connection
curl http://localhost:8000/health/ready

# View detailed logs
docker-compose logs -f rik-api | grep ERROR
```

### High memory usage

```bash
# Check current memory
docker stats rik-api

# Restart with memory limit
docker run --memory="512m" rik-api:latest
```

### Slow performance

```bash
# Run benchmarks
python3 benchmarks/performance_test.py

# Increase workers
docker-compose up -d --scale rik-api=3

# Or set RIK_API_WORKERS=4 in environment
```

---

## 📚 Additional Resources

- **Configuration:** See `PRODUCTION_FEATURES.md`
- **API Documentation:** http://localhost:8000/docs
- **Environment Templates:** `config/*.env` files
- **Performance Benchmarks:** `benchmarks/performance_test.py`

---

## 🆘 Support

Issues? Check:
1. Logs: `docker-compose logs -f`
2. Health: `curl http://localhost:8000/health/ready`
3. Config: `python3 config.py`
4. Environment: Verify `.env` file settings

---

**RIK v5.4.0** - Production-Ready Deployment 🚀
