from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore
from pathlib import Path
import random

app = FastAPI()

# Firestore client:
# Uses Application Default Credentials (Workload Identity on GKE)
db = firestore.Client()

LANDING_DOMAIN = "https://nowhereapp.ai"
LINKS_DOMAIN = "https://links.nowhereapp.ai"

# City configurations for random OG image
CITY_IMAGES = [
    {"path": "cities/new-york_new-york_us/featureImgsThumbnail", "count": 1},
    {"path": "cities/dubai_dubayy_ae/featureImgsThumbnail", "count": 1},
    {"path": "cities/paris_ile-de-france_fr/featureImgsThumbnail", "count": 1},
    {"path": "cities/sydney_new-south-wales_au/featureImgsThumbnail", "count": 1},
    {"path": "cities/shanghai_shanghai_cn/featureImgsThumbnail", "count": 1},
]
FIREBASE_BUCKET = "steps-d1514.firebasestorage.app"

def get_random_og_image() -> str:
    """Get a random thumbnail image URL for OG tags"""
    city = random.choice(CITY_IMAGES)
    img_num = random.randint(1, city["count"])
    path = f"{city['path']}/{img_num}.jpg"
    # URL encode the path
    encoded_path = path.replace("/", "%2F")
    return f"https://firebasestorage.googleapis.com/v0/b/{FIREBASE_BUCKET}/o/{encoded_path}?alt=media"

# Mount static files directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )

def get_host(request: Request) -> str:
    """Get the host from the request"""
    return request.headers.get("host", "").lower()

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def landing(request: Request):
    host = get_host(request)
    
    # If accessed via links.nowhereapp.ai, redirect to landing domain
    if "links.nowhereapp.ai" in host:
        return RedirectResponse(url=LANDING_DOMAIN, status_code=302)
    
    # Serve carousel landing page for nowhereapp.ai with dynamic OG tags
    index_path = static_dir / "index.html"
    if index_path.exists():
        # Read the HTML file
        html_content = index_path.read_text()
        
        # Get random OG image
        og_image = get_random_og_image()
        
        # Inject OG meta tags after the viewport meta tag
        og_tags = f"""
    
    <!-- Open Graph / Link Preview -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{LANDING_DOMAIN}" />
    <meta property="og:title" content="nowhere - Explore. Discover. Share." />
    <meta property="og:description" content="Your personal places passport. Discover and share the world's most beautiful destinations." />
    <meta property="og:image" content="{og_image}" />
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="nowhere - Explore. Discover. Share." />
    <meta name="twitter:description" content="Your personal places passport. Discover and share the world's most beautiful destinations." />
    <meta name="twitter:image" content="{og_image}" />
"""
        
        # Insert OG tags after the viewport meta tag
        html_content = html_content.replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">{og_tags}'
        )
        
        return HTMLResponse(content=html_content)
    
    # Fallback if index.html is missing
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>nowhere · Your Places Passport</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body>
    <h1>nowhere</h1>
    <p>Your personal places graph. Smart imports. Beautiful passports. Deep links that just work.</p>
  </body>
</html>"""

@app.api_route("/.well-known/apple-app-site-association", methods=["GET", "HEAD"])
def aasa():
    # Serve the AASA file from static directory
    aasa_path = static_dir / ".well-known" / "apple-app-site-association"
    if aasa_path.exists():
        return FileResponse(aasa_path, media_type="application/json")
    
    # Fallback with correct app ID
    payload = {
        "applinks": {
            "apps": [],
            "details": [
                {
                    "appIDs": ["G5Q9BF9HW9.com.AceKingLLC.Steps"],
                    "paths": ["*"]
                }
            ]
        },
        "webcredentials": {
            "apps": ["G5Q9BF9HW9.com.AceKingLLC.Steps"]
        }
    }
    return JSONResponse(content=payload, media_type="application/json")

# Error page for invalid profile access
@app.api_route("/profile", methods=["GET", "HEAD"], response_class=HTMLResponse)
def profile_no_id():
    error_path = static_dir / "error.html"
    if error_path.exists():
        return FileResponse(error_path, media_type="text/html", status_code=400)
    
    # Fallback error page
    return HTMLResponse(
        content="""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Invalid Profile · nowhere</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 20px;
      }
      .error-container {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(40px);
        padding: 48px;
        border-radius: 32px;
        border: 1px solid rgba(255, 255, 255, 0.3);
      }
      h1 { font-size: 3rem; margin-bottom: 1rem; }
      p { font-size: 1.2rem; opacity: 0.9; }
    </style>
  </head>
  <body>
    <div class="error-container">
      <h1>Invalid Profile</h1>
      <p>No profile ID provided</p>
    </div>
  </body>
</html>""",
        status_code=400,
        media_type="text/html"
    )

@app.api_route("/profile/{profile_id}", methods=["GET", "HEAD"], response_class=HTMLResponse)
def user_profile(profile_id: str):
    """Serve user profile page"""
    profile_path = static_dir / "profile.html"
    if profile_path.exists():
        return FileResponse(profile_path, media_type="text/html")
    
    # Fallback: fetch from Firestore and render inline
    try:
        doc = db.collection("users").document(profile_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        u = doc.to_dict()
        display = u.get("displayName", "nowhere traveler")
        bio = u.get("bio", f"{display}'s travel passport")
        og_image = u.get("ogImageUrl", f"{LINKS_DOMAIN}/static/og-default.png")
        url = f"{LINKS_DOMAIN}/profile/{profile_id}"

        html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{escape(display)} · nowhere</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <meta property="og:type" content="profile" />
    <meta property="og:title" content="{escape(display)} · nowhere" />
    <meta property="og:description" content="{escape(bio)}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{og_image}" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escape(display)} · nowhere" />
    <meta name="twitter:description" content="{escape(bio)}" />
    <meta name="twitter:image" content="{og_image}" />

    <!-- App Links / Universal Links -->
    <meta property="al:ios:url" content="nowhereapp://profile/{escape(profile_id)}" />
    <meta property="al:ios:app_store_id" content="YOUR_APPSTORE_ID" />
    <meta property="al:ios:app_name" content="nowhere" />
  </head>
  <body>
    <h1>{escape(display)}</h1>
    <p>{escape(bio)}</p>
  </body>
</html>"""
        return HTMLResponse(content=html, media_type="text/html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy /u/{user_id} endpoint - redirect to new /profile/{profile_id}
@app.api_route("/u/{user_id}", methods=["GET", "HEAD"], response_class=HTMLResponse)
def user_passport_legacy(user_id: str):
    """Legacy endpoint - redirect to new profile URL"""
    return RedirectResponse(url=f"{LINKS_DOMAIN}/profile/{user_id}", status_code=302)
