# Link Server Application

FastAPI application serving the Nowhere link server with Universal Links support, Open Graph previews, and a landing page.

## What It Does

The link server provides:

1. **Landing Page** (`/`) - Marketing page with Open Graph metadata
2. **Apple App Site Association** (`/.well-known/apple-app-site-association`) - Universal Links configuration for iOS deep linking
3. **User Passport Pages** (`/u/{user_id}`) - Dynamic user profile pages with:
   - Open Graph meta tags for rich link previews (iMessage, Twitter, Instagram, etc.)
   - Twitter Card metadata
   - App Links metadata for iOS Universal Links
   - Fetches user data from Firestore (`users/{user_id}` collection)

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Google Cloud Firestore** - User data storage
- **Workload Identity** - Authenticates to Firestore via GKE service account

## Files

- `main.py` - FastAPI application with all endpoints
- `Dockerfile` - Container image definition
- `static/og-default.png` - Placeholder Open Graph image (replace with actual image)

## Local Development

```bash
# Install dependencies
pip install fastapi uvicorn[standard] google-cloud-firestore

# Run locally (requires Firestore credentials)
uvicorn main:app --reload --port 8080
```

## Building & Deploying

### Build and Push Image (Cloud Build - Recommended)

```bash
cd app

# Build using Cloud Build (no local Docker needed)
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/nowhere-link-prod/nowhere-link-repo/link-server:v1 \
  --project=nowhere-link-prod
```

### Build Locally (Alternative)

```bash
cd app

# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build image
docker build -t us-central1-docker.pkg.dev/nowhere-link-prod/nowhere-link-repo/link-server:v1 .

# Push image
docker push us-central1-docker.pkg.dev/nowhere-link-prod/nowhere-link-repo/link-server:v1
```

### Deploy to Kubernetes

After building a new image, update the deployment:

```bash
cd ../k8s
kubectl rollout restart deployment/link-server
```

Or update with a new version tag:
```bash
kubectl set image deployment/link-server \
  link-server=us-central1-docker.pkg.dev/nowhere-link-prod/nowhere-link-repo/link-server:v2
```

## Customization

### Update AASA Configuration

Edit `main.py` and update the AASA endpoint with your real Team ID and bundle identifier:

```python
"appIDs": ["TEAMID.com.nowhereapp.ios"]
```

After changes, rebuild and redeploy.

### Update Open Graph Images

Replace `static/og-default.png` with your actual Open Graph image (recommended: 1200x630px).

### User Data Schema

The `/u/{user_id}` endpoint expects Firestore documents at `users/{user_id}` with:
- `displayName` (string) - User's display name
- `bio` (string, optional) - User bio for OG description
- `ogImageUrl` (string, optional) - Custom OG image URL

## Testing

```bash
# Test landing page
curl http://links.nowhereapp.ai/

# Test AASA
curl https://links.nowhereapp.ai/.well-known/apple-app-site-association

# Test user profile
curl https://links.nowhereapp.ai/u/testuser

# Validate OG tags
curl -s https://links.nowhereapp.ai/u/testuser | grep "og:"
```
