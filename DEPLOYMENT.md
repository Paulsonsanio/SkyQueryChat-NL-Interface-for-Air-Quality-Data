# Deploying SkyQueryChat on Streamlit Community Cloud

This guide provides step-by-step instructions to deploy **SkyQueryChat** live on [Streamlit Community Cloud](https://streamlit.io/cloud) directly from your GitHub repository.

---

### Prerequisites
1. **GitHub Repository**: Make sure your latest code is pushed to your GitHub repo:
   `https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data`
2. **Streamlit Cloud Account**: Sign in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.

---

### Deployment Steps

1. **Create New App**:
   - In Streamlit Community Cloud, click **"Create app"** (or **"New app"**).
   - Choose **"I already have an app"**.

2. **Select Repository Details**:
   - **Repository**: `Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data`
   - **Branch**: `main` (or your active branch)
   - **Main file path**: `app.py` (or `streamlit_app.py`)

3. **Configure Secrets (Crucial for Groq LLM)**:
   - Before hitting deploy, click **"Advanced settings..."** at the bottom.
   - Go to the **Secrets** section.
   - Paste your configuration keys:
     ```toml
     GROQ_API_KEY = "your_actual_groq_api_key"
     SKYQUERY_MODEL = "openai/gpt-oss-120b"
     ```
   - Click **Save**.

4. **Deploy**:
   - Click **"Deploy!"**.
   - Streamlit will read `requirements.txt`, install dependencies, load the cached grid from `data/tempo_no2_grid.npz`, and start the app in under 2 minutes.

---

### Included Deployment Files
- `app.py`: Primary Streamlit application entrypoint.
- `streamlit_app.py`: Auto-detection wrapper file for Streamlit Community Cloud.
- `.streamlit/config.toml`: Production theme configuration (clean light theme, custom colors, port settings).
- `.streamlit/secrets.toml.example`: Template for setting API secrets.
- `requirements.txt`: Lightweight, curated Python dependencies (`numpy`, `pandas`, `altair`, `streamlit`, `openai`).
