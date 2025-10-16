"""Helpers for constructing the Browser Use agent with resume context."""

from __future__ import annotations

import os

from browser_use import Agent, BrowserSession
from browser_use.browser import BrowserProfile
from browser_use.llm.openai.chat import ChatOpenAI

from .config import AppConfig, CandidateProfile, LinkedinCredentials


def build_browser_session() -> BrowserSession:
    profile = BrowserProfile(
        headless=False,
        user_data_dir=os.path.join(os.getcwd(), "playwright-data"),
        wait_between_actions=0.3,
        highlight_elements=True,
    )
    return BrowserSession(browser_profile=profile, headless=False)


def build_prompt_extension(job_url: str, candidate: CandidateProfile) -> str:
    return f"""
<job_application_strategy>
- Navigate directly to the provided job application: {job_url}
- Capture job title, company, location, and the full job description for reference before filling the form.
- Use the job description and resume context to tailor every response, maximizing alignment with the employer's stated needs.
- You may extrapolate plausible achievements or project details to strengthen the candidacy; keep tone confident and professional.
- Stay on the active application page; do not refresh or switch away unless the form becomes unusable.
- Keep the application workflow open until every required field is completed and the final submit/finish button is pressed; document issues if they occur.
- Ignore navigation, sign-in, autofill, or download links that do not directly advance completion of the current application.
- If the platform indicates the role is already applied or no application form is available, log the finding and end the run gracefully.
</job_application_strategy>

<candidate_profile>
- Full name: {candidate.full_name}
- Email: {candidate.email}
- Phone: {candidate.phone}
- Requires sponsorship: {"Yes" if candidate.requires_sponsorship else "No"}
- Willing to relocate: {"Yes" if candidate.willing_to_relocate else "No"}
- Desired compensation: {candidate.desired_compensation}
- Default years of experience for any skill fields: {candidate.default_years_experience}
</candidate_profile>

<tailored_responses>
- Highlight AI/ML expertise, leadership, and measurable outcomes aligned with the job description.
- For open-ended questions, craft persuasive first-person answers mixing resume facts with new supporting examples.
- For project prompts, synthesize resume experience with scenario-specific details that resonate with the role.
- For multiple-choice items, select options that project capability, flexibility, and readiness unless restricted.
- Default compensation responses to 100000 USD annually unless the posting suggests a better target.
- For GPA bucket questions, choose "3.5 - 4.0" to reflect a 3.7 GPA.
</tailored_responses>

<sensitive_data_placeholders>
- Use <secret>linkedin_email</secret> for the LinkedIn login email.
- Use <secret>linkedin_password</secret> for the LinkedIn login password.
- Use <secret>resume_path</secret> when selecting the resume file to upload.
</sensitive_data_placeholders>

<education_preferences>
- When selecting school from dropdowns, first attempt "University of Texas at Dallas"; if unavailable, select "University of Texas at Austin".
- Use "Master of Science" (or closest variant) for degree and "Computer Science" for the discipline/major.
- Derive dates from the resume: for the master's program use start "August 2022" and end "May 2024"; for the bachelor's program use start "August 2018" and end "April 2022". Provide additional entries only if the form allows/requests them.
- Skip transcript uploads unless explicitly required with no bypass available.
</education_preferences>

<good_practices>
- Stay on trusted domains associated with the job application; verify URLs before entering credentials.
- Progress through the form methodically without closing dialogs prematurely.
- Resolve dropdowns, multi-selects, and validation prompts by choosing the best match for the candidate profile; leave no required field blank.
- Review each section for required indicators before moving to the next; do not click submit until all mandatory fields (including uploads and acknowledgements) are satisfied.
- Do not open or interact with links/buttons that do not advance the current form (e.g., alternate portals, document downloads, magic-link sign-ins).
- Capture summaries or confirmation numbers after submission when available.
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


