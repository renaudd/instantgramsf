# Deployment Guide — Night Merchant: InstantGram SF

This project uses the same hybrid static + Cloud Run + Firebase architecture as **Night Merchant**:

1. **Source Repository**: `https://github.com/renaudd/instantgramsf`
2. **Static Web Frontend**: `https://dashiellrenaud.com/instantgram` (served from `/instantgram/` inside `dashiellrenaud_site` on GitHub Pages)
3. **Backend API + Persistent Database**: Google Cloud Run (`instantgramsf-api`) + Firebase Authentication + Cloud Firestore in a dedicated Firebase / Google Cloud project (e.g., `instantgramsf`)

---

## Part 1: Push Source Code to `github.com/renaudd/instantgramsf`

### 1A. Create the Empty Repository on GitHub
1. In your browser, go to **[https://github.com/new](https://github.com/new)**.
2. Set **Repository name** to `instantgramsf` (under owner `renaudd`).
3. Leave **"Add a README file"**, **"Add .gitignore"**, and **"Choose a license"** **unchecked** (the local repository already has commits, `.gitignore`, and `LICENSE`).
4. Click **Create repository**.

### 1B. Push from Your Local Terminal (Mac)
Run in your **Local Mac Terminal**:

```bash
cd /Users/rend/Development/FreeParking
git remote set-url origin git@github.com:renaudd/instantgramsf.git 2>/dev/null || git remote add origin git@github.com:renaudd/instantgramsf.git
git branch -M main
git push -u origin main
```

---

## Part 2: Create the New Firebase + Google Cloud Project & Enable Services

### 2A. In the Firebase Console (Browser)
1. Open **[https://console.firebase.google.com/](https://console.firebase.google.com/)** and click **Create a project** (or **Add project**).
2. Enter Project Name: **`instantgramsf`** (note the exact **Project ID** Firebase assigns, e.g. `instantgramsf` or `instantgramsf-xxxxx`).
3. Enable **Authentication**:
   - In the left sidebar, click **Build → Authentication → Get started**.
   - Under the **Sign-in method** tab, enable:
     - **Email/Password**
     - **Google** (choose a support email and click **Save**)
   - Under **Authentication → Settings → Authorized domains**, click **Add domain** and add:
     - `dashiellrenaud.com`
     - `www.dashiellrenaud.com`
4. Enable **Cloud Firestore**:
   - In the left sidebar, click **Build → Firestore Database → Create database**.
   - Select **Standard edition**, choose location **`us-west2` (Los Angeles)** (or `nam5`), and start in **Production mode** (the Cloud Run backend accesses Firestore via its server-side Admin SDK service account).
5. Register a **Web App** in Firebase to get your `firebaseConfig`:
   - Go to **Project Overview (⚙️ Gear icon) → Project settings → General**.
   - Scroll to **Your apps** and click the **`</>` (Web)** icon.
   - App nickname: `instantgramsf-web`, then click **Register app**.
   - Copy the `firebaseConfig` values (`apiKey`, `authDomain`, `projectId`, `storageBucket`, `messagingSenderId`, `appId`, `measurementId`).

---

## Part 3: Deploy the Backend to Google Cloud Run (Run in Google Cloud Shell)

1. Open **[https://console.cloud.google.com/](https://console.cloud.google.com/)**, select your new **`instantgramsf`** project in the top project picker, and click the **Activate Cloud Shell (`>_`)** icon in the top-right toolbar.
2. In the **Google Cloud Shell terminal**, run the following commands (replace `YOUR_PROJECT_ID` with your actual Firebase Project ID and `YOUR_FIREBASE_WEB_API_KEY` with the `apiKey` from Step 2A.5):

```bash
# 1. Set your active Google Cloud project
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-west2"
export SERVICE_NAME="instantgramsf-api"
export FIREBASE_WEB_API_KEY="YOUR_FIREBASE_WEB_API_KEY"

gcloud config set project "$PROJECT_ID"

# 2. Enable required Google Cloud APIs (Cloud Run, Cloud Build, Artifact Registry, Firestore)
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com

# 3. Clone (or pull) the InstantGram SF repository in Cloud Shell
rm -rf ~/instantgramsf
git clone https://github.com/renaudd/instantgramsf.git ~/instantgramsf
cd ~/instantgramsf

# 4. Generate a persistent session secret and deploy to Cloud Run
export SESSION_SECRET="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --set-env-vars "NIGHTMERCHANT_CLOUD_RUN=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},FIREBASE_PROJECT_ID=${PROJECT_ID},FIREBASE_WEB_API_KEY=${FIREBASE_WEB_API_KEY},NIGHTMERCHANT_PUBLIC_URL=https://dashiellrenaud.com/instantgram/,NIGHTMERCHANT_SESSION_SECRET=${SESSION_SECRET}"
```

3. When `gcloud run deploy` finishes, it prints a **Service URL** like:
   ```text
   Service URL: https://instantgramsf-api-XXXXXXXXXXXX.us-west2.run.app
   ```
   Copy that `https://instantgramsf-api-...run.app` URL.

---

## Part 4: Point `public/config.js` at Your New Cloud Run Service & Re-Sync to `dashiellrenaud.com/instantgram`

1. Back in your **Local Mac Terminal**, update `/Users/rend/Development/FreeParking/public/config.js` with your new Cloud Run URL and non-secret `firebaseConfig` identifiers:

```javascript
window.NIGHTMERCHANT_CONFIG = window.NIGHTMERCHANT_CONFIG || {
  apiBaseUrl: isLocalDev ? "" : "https://instantgramsf-api-XXXXXXXXXXXX.us-west2.run.app",
  firebaseConfig: {
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.firebasestorage.app",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID",
  },
};
```

2. Sync `public/` into `/Users/rend/Development/dashiellrenaud_site/instantgram` and push both repositories from your **Local Mac Terminal**:

```bash
# Sync static webapp to dashiellrenaud_site/instantgram
cd /Users/rend/Development/FreeParking
python3 scripts/sync_to_site.py

# Commit and push InstantGram SF source repo
git add public/config.js
git commit -m "Configure production Cloud Run URL and Firebase project for InstantGram SF"
git push origin main

# Commit and push dashiellrenaud_site so https://dashiellrenaud.com/instantgram updates live
cd /Users/rend/Development/dashiellrenaud_site
git add instantgram .nojekyll
git commit -m "Update InstantGram SF webapp at /instantgram"
git push origin main
```
