"""Entry point for running the LinkedIn job application agent."""

from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime

from browser_use.llm.openai.chat import ChatOpenAI
from browser_use.logging_config import setup_logging

from .agent_setup import (
    build_agent,
    build_browser_session,
    build_prompt_extension,
    build_sensitive_data,
    build_task,
)
from .config import LinkedinCredentials, load_env
from .resume_ocr import ResumeOCRError, ResumeContext, extract_resume_context


async def main(job_url: str) -> None:

    run_started_at = datetime.now()

    setup_logging()
    creds = load_env()

    try:
        resume_context: ResumeContext = extract_resume_context(
            mistral_api_key=creds.mistral_api_key,
            resume_path=creds.resume_path,
        )
    except ResumeOCRError as exc:
        raise RuntimeError(f"Resume OCR failed: {exc}") from exc

    print("=== Resume OCR Output ===")
    print(f"Pages processed: {resume_context.pages_processed}")
    print(f"Source file: {creds.resume_path}")
    print("-------------------------")
    print(resume_context.markdown or "[No text extracted]")
    print("=== End Resume OCR Output ===")

    llm = ChatOpenAI(model="gpt-4o-mini")
    browser_session = build_browser_session()

    prompt_extension = build_prompt_extension(job_url)
    if resume_context.markdown:
        prompt_extension = (
            f"{prompt_extension}\n<resume_context>\n{resume_context.markdown}\n</resume_context>"
        )

    sensitive_data = build_sensitive_data(creds)

    agent = build_agent(
        task=build_task(job_url),
        llm=llm,
        browser_session=browser_session,
        sensitive_data=sensitive_data,
        prompt_extension=prompt_extension,
        resume_path=creds.resume_path,
        job_url=job_url,
    )

    history = await agent.run()
    usage_summary = await agent.token_cost_service.get_usage_summary(since=run_started_at)
    summary_path = os.path.join(os.getcwd(), "application-history.json")
    history.save_to_file(summary_path, sensitive_data=sensitive_data)
    print(f"Agent finished. History saved to {summary_path}")

    if resume_context.pages_processed:
        ocr_cost = resume_context.pages_processed * 0.001
        print(
            "Mistral OCR usage: "
            f"pages_processed={resume_context.pages_processed}, "
            f"estimated_cost_usd={ocr_cost:.4f}"
        )

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
    parser = argparse.ArgumentParser(description="Apply to a specific LinkedIn job using the browser-use agent")
    parser.add_argument("job_url", help="LinkedIn job posting URL to apply to")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.job_url))
    except KeyboardInterrupt:
        print("Interrupted by user")
