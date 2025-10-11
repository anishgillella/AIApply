import asyncio
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Final

from browser_use import Agent, BrowserSession
from browser_use.browser import BrowserProfile
from browser_use.llm.openai.chat import ChatOpenAI
from browser_use.logging_config import setup_logging
from dotenv import load_dotenv


@dataclass(frozen=True)
class LinkedinCredentials:
    email: str
    password: str
    resume_path: str


LINKEDIN_DOMAIN: Final[str] = "https://www.linkedin.com"
LINKEDIN_JOBS_URL: Final[str] = (
    "https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer&f_TPR=r86400&f_AL=true"
)


def load_env() -> LinkedinCredentials:
    load_dotenv(dotenv_path=".env")
    missing: list[str] = []

    openai_key = os.getenv("OPENAI_API_KEY")
    email = os.getenv("LINKEDIN_LOGIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    resume_path = os.getenv("RESUME_PATH")

    if not openai_key:
        missing.append("OPENAI_API_KEY")
    if not email:
        missing.append("LINKEDIN_LOGIN_EMAIL")
    if not password:
        missing.append("LINKEDIN_PASSWORD")
    if not resume_path:
        missing.append("RESUME_PATH")

    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    return LinkedinCredentials(email=email, password=password, resume_path=resume_path)


def build_browser_session() -> BrowserSession:
    profile = BrowserProfile(
        headless=False,
        user_data_dir=os.path.join(os.getcwd(), "playwright-data"),
        wait_between_actions=0.3,
        highlight_elements=False,
    )
    return BrowserSession(browser_profile=profile, headless=False)


def build_prompt_extension() -> str:
    return """
<linkedin_workflow>
- Log in using the provided credentials only on official LinkedIn login forms.
- Prioritize the existing-account "Sign in" experience; do not click "Join now" or create-new-account flows.
- Navigate to the LinkedIn Jobs page filtered for AI Engineer roles posted in the last 24 hours.
- Apply the "Easy Apply" filter before reviewing listings.
- For each job card in the results list:
  1. Open job details in the same tab.
  2. Review the description briefly to ensure relevance to AI Engineering.
  3. Launch the Easy Apply flow if available; otherwise skip the job politely.
  4. Upload the provided resume when prompted.
  5. Answer application questions concisely using professional tone. If unsure, prefer truthful defaults such as "No" or "Not specified" rather than guessing.
  6. Deselect any optional "Follow" or "Follow company" checkboxes before continuing.
  7. Review the entire form, then submit once all sections are complete.
  8. After submission, log the job title and link in your notes and move on to the next unique listing without reopening completed applications.
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


async def main() -> None:
    setup_logging()
    creds = load_env()

    llm = ChatOpenAI(model="gpt-4o-mini")
    browser_session = build_browser_session()

    prompt_extension = build_prompt_extension()

    sensitive_data = build_sensitive_data(creds)

    agent = Agent(
        task=build_task(),
        llm=llm,
        browser_session=browser_session,
        sensitive_data=sensitive_data,
        extend_system_message=prompt_extension,
        directly_open_url=False,
        include_recent_events=True,
        available_file_paths=[creds.resume_path],
        initial_actions=[
            {
                "navigate": {
                    "url": LINKEDIN_JOBS_URL,
                    "new_tab": False,
                }
            }
        ],
    )

    run_started_at = datetime.now()

    history = await agent.run()
    usage_summary = await agent.token_cost_service.get_usage_summary(since=run_started_at)
    summary_path = os.path.join(os.getcwd(), "application-history.json")
    history.save_to_file(summary_path, sensitive_data=sensitive_data)
    print(f"Agent finished. History saved to {summary_path}")

    if usage_summary.entry_count:
        print(
            "Token usage summary: "
            f"prompt={usage_summary.total_prompt_tokens}, "
            f"cached_prompt={usage_summary.total_prompt_cached_tokens}, "
            f"completion={usage_summary.total_completion_tokens}, "
            f"total={usage_summary.total_tokens}"
        )
    else:
        print("Token usage summary: no model invocations recorded.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user")
