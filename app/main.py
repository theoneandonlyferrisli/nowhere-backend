from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import random
import httpx

app = FastAPI()

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
    
    # Redirect links.nowhereapp.ai to landing domain
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

# Profile routes - only on nowhereapp.ai
@app.api_route("/profile", methods=["GET", "HEAD"], response_class=HTMLResponse)
def profile_no_id():
    """Error page for profile access without ID"""
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
async def user_profile(profile_id: str):
    """Serve user profile page on nowhereapp.ai with dynamic OG tags"""
    profile_path = static_dir / "profile.html"
    
    if profile_path.exists():
        # Read the HTML template
        with open(profile_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # For test profile, inject static OG tags
        if profile_id.lower() == "test":
            first_name = "John"
            countries_count = 5
            cities_count = 8
            places_count = 8
            profile_pic_url = get_random_og_image()  # Use random thumbnail if no profile pic
            
            og_title = f"{first_name}'s nowhere passport"
            og_description = f"{countries_count} countries • {cities_count} cities • {places_count} places"
            og_url = f"{LANDING_DOMAIN}/profile/{profile_id}"
            
            # Inject OG tags - replace the entire OG tags block
            og_tags = f'''<!-- OG Tags Placeholder - Will be injected by server -->
    <meta property="og:type" content="profile" />
    <meta property="og:title" content="{escape(og_title)}" />
    <meta property="og:description" content="{escape(og_description)}" />
    <meta property="og:image" content="{profile_pic_url}" />
    <meta property="og:url" content="{og_url}" />
    
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escape(og_title)}" />
    <meta name="twitter:description" content="{escape(og_description)}" />
    <meta name="twitter:image" content="{profile_pic_url}" />'''
            
            # Replace the entire OG tags block (from comment through all meta tags)
            html_content = html_content.replace(
                '''<!-- OG Tags Placeholder - Will be injected by server -->
    <meta property="og:type" content="profile" />
    <meta property="og:title" content="nowhere passport" />
    <meta property="og:description" content="Explore the world with nowhere" />
    <meta property="og:image" content="" />
    <meta property="og:url" content="" />
    
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="nowhere passport" />
    <meta name="twitter:description" content="Explore the world with nowhere" />
    <meta name="twitter:image" content="" />''',
                og_tags
            )
            
            return HTMLResponse(content=html_content, media_type="text/html")
        
        # For real profiles, fetch via Cloud Function API (same as frontend)
        try:
            cloud_function_url = "https://us-central1-steps-d1514.cloudfunctions.net/getUserProfile"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    cloud_function_url,
                    params={"id": profile_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and data.get("profile"):
                        u = data["profile"]
                        first_name = (u.get("firstName", "") or "").strip()
                        
                        # Get counts
                        countries_count = len(u.get("visitedCountries", []))
                        cities_count = len(u.get("visitedCities", []))
                        
                        # Normalize places count
                        places_count = 0
                        visited_pois = u.get("visitedPois", [])
                        if isinstance(visited_pois, list):
                            places_count = len(visited_pois)
                        elif isinstance(visited_pois, dict):
                            places_count = len(visited_pois)
                        
                        # Use profile picture if available, otherwise random thumbnail
                        profile_pic_url = (u.get("profilePictureUrl", "") or "").strip()
                        if profile_pic_url.startswith('//'):
                            profile_pic_url = f"https:{profile_pic_url}"
                        
                        # For Google profile pictures, increase size to 1200px for better OG images
                        if profile_pic_url and 'googleusercontent.com' in profile_pic_url:
                            # Replace size parameter (e.g., s96-c) with s1200 for high-res OG image
                            import re
                            profile_pic_url = re.sub(r'=s\d+-c$', '=s1200', profile_pic_url)
                        
                        if not profile_pic_url:
                            profile_pic_url = get_random_og_image()
                        
                        og_title = f"{first_name}'s nowhere passport"
                        og_description = f"{countries_count} countries • {cities_count} cities • {places_count} places"
                        og_url = f"{LANDING_DOMAIN}/profile/{profile_id}"
                        
                        # Inject OG tags - replace the entire OG tags block
                        og_tags = f'''<!-- OG Tags Placeholder - Will be injected by server -->
    <meta property="og:type" content="profile" />
    <meta property="og:title" content="{escape(og_title)}" />
    <meta property="og:description" content="{escape(og_description)}" />
    <meta property="og:image" content="{profile_pic_url}" />
    <meta property="og:url" content="{og_url}" />
    
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escape(og_title)}" />
    <meta name="twitter:description" content="{escape(og_description)}" />
    <meta name="twitter:image" content="{profile_pic_url}" />'''
                        
                        # Replace the entire OG tags block (from comment through all meta tags)
                        html_content = html_content.replace(
                            '''<!-- OG Tags Placeholder - Will be injected by server -->
    <meta property="og:type" content="profile" />
    <meta property="og:title" content="nowhere passport" />
    <meta property="og:description" content="Explore the world with nowhere" />
    <meta property="og:image" content="" />
    <meta property="og:url" content="" />
    
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="nowhere passport" />
    <meta name="twitter:description" content="Explore the world with nowhere" />
    <meta name="twitter:image" content="" />''',
                            og_tags
                        )
                        
                        return HTMLResponse(content=html_content, media_type="text/html")
        except Exception as e:
            print(f"Error fetching profile {profile_id} via Cloud Function: {e}")
        
        # If Cloud Function fetch fails or profile doesn't exist, serve template with default OG tags
        return FileResponse(profile_path, media_type="text/html")
    
    # Fallback if profile.html doesn't exist
    raise HTTPException(status_code=404, detail="Profile page not found")

# API endpoint to fetch user profile (proxies Cloud Function)
@app.get("/api/profile/{profile_id}")
async def api_get_profile(profile_id: str):
    """
    Proxy endpoint to fetch user profile from Cloud Function.
    This prevents exposing the Cloud Function URL to the client
    and avoids CORS/permission issues with direct Firestore access.
    """
    cloud_function_url = "https://us-central1-steps-d1514.cloudfunctions.net/getUserProfile"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                cloud_function_url,
                params={"id": profile_id}
            )
            
            # Return the response from the Cloud Function
            if response.status_code == 200:
                return response.json()
            else:
                # Pass through error responses
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Cloud Function returned {response.status_code}"
                )
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error calling Cloud Function: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
