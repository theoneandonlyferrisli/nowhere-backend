from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from google.cloud import firestore

app = FastAPI()

# Firestore client:
# Uses Application Default Credentials (Workload Identity on GKE)
db = firestore.Client()

PUBLIC_BASE = "https://links.nowhereapp.ai"

def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )

@app.get("/", response_class=HTMLResponse)
def landing():
    # Lightweight landing page; customize copy & styling as needed.
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Nowhere · Your Places Passport</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta property="og:title" content="Nowhere · Your Places Passport" />
    <meta property="og:description" content="Turn your trips, photos, and saved spots into a living passport." />
    <meta property="og:image" content="https://links.nowhereapp.ai/static/og-default.png" />
    <meta property="og:url" content="https://links.nowhereapp.ai/" />
    <meta name="twitter:card" content="summary_large_image" />
  </head>
  <body>
    <h1>Nowhere</h1>
    <p>Your personal places graph. Smart imports. Beautiful passports. Deep links that just work.</p>
  </body>
</html>"""

@app.get("/.well-known/apple-app-site-association")
def aasa():
    # Replace TEAMID and bundle with your real values before shipping.
    payload = {
        "applinks": {
            "details": [
                {
                    "appIDs": ["TEAMID.com.nowhereapp.ios"],
                    "components": [
                        { "/u/*": {} }
                    ]
                }
            ]
        }
    }
    return JSONResponse(content=payload, media_type="application/json")

@app.get("/u/{user_id}", response_class=HTMLResponse)
def user_passport(user_id: str):
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    u = doc.to_dict()
    display = u.get("displayName", "Nowhere traveler")
    bio = u.get("bio", f"{display}'s travel passport on Nowhere")
    og_image = u.get("ogImageUrl", f"{PUBLIC_BASE}/static/og-default.png")
    url = f"{PUBLIC_BASE}/u/{user_id}"

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{escape(display)} · Nowhere Passport</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <meta property="og:type" content="website" />
    <meta property="og:title" content="{escape(display)} · Nowhere Passport" />
    <meta property="og:description" content="{escape(bio)}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{og_image}" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escape(display)} · Nowhere Passport" />
    <meta name="twitter:description" content="{escape(bio)}" />
    <meta name="twitter:image" content="{og_image}" />

    <!-- App Links / Universal Links -->
    <meta property="al:ios:url" content="nowhereapp://user/{escape(user_id)}" />
    <meta property="al:ios:app_store_id" content="YOUR_APPSTORE_ID" />
    <meta property="al:ios:app_name" content="Nowhere" />

    <!-- Fallback: if app not installed, can redirect to web profile (optional)
         For now we avoid immediate meta refresh to not break crawlers.
    -->
  </head>
  <body>
  </body>
</html>"""
    return HTMLResponse(content=html, media_type="text/html")
