# Link Server Application

FastAPI application serving the Nowhere link server with dual-domain architecture, Universal Links, and beautiful UI.

## What It Does

The link server provides domain-based routing:

### **nowhereapp.ai** (Landing Page Domain)

1. **Landing Page** (`/`) - Full-screen carousel with glassmorphism overlay featuring:
   - Dynamic image carousel from Firebase Storage (5 cities: NYC, Dubai, Paris, Sydney, Shanghai)
   - iOS 18-style liquid glass effect overlay
   - Responsive design with smooth transitions
   - Configurable via `static/config.js`

2. **Apple App Site Association** (`/.well-known/apple-app-site-association`) - Universal Links configuration:
   - App ID: `G5Q9BF9HW9.com.AceKingLLC.Steps`
   - Path matching for all routes

### **links.nowhereapp.ai** (Profile Domain)

1. **Root Redirect** (`/`) - Automatically redirects to `nowhereapp.ai`

2. **User Profile Pages** (`/profile/{profile_id}`) - Liquid glass UI profile pages with:
   - User avatar and display name
   - Travel stats (places, cities, countries)
   - "Open in App" deep link button
   - Fetches user data via backend API (proxies Cloud Function)

3. **Profile API Endpoint** (`/api/profile/{profile_id}`) - Backend API that:
   - Proxies requests to the Cloud Function `getUserProfile`
   - Prevents exposing Cloud Function URL to clients
   - Handles authentication and permissions server-side
   - Returns JSON profile data

4. **Legacy Redirect** (`/u/{user_id}`) - 301 redirects to `/profile/{user_id}`

4. **Error Page** (`/profile` without ID) - Beautiful error page matching design system

5. **AASA File** - Same Universal Links configuration as root domain

## Architecture

### Profile Data Flow

The profile fetching has been updated to use a secure backend API proxy pattern:

1. **Client** (`profile.html`) → Makes request to `/api/profile/{profile_id}`
2. **Backend API** (`main.py`) → Proxies request to Cloud Function with server credentials
3. **Cloud Function** → Fetches data from Firestore and returns to backend
4. **Backend** → Returns profile data to client

**Benefits:**
- Cloud Function URL not exposed to clients
- No CORS or permission issues with direct Firestore access
- Centralized authentication handling
- User profiles don't need to be publicly readable

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **httpx** - Async HTTP client for Cloud Function requests
- **Google Cloud Firestore** - User data storage (via Cloud Function)
- **Firebase Storage** - Image hosting for carousel
- **Workload Identity** - Authenticates to GCP services via GKE service account

## Files

- `main.py` - FastAPI application with domain-based routing logic
- `Dockerfile` - Container image definition
- `static/index.html` - Carousel landing page
- `static/config.js` - Landing page configuration (Firebase URLs, carousel settings)
- `static/profile.html` - User profile page template
- `static/error.html` - Error page for invalid profile access
- `static/.well-known/apple-app-site-association` - AASA file for Universal Links

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires Firestore credentials)
uvicorn main:app --reload --port 8080
```

### Landing Page Configuration

Edit `static/config.js` to customize:
- App name and tagline
- Firebase Storage bucket
- Multiple city image folders
- Maximum photos to display
- Carousel shuffle and transition timing
- Debug mode

```javascript
const CONFIG = {
    APP_NAME: 'nowhere',
    APP_TAGLINE: 'Explore. Discover. Share.',
    FIREBASE_BUCKET: 'steps-d1514.firebasestorage.app',
    
    // Add multiple city folders with image counts
    CITY_IMAGES: [
        {
            path: 'cities/new-york_new-york_us/featureImgsFullRes',
            count: 5
        },
        {
            path: 'cities/tokyo_tokyo_jp/featureImgsFullRes',
            count: 3
        }
    ],
    
    CAROUSEL: {
        MAX_PHOTOS: 10,            // Max photos to show
        TRANSITION_DURATION: 5000,
        PRELOAD_NEXT: true,
        SHUFFLE: true              // Randomize images from different cities
    }
};
```

## Building & Deploying

### Build and Push Image (Cloud Build - Required)

**Note:** Local Docker is not installed. Always use Cloud Build.

```bash
cd app

# Build using Cloud Build with YYYY.MM.N version format
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/nowhere-link-prod/nowhere-link-repo/link-server:2025.11.1
```

**Versioning:** Use `YYYY.MM.N` format (e.g., 2025.11.1 for first version in November 2025)

### Deploy to Kubernetes

After building a new image, update the deployment:

```bash
cd ../k8s

# Edit deployment.yaml to use new version
# Then apply:
kubectl apply -f deployment.yaml

# Monitor rollout
kubectl rollout status deployment/link-server
```

## Configuration & Customization

### Firebase Storage Images

The landing page carousel loads images from multiple city folders in Firebase Storage. To configure:

1. **Update `static/config.js`** with your Firebase Storage bucket and city paths:
   ```javascript
   CITY_IMAGES: [
       {
           path: 'cities/new-york_new-york_us/featureImgsFullRes',
           count: 5  // Number of images (1.jpg through 5.jpg)
       },
       {
           path: 'cities/paris_ile-de-france_fr/featureImgsFullRes',
           count: 4
       }
   ]
   ```

2. **Set up Firebase Storage permissions**:
   - For public access, set Firebase Storage rules to allow read
   - Images must be accessible via public URLs
   - Images are automatically loaded from all configured city folders

3. **Image naming**: Images should be numbered sequentially (1.jpg, 2.jpg, etc.) in each city's `featureImgsFullRes` folder

4. **Carousel behavior**:
   - Images from all cities are combined
   - Optionally shuffled for variety
   - Limited to `MAX_PHOTOS` setting
   - Smooth transitions with preloading

### Update AASA Configuration

The AASA file is located at `static/.well-known/apple-app-site-association`. Current configuration:
- App ID: `G5Q9BF9HW9.com.AceKingLLC.Steps`
- Paths: All routes (`*`)
- Web credentials enabled

To update, edit the JSON file directly or update the fallback in `main.py`.

After changes, rebuild and redeploy.

### User Data Schema

The `/u/{user_id}` endpoint expects Firestore documents at `users/{user_id}` with:
- `displayName` (string) - User's display name
- `bio` (string, optional) - User bio for OG description
- `ogImageUrl` (string, optional) - Custom OG image URL

## Testing

```bash
# Test landing page
curl http://localhost:8080/

# Test AASA
curl http://localhost:8080/.well-known/apple-app-site-association

# Test user profile
curl http://localhost:8080/u/testuser

# Validate OG tags
curl -s http://localhost:8080/u/testuser | grep "og:"

# View landing page in browser
open http://localhost:8080/
```

### Firebase Storage Permissions

If carousel images don't load, check Firebase Storage permissions:

```bash
# Images should be accessible at URLs like:
# https://firebasestorage.googleapis.com/v0/b/steps-d1514.firebasestorage.app/o/cities%2Fnew-york_new-york_us%2FfeatureImgsFullRes%2F1.jpg?alt=media

# To make images public, update Firebase Storage rules in the Firebase Console
```
