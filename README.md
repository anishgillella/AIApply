# LinkedIn Easy Apply Agent

Automates searching and applying to "AI Engineer" LinkedIn jobs posted within the last 24 hours using the open-source [browser-use](https://docs.browser-use.com) agent framework. The agent runs locally, controls Chromium via Playwright, and leverages OpenAI `gpt-4o` for reasoning during the application workflow.

## Prerequisites
- macOS with Python 3.12+
- LinkedIn credentials that can use Easy Apply
- Resume file path accessible on this machine
- OpenAI API key with access to GPT-4o

## Setup
1. Create an `.env` file (already present) containing:
   ```
   OPENAI_API_KEY=...
   LINKEDIN_LOGIN_EMAIL=...
   LINKEDIN_PASSWORD=...
   RESUME_PATH=/absolute/path/to/resume.pdf
   ```
   Keep this file private.
2. Create and activate the virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium --with-deps
   ```

## Running the agent
```bash
source .venv/bin/activate
python src/main.py
```

The agent will:
- Launch Chromium in headed mode, constrained to LinkedIn domains
- Log in using the provided credentials
- Apply filters (AI Engineer, past 24 hours, Easy Apply)
- Iterate job cards and launch the Easy Apply flow when available
- Use the supplied resume for uploads and answer prompts with conservative defaults
- Save a run history at `application-history.json`

## Safety and operations
- Credentials are injected via `sensitive_data` placeholders; the agent only exposes them on `linkedin.com` domains.
- Automation may violate LinkedIn terms of service—use at your own risk.
- If captchas or unexpected verification appear, the agent reports the issue instead of bypassing it.

## Troubleshooting
- Ensure Chromium can access your resume path (use absolute path).
- If the agent stalls, close the Chromium window and rerun.
- Review `application-history.json` for step-by-step details.

## References
- [Browser Use Quickstart](https://docs.browser-use.com/quickstart)
- [browser-use GitHub](https://github.com/browser-use/browser-use)
