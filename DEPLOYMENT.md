# Deployment Guide

Comprehensive guide for deploying Enterprise Knowledge Assistant to production.

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / Ingress                   │
└─────────────────────────────────────────────────────────────┘
         ↓                                    ↓
    ┌─────────────┐                   ┌──────────────┐
    │  Frontend   │                   │   Backend    │
    │ (Streamlit) │                   │  (FastAPI)   │
    └─────────────┘                   └──────────────┘
                                            ↓
                                    ┌───────────────┐
                                    │  PostgreSQL   │
                                    │  + pgvector   │
                                    └───────────────┘
```

## Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] OpenAI API key secured
- [ ] Database backup strategy in place
- [ ] SSL/TLS certificates ready
- [ ] Monitoring and logging configured
- [ ] Health checks implemented
- [ ] Rate limiting configured
- [ ] Backup and disaster recovery plan

## Option 1: Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Container registry access
- Persistent volume provisioner

### Step 1: Build and Push Image

```bash
# Build image
docker build -f docker/Dockerfile -t myregistry/eka:1.0.0 .

# Push to registry
docker push myregistry/eka:1.0.0
```

### Step 2: Create Namespace

```bash
kubectl create namespace eka
```

### Step 3: Create Secrets

```bash
# OpenAI API key
kubectl create secret generic eka-secrets \
  --from-literal=OPENAI_API_KEY=sk-... \
  --from-literal=DB_PASSWORD=secure_password \
  -n eka

# TLS certificates (optional)
kubectl create secret tls eka-tls \
  --cert=path/to/cert.crt \
  --key=path/to/key.key \
  -n eka
```

### Step 4: Create ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

### Step 5: Deploy Database (PostgreSQL + pgvector)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: eka
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: eka
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: ankane/pgvector:latest
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: eka_db
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: eka-secrets
              key: DB_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
```

### Step 6: Deploy Applications

```bash
# Update image in deployment.yaml
sed -i 's|eka:latest|myregistry/eka:1.0.0|g' k8s/deployment.yaml

# Apply deployment
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check rollout
kubectl rollout status deployment/eka-backend -n eka
```

### Step 7: Verify Deployment

```bash
# Check pods
kubectl get pods -n eka

# Check services
kubectl get svc -n eka

# Port forward for testing
kubectl port-forward svc/eka-backend 8000:8000 -n eka
```

### Step 8: Setup Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: eka-ingress
  namespace: eka
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - eka.example.com
    secretName: eka-tls
  rules:
  - host: eka.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: eka-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: eka-frontend
            port:
              number: 8501
```

## Option 2: Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml eka

# Check services
docker service ls

# Scale backend
docker service scale eka_backend=3
```

## Option 3: EC2/VM Deployment

### Setup

```bash
# SSH into instance
ssh -i key.pem ubuntu@instance-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone <repo-url>
cd Enterprise-Knowledge-Assistant

# Setup environment
cp .env.example .env
# Edit .env with production values
nano .env

# Start services
docker-compose -f docker-compose.yml up -d
```

### Add Nginx Reverse Proxy

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:8501;
}

server {
    listen 80;
    server_name eka.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name eka.example.com;

    ssl_certificate /etc/letsencrypt/live/eka.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/eka.example.com/privkey.pem;

    # API routes
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # Streamlit
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

## Monitoring and Logging

### Application Logs

```bash
# View logs
docker-compose logs -f backend

# Save logs
docker-compose logs backend > logs.txt

# Log aggregation (ELK Stack)
docker-compose up -d elasticsearch logstash kibana
```

### Health Monitoring

```bash
# Health check endpoint
curl http://localhost:8000/api/v1/health

# Database health
curl http://localhost:8000/api/v1/health | jq .database
```

### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## Database Backup Strategy

### Regular Backups

```bash
# Backup PostgreSQL
docker exec eka_postgres pg_dump -U postgres eka_db > backup.sql

# Restore from backup
docker exec -i eka_postgres psql -U postgres eka_db < backup.sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec eka_postgres pg_dump -U postgres eka_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
```

## Performance Optimization

### Database
- Add indexes on frequently searched columns
- Use pgvector IVFFLAT indexing
- Regular VACUUM and ANALYZE

### Application
- Enable query caching
- Use connection pooling
- Load balancing across instances
- CDN for static files

### Infrastructure
- Auto-scaling for load spikes
- Resource limits and quotas
- Network optimization
- Storage optimization

## Security Hardening

### Network Security
```bash
# Firewall rules
ufw allow 443/tcp
ufw allow 80/tcp
ufw deny 5432/tcp  # PostgreSQL internal only
```

### Application Security
- Use environment variables for secrets
- Enable SSL/TLS
- Implement rate limiting
- Regular security updates
- Input validation

### Database Security
- Use strong passwords
- Enable SSL for connections
- Regular backups
- Access control

## Scaling Strategy

### Horizontal Scaling

```yaml
# Multiple backend replicas
replicas: 3

# Load balancer configuration
apiVersion: v1
kind: Service
metadata:
  name: eka-backend
spec:
  type: LoadBalancer
  sessionAffinity: ClientIP
  selector:
    app: eka-backend
```

### Auto-Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: eka-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: eka-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Disaster Recovery

### Backup Strategy
- Daily backups to S3
- Monthly full backups
- Test restore procedures
- Document recovery steps

### High Availability
- Multi-zone deployment
- Database replication
- Load balancing
- Health checks and failover

## Troubleshooting

### High Memory Usage
```bash
# Check memory
docker stats

# Reduce connection pool
CONNECTION_POOL_SIZE=5
```

### Slow Queries
```bash
# Enable query logging
SQLALCHEMY_ECHO=True

# Add indexes
CREATE INDEX ON document_chunks USING ivfflat (embedding);
```

### API Timeouts
```bash
# Increase timeout
TIMEOUT=60

# Optimize GPT calls
MAX_TOKENS=500
```

## Maintenance

### Regular Tasks
- [ ] Monitor logs daily
- [ ] Review performance metrics
- [ ] Test backups weekly
- [ ] Security patches monthly
- [ ] Full disaster recovery test quarterly

### Upgrade Procedure
```bash
# Pull latest
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Test locally
pytest

# Deploy with blue-green deployment
kubectl set image deployment/eka-backend \
  backend=myregistry/eka:new-version
```

---

**Deployment Status: Production Ready ✅**
