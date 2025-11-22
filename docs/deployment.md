# Cloud Deployment Guide

This document describes how to deploy the AI-Friendly Repo Template to cloud infrastructure using the AI-Friendly Cloud Infrastructure Platform architecture.

## Overview

The `cloud-main` branch is specifically configured for cloud deployment with production-ready adapters and containerization. This branch follows the AI-Friendly Cloud Infrastructure Federation model where apps are orchestrated through a central infrastructure repository.

## Branch Strategy

### `main` Branch (Local Development)
- Optimized for speed and local development
- Uses SQLite for database
- Uses local filesystem for storage
- Mocked authentication
- Goal: "Works on my machine"

### `cloud-main` Branch (Production)
- Optimized for cloud platform integration
- **Adapters Swapped:** SQLite → Postgres, Filesystem → S3
- **Contract Enforced:** Contains valid `deployment/service.json`
- **Status:** Always deployable
- **Compliance:** Passes all AI-Friendly Cloud Infrastructure validation rules

## Architecture

### Components

#### Backend (Python/FastAPI)
- **Runtime:** Python 3.11
- **Framework:** FastAPI
- **Port:** 8000
- **Path:** `repo_src/backend`
- **Entry:** `main.py`

#### Frontend (React/TypeScript)
- **Runtime:** Node.js 20
- **Framework:** React + Vite
- **Port:** 3000 (build served via backend in production)
- **Path:** `repo_src/frontend`

### Cloud Adapters

The application uses adapter pattern to swap implementations between local and cloud:

| Component | Local | Cloud | Adapter Path |
|-----------|-------|-------|--------------|
| Database | SQLite | PostgreSQL | `repo_src/backend/adapters/database.py` |
| Storage | Filesystem | S3 | `repo_src/backend/adapters/storage.py` |

## Required Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection string (format: `postgresql://user:pass@host:port/db`)
- `API_PORT` - Backend API port (default: 8000)
- `FRONTEND_URL` - URL where frontend is hosted (for CORS configuration)

### Optional
- `REDIS_URL` - Redis connection string (if caching enabled)
- `S3_BUCKET_NAME` - AWS S3 bucket for file storage
- `LOG_LEVEL` - Logging verbosity (debug, info, warning, error)
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins

### Secrets (Injected by Platform)
- `DATABASE_PASSWORD` - PostgreSQL password
- `API_SECRET_KEY` - Secret key for JWT/session management
- `AWS_ACCESS_KEY_ID` - AWS credentials for S3 access
- `AWS_SECRET_ACCESS_KEY` - AWS secret access key

## Deployment Contract

The `deployment/service.json` file defines the service contract for the platform. Key sections:

### Resource Requirements
```json
{
  "cpu": "0.5",
  "memory": "1024",
  "storage": "10GB",
  "min_instances": 1,
  "max_instances": 5
}
```

### Dependencies
- **PostgreSQL:** Required for data persistence
- **S3:** Required for file storage
- **Redis:** Optional (for future caching layer)

### Health Checks
- **Backend:** `GET /health` - Checks database connectivity and service status
- **Frontend:** `GET /` - Ensures frontend is serving correctly

## Container Build

### Build Command
```bash
docker build -t ai-friendly-repo-template:latest .
```

### Multi-Stage Build Process
1. **Frontend Builder:** Builds React app with Vite
2. **Backend Builder:** Installs Python dependencies
3. **Production Runtime:** Combines built artifacts, runs as non-root user

### Security Features
- Non-root user execution (uid: 1000)
- No embedded secrets
- Minimal attack surface (slim base image)
- Health check endpoint

## Platform Integration Workflow

### 1. Development Flow
```bash
# Work on main branch locally
git checkout main
# ... make changes ...
git commit -m "Add new feature"

# Merge to cloud-main
git checkout cloud-main
git merge main

# Resolve any cloud-specific adapter changes
# ... update adapters if needed ...
git commit -m "Merge main: Add new feature (cloud adapters updated)"
```

### 2. Update Platform Repository
```bash
# In the platform repo (ai-friendly-cloud-infra)
cd apps/ai-friendly-repo-template
git pull origin cloud-main

# Commit the new submodule hash
cd ../..
git add apps/ai-friendly-repo-template
git commit -m "Update ai-friendly-repo-template to latest"
```

### 3. Platform CI/CD Validation

The platform runs these checks before deployment:

#### ✅ Rule 1: Contract Exists
- File `deployment/service.json` must exist
- Must pass JSON Schema validation

#### ✅ Rule 2: Container Readiness
- `Dockerfile` must exist in root
- Must successfully build via `docker build .`
- Must NOT embed `.env` files

#### ✅ Rule 3: Cloud Context Test
- Cloud adapter tests must pass
- Example: `pytest repo_src/backend/tests/test_cloud_adapters.py`

#### ✅ Rule 4: Documentation Exposure
- `docs/deployment.md` must exist
- `registry/context.json` must be present

## Infrastructure Provisioning

When deployed through the AI-Friendly Cloud Infrastructure Platform, the following infrastructure is automatically provisioned:

### Compute
- ECS Task Definition with resource limits
- Auto-scaling group (1-5 instances)
- Load balancer with health checks

### Database
- RDS PostgreSQL instance
- Automated backups
- Multi-AZ deployment (production)

### Storage
- S3 bucket with versioning
- IAM role with minimal permissions
- Lifecycle policies for cost optimization

### Networking
- VPC with public/private subnets
- Security groups (restrictive by default)
- CloudWatch logs and metrics

## Monitoring and Observability

### Metrics
- Request rate and latency (p50, p95, p99)
- Error rate and types
- Resource utilization (CPU, memory)
- Database connection pool metrics

### Logging
- Structured JSON logs
- 30-day retention
- Searchable via CloudWatch Logs Insights

### Alerts
- **High Error Rate:** Triggers when error rate > 5%
- **High Latency:** Triggers when p95 latency > 1000ms

## Deployment Strategy

### Rolling Deployment
- Deploy new version to single instance
- Health check must pass
- Gradually roll out to remaining instances
- Automatic rollback on failure

### Pre-Deploy Commands
```bash
pnpm install
pnpm build
```

### Post-Deploy Commands
```bash
python repo_src/backend/database/migrations/run.py
```

## Troubleshooting

### Container Won't Start
1. Check environment variables are set: `docker logs <container-id>`
2. Verify database connectivity: `DATABASE_URL` format
3. Check health endpoint: `curl http://localhost:8000/health`

### Database Connection Issues
1. Verify PostgreSQL is accessible from container
2. Check security group rules
3. Validate `DATABASE_URL` format and credentials

### Build Failures
1. Ensure all dependencies are in `requirements.txt` and `package.json`
2. Check for missing system dependencies in Dockerfile
3. Verify multi-stage build copies all necessary files

## Migration from Local to Cloud

### Database Migration
```bash
# Export local SQLite data
python repo_src/scripts/export_sqlite.py > data_export.sql

# Import to PostgreSQL
psql $DATABASE_URL -f data_export.sql
```

### File Storage Migration
```bash
# Sync local files to S3
aws s3 sync ./local_storage/ s3://$S3_BUCKET_NAME/
```

## Compliance Checklist

Before merging to `cloud-main`:

- [ ] All tests pass (including cloud adapter tests)
- [ ] `deployment/service.json` is valid
- [ ] `Dockerfile` builds successfully
- [ ] No secrets embedded in code or `.env` files
- [ ] Documentation updated
- [ ] Health check endpoint implemented
- [ ] Database migrations tested

## Support

For platform-related issues:
- Team: Platform Engineering
- Contact: platform@example.com
- Documentation: [Platform Wiki](https://internal-wiki/ai-friendly-cloud-infra)

For application-specific issues:
- Repository: https://github.com/Sivolc2/ai-friendly-repo-template
- Issues: https://github.com/Sivolc2/ai-friendly-repo-template/issues
