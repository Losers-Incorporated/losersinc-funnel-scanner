from kiteconnect import KiteConnect
import os

# Load your Zerodha API credentials
API_KEY = "qamoej8ga26cbfxh"
API_SECRET = "i7uxaze048ezqzrpo9at210waeel4lyn"

# Initialize KiteConnect session
kite = KiteConnect(api_key=API_KEY)

# Step 1: Print login URL
print("\n🔐 Visit this login URL in your browser and authorize the app:")
print(kite.login_url())

# Step 2: Get the request token from user
request_token = input("\n📥 Paste the request_token here: ")

# Step 3: Generate the session and fetch access token
try:
    data = kite.generate_session(request_token, api_secret=API_SECRET)
    access_token = data["access_token"]

    # Save token to a file
    with open("token.txt", "w") as f:
        f.write(access_token)

    print("\n✅ Access token generated and saved to 'token.txt'.")
    print("Use this token in your Render or GitHub scripts.")

except Exception as e:
    print("\n❌ Error generating access token:", e)

