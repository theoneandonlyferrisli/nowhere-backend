# Nowhere Link Server

**Production link server for Nowhere app** - Handles Universal Links (iOS deep linking), landing page, and user profile pages across dual domains.

## What This Is

A FastAPI-based link server running on GKE that provides:
- **Landing Page** (`nowhereapp.ai`) - Beautiful carousel showcasing cities from Firebase Storage
- **Universal Links** - Seamless iOS app deep linking via AASA (Apple App Site Association)
- **User Profiles** (`links.nowhereapp.ai/profile/{id}`) - Shareable profile pages with liquid glass UI
- **Smart Redirects** - Domain-based routing (links.nowhereapp.ai → nowhereapp.ai for root access)

## Project Structure

```
nowhere-backend/
├── infra/terraform/     # Infrastructure as Code (GCP resources)
│   └── README.md        # Terraform setup and operations
├── app/                 # FastAPI application
│   ├── main.py          # Application endpoints
│   ├── Dockerfile       # Container image definition
│   ├── static/          # Static assets (OG images, etc.)
│   └── README.md        # App details and local development
├── k8s/                 # Kubernetes manifests
│   ├── deployment.yaml  # Application deployment
│   ├── service.yaml     # Service configuration
│   ├── ingress.yaml     # Load balancer & routing
│   ├── managed-cert.yaml # TLS certificate
│   └── README.md        # Deployment and operations
└── README.md            # This file
```

## Quick Start

### Initial Setup

1. **Provision Infrastructure**
   ```bash
   cd infra/terraform
   terraform init
   terraform apply
   ```
   See [infra/terraform/README.md](infra/terraform/README.md) for details.

2. **Update DNS** - Point `nowhereapp.ai` nameservers to Cloud DNS (from Terraform output)

3. **Build & Push Image** (using Cloud Build, no local Docker needed)
   ```bash
   cd app
   gcloud builds submit \
     --tag us-central1-docker.pkg.dev/nowhere-link-prod/nowhere-link-repo/link-server:2025.11.1
     --project=nowhere-link-prod
   ```

4. **Deploy to Kubernetes**
   ```bash
   cd k8s
   kubectl apply -f .
   ```

## Common Workflows

### Update Business Logic

1. **Edit Code**
   ```bash
   # Modify app/main.py with your changes
   ```

2. **Build New Image** (increment version: 2025.11.2, 2025.11.3, etc.)
   ```bash
   cd app
   gcloud builds submit \
     --tag us-central1-docker.pkg.dev/nowhere-link-prod/nowhere-link-repo/link-server:2025.11.2
   ```

3. **Update Deployment**
   ```bash
   cd ../k8s
   # Edit deployment.yaml to use new version tag
   kubectl apply -f deployment.yaml
   ```

4. **Verify Deployment**
   ```bash
   kubectl rollout status deployment/link-server
   kubectl get pods
   ```

### Versioning Format

Use `YYYY.MM.N` format (e.g., 2025.11.1, 2025.11.2):
- First number: Year (2025)
- Second number: Month (11 = November)
- Third number: Incremental version within that month (1, 2, 3...)

Old versions are automatically cleaned up after 90 days (minimum 5 versions kept).

### Update Infrastructure

```bash
cd infra/terraform
# Edit .tf files as needed
terraform plan      # Preview changes
terraform apply     # Apply changes
```

See [infra/terraform/README.md](infra/terraform/README.md) for infrastructure operations.

### Update Kubernetes Configuration

```bash
cd k8s
# Edit manifest files (deployment.yaml, ingress.yaml, etc.)
kubectl apply -f <modified-file>.yaml
```

See [k8s/README.md](k8s/README.md) for deployment operations and troubleshooting.

## Deployment Status

Check current status:

```bash
# Pods
kubectl get pods

# Ingress & IP
kubectl get ingress

# TLS Certificate
kubectl get managedcertificate

# View logs
kubectl logs -l app=link-server --tail=50
```

## Testing

```bash
# Landing page
curl https://links.nowhereapp.ai/

# AASA for Universal Links
curl https://links.nowhereapp.ai/.well-known/apple-app-site-association

# User profile (requires Firestore data)
curl https://links.nowhereapp.ai/u/{user_id}
```

## Tech Stack

- **Infrastructure**: GCP (GKE Autopilot, Cloud DNS, Cloud Load Balancing)
- **IaC**: Terraform
- **Application**: FastAPI (Python)
- **Container Registry**: GCP Artifact Registry
- **Database**: Firestore (user data)
- **CI/CD**: Cloud Build
- **TLS**: Google-managed certificates

## Documentation

- **[infra/terraform/README.md](infra/terraform/README.md)** - Infrastructure setup, Terraform operations
- **[app/README.md](app/README.md)** - Application details, building images, local development
- **[k8s/README.md](k8s/README.md)** - Kubernetes deployment, updates, troubleshooting

## Project Details

- **GCP Project**: `nowhere-link-prod`
- **Domain**: `nowhereapp.ai` (managed via Cloud DNS)
- **Link Server**: `links.nowhereapp.ai`
- **Cluster**: `nowhere-link-autopilot` (us-central1)
- **Image Registry**: `us-central1-docker.pkg.dev/nowhere-link-prod/nowhere-link-repo`
