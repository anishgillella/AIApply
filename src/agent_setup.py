"""Helpers for constructing the Browser Use agent with resume context."""

from __future__ import annotations

import os

from browser_use import Agent, BrowserSession
from browser_use.browser import BrowserProfile
from browser_use.llm.openai.chat import ChatOpenAI

from .config import LinkedinCredentials


def build_browser_session() -> BrowserSession:
    profile = BrowserProfile(
        headless=False,
        user_data_dir=os.path.join(os.getcwd(), "playwright-data"),
        wait_between_actions=0.3,
        highlight_elements=True,
    )
    return BrowserSession(browser_profile=profile, headless=False)


def build_prompt_extension(job_url: str) -> str:
    return f"""
<job_application_strategy>
- Navigate directly to the provided job posting: {job_url}
- Before interacting with Easy Apply, capture job title, company, location, and the full job description for reference.
- Use the job description and resume context to tailor every response, maximizing alignment with the employer's stated needs.
- You may extrapolate plausible achievements or project details to strengthen the candidacy; keep tone confident and professional.
- Stay on the job tab; do not refresh the page unless it becomes unusable.
- Keep the Easy Apply modal open until the application is submitted or clearly blocked; document issues if they occur.
- If no Easy Apply option is available, log the finding and end the run gracefully.
</job_application_strategy>

<candidate_profile>
- Full name: Anish Gillella
- Email: **********
- Phone: **********
- Requires sponsorship: No
- Willing to relocate: Yes
- Desired compensation: 100000 USD annually (enter as digits when prompted)
- Default years of experience for any skill fields: 2
</candidate_profile>

<tailored_responses>
- Highlight AI/ML expertise, leadership, and measurable outcomes aligned with the job description.
- For open-ended questions, craft persuasive first-person answers mixing resume facts with new supporting examples.
- For project prompts, synthesize resume experience with scenario-specific details that resonate with the role.
- For multiple-choice items, select options that project capability, flexibility, and readiness unless restricted.
- Default compensation responses to 100000 USD annually unless the posting suggests a better target.
</tailored_responses>

<sensitive_data_placeholders>
- Use <secret>linkedin_email</secret> for the LinkedIn login email.
- Use <secret>linkedin_password</secret> for the LinkedIn login password.
- Use <secret>resume_path</secret> when selecting the resume file to upload.
</sensitive_data_placeholders>

<good_practices>
- Stay on trusted LinkedIn-owned domains when possible; verify URLs before entering credentials.
- Progress through Easy Apply methodically without closing dialogs prematurely.
- Deselect optional "Follow" or "Follow company" checkboxes before submitting.
- Log final status and any blockers in notes.
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


def build_task(job_url: str) -> str:
    return (
        "Open the provided LinkedIn job posting and submit a tailored Easy Apply application that maximizes the "
        "candidate's chances of receiving an offer. Job URL: "
        f"{job_url}"
    )


def build_agent(
    task: str,
    llm: ChatOpenAI,
    browser_session: BrowserSession,
    sensitive_data: dict[str, dict[str, str]],
    prompt_extension: str,
    resume_path: str,
    job_url: str,
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
                    "url": job_url,
                    "new_tab": False,
                }
            }
        ],
    )


