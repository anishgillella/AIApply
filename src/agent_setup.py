"""Helpers for constructing the Browser Use agent with resume context."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Final

from browser_use import Agent, BrowserSession
from browser_use.browser import BrowserProfile
from browser_use.llm.openai.chat import ChatOpenAI

from .config import LinkedinCredentials


LINKEDIN_DOMAIN: Final[str] = "https://www.linkedin.com"
LINKEDIN_JOBS_URL: Final[str] = (
    "https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer&f_TPR=r86400&f_AL=true"
)


def build_browser_session() -> BrowserSession:
    profile = BrowserProfile(
        headless=False,
        user_data_dir=os.path.join(os.getcwd(), "playwright-data"),
        wait_between_actions=0.3,
        highlight_elements=True,
    )
    return BrowserSession(browser_profile=profile, headless=False)


def build_prompt_extension() -> str:
    return """
<linkedin_workflow>
- Log in using the provided credentials only on official LinkedIn login forms.
- Prioritize the existing-account "Sign in" experience; do not click "Join now" or create-new-account flows.
- Navigate to the LinkedIn Jobs page filtered for AI Engineer roles posted in the last 24 hours.
- Set filters once when the page loads: ensure "Easy Apply" is active before reviewing listings. If the quick filter is not visible, open "All filters" or "More filters", scroll the filters panel until "Easy Apply" is visible, toggle it on, then apply filters. Do not refresh or re-run the search unless the page becomes unusable.
- For each job card in the results list:
  1. Open job details in the same tab.
  2. Review the description briefly to ensure relevance to AI Engineering.
  3. If the card shows "Applied", "Already applied", "Applied before", "Promoted", or lacks an Easy Apply button, skip it and move on without refreshing the page.
  4. Launch the Easy Apply flow when available; otherwise skip the job politely.
  5. Upload the provided resume when prompted.
  6. Answer application questions concisely using professional tone. If unsure, prefer truthful defaults such as "No" or "Not specified" rather than guessing.
  7. Deselect any optional "Follow" or "Follow company" checkboxes before continuing.
  8. Review the entire form, then submit once all sections are complete. Do not close the modal prematurely; stay on the application until it is either submitted or clearly blocked.
  9. If the Easy Apply modal fails (missing upload control, navigation error, etc.), exhaust all available actions within the modal, document the issue, then close it and move on to the next listing without refreshing.
- After each application, document status in a local notes file.
- Stop when listings are exhausted or when the user explicitly asks to finish.
</linkedin_workflow>

<candidate_profile>
- Full name: Anish Gillella
- Email: **********
- Phone: **********
- Requires sponsorship: No
- Willing to relocate: Yes
- Desired compensation: 100000 USD annually (enter as digits when prompted)
- Default years of experience for any skill fields: 2
</candidate_profile>

<form_responses>
- For contact details, pull values from <candidate_profile>.
- When asked about visa or sponsorship needs, answer that no sponsorship is required now or in the future.
- Confirm willingness to relocate whenever prompted.
- Enter desired salary as 100000 unless a different format is requested; if asked for hourly rates, divide appropriately and note the conversion in the summary.
- For skills requesting years of experience, enter 2 unless specific instructions override.
- If a question is unanswerable with provided data, pause submission, note the missing field, and request clarification.
</form_responses>

<sensitive_data_placeholders>
- Use <secret>linkedin_email</secret> for the LinkedIn login email.
- Use <secret>linkedin_password</secret> for the LinkedIn login password.
- Use <secret>resume_path</secret> when selecting the resume file to upload.
</sensitive_data_placeholders>

<good_practices>
- Stay on trusted LinkedIn-owned domains when possible; verify URLs before entering credentials.
- Always confirm current URL and visible filters before taking actions.
- Use scrolling to reveal more job cards when the list ends.
- Take a screenshot or extract summary after submitting each application to capture confirmation details.
- If a captcha or unexpected verification appears, pause and request human assistance via the final report instead of attempting risky workarounds.
</good_practices>
"""


def build_sensitive_data(creds: LinkedinCredentials) -> dict[str, dict[str, str]]:
    return {
        "https://*.linkedin.com": {
            "linkedin_email": creds.email,
            "linkedin_password": creds.password,
            "resume_path": creds.resume_path,
        }
    }


def build_task() -> str:
    return (
        "Open LinkedIn Jobs, search for AI Engineer roles posted in the last 24 hours with Easy Apply enabled."
        " Apply to each relevant listing using the provided resume. Keep track of which positions were applied to"
        " and note any issues encountered."
    )


def build_agent(
    task: str,
    llm: ChatOpenAI,
    browser_session: BrowserSession,
    sensitive_data: dict[str, dict[str, str]],
    prompt_extension: str,
    resume_path: str,
) -> Agent:
    return Agent(
        task=task,
        llm=llm,
        browser_session=browser_session,
        sensitive_data=sensitive_data,
        extend_system_message=prompt_extension,
        directly_open_url=False,
        include_recent_events=True,
        available_file_paths=[resume_path],
        initial_actions=[
            {
                "navigate": {
                    "url": LINKEDIN_JOBS_URL,
                    "new_tab": False,
                }
            }
        ],
    )


