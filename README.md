# AI-Powered Job Application Automation

An intelligent job application system that automatically fills out job application forms using Stagehand's agent-based automation and your resume information.

## 🎯 Project Overview

This project uses Stagehand's AI agent to intelligently fill out job application forms with **zero hardcoded question templates**. Unlike traditional form-fillers that rely on predetermined field mappings, this system:

### 🌟 Key Innovation: Dynamic Question Extraction & Generation

**The agent doesn't know what questions it will encounter.** Instead, for each job application:

1. **Discovers** all questions on the form (extracts field labels, types, constraints)
2. **Categorizes** each question (static data vs. selection vs. open-ended)
3. **Generates** custom answers tailored to THIS specific job:
   - Static fields (name, email) → Retrieved from your profile
   - Selection fields (dropdowns, checkboxes) → Intelligently selected based on your data
   - Open-ended questions (why this company?) → **Dynamically generated** using:
     - Job description analysis
     - Resume-to-job alignment scoring
     - LLM-powered custom answer generation
     - Specific examples from your most relevant experiences

4. **Detects pre-filled fields** and skips them automatically
5. **Adapts** to any form structure across different platforms

**Result**: Every screening question gets a personalized, job-specific answer that references your actual experience and aligns with the company's needs.

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 30 minutes
- **[Phase 1: Foundation](PHASE_1_FOUNDATION.md)** - Resume parsing & setup
- **[Phase 2: Job Intelligence](PHASE_2_JOB_INTELLIGENCE.md)** - Job analysis & answer generation
- **[Phase 3: Form Automation](PHASE_3_FORM_AUTOMATION.md)** - Dynamic question discovery & filling
- **[Phase 4: Polish & Safety](PHASE_4_POLISH_SAFETY.md)** - Production-ready features
- **[Project Structure](PROJECT_STRUCTURE.md)** - Complete file organization

---

## 🏗️ Architecture

### Core Components

1. **Resume Parser & Profile Builder**
   - Extracts structured information from your resume PDF using OCR/PyMuPDF
   - Creates a canonical data model (`profile_data.json`) with:
     - Personal information (name, email, phone, location, links)
     - Work experience (companies, titles, dates, descriptions, achievements)
     - Education (degrees, institutions, dates, GPAs)
     - Skills (technical stack, tools, frameworks)
     - Projects and notable work
   - **One-time setup**: This data remains constant across all applications

2. **Job Intelligence Engine** 🧠 (NEW - Dynamic Content Generation)
   - **Scrapes job description** from the application URL using Stagehand
   - **Extracts structured job data**:
     ```json
     {
       "company": "Company Name",
       "role": "Role Title",
       "required_skills": ["Python", "LLMs", "Docker"],
       "preferred_skills": ["AWS", "React"],
       "responsibilities": ["Build X", "Design Y", "Lead Z"],
       "company_values": ["Innovation", "Collaboration"],
       "benefits": ["Remote work", "Equity"],
       "description_raw": "Full job posting text..."
     }
     ```
   - **Performs Resume-to-Job Matching**:
     - Uses LLM to analyze alignment between your experience and job requirements
     - Calculates match scores for each past role, skill, and project
     - Identifies your top 2-3 most relevant experiences for this specific job
   - **Generates Custom Screening Answers** using LLM:
     - "Why this company?" → Researches company + references your aligned experience
     - "Why this role?" → Connects job responsibilities to your specific achievements
     - "Tell us about yourself" → Crafts 2-3 paragraph bio highlighting relevant work
     - Cover letter → Full personalized letter with job-specific examples
   - **Character/Word Limit Awareness**: Truncates answers to fit field constraints

3. **Dynamic Question Extractor & Answer Generator**
   - **Discovers all questions** on the form by extracting field labels, placeholders, and context
   - **Categorizes questions** by type:
     - Static fields (name, email, phone) → Direct mapping from `profile_data`
     - Dropdown selections (experience level, education) → Intelligent selection from `profile_data`
     - Open-ended questions (why interested, tell us about yourself) → Generate custom answer using LLM
     - Screening questions (describe a project, leadership experience) → Generate from resume + job context
   - **For each discovered question**, generates an appropriate answer:
     - Extracts question text, character limit, field type
     - Determines answer source (profile_data vs. generated content)
     - Generates answer if needed using job context + resume alignment
   - **No predetermined question list** - adapts to whatever questions the form asks

4. **Stagehand Agent** (Form Automation)
   - Navigates to application page and discovers form structure
   - Detects pre-filled fields and skips them
   - For each empty field, determines appropriate answer and fills it
   - Handles all field types intelligently
   - Manages multi-page forms and navigation
   - Validates entries before proceeding

5. **Smart Field Mapping**
   - Fuzzy matching for field labels (e.g., "First Name" = "Given Name" = "Name (First)")
   - Context-aware understanding (e.g., "Name" next to "Email" likely means full name)
   - Validates data format (email validation, phone formatting)
   - Respects character/word limits and truncates intelligently

### How It Works - End-to-End Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    ONE-TIME SETUP                                │
│                                                                  │
│  ┌─────────────┐          ┌─────────────────┐                  │
│  │ Resume PDF  │  ───────>│ Extract Data    │                  │
│  │             │          │ (PyMuPDF/OCR)   │                  │
│  └─────────────┘          └────────┬────────┘                  │
│                                    │                            │
│                                    ▼                            │
│                          ┌──────────────────┐                  │
│                          │ profile_data.json│                  │
│                          │  (Your Info)     │                  │
│                          └──────────────────┘                  │
└──────────────────────────────────────────────────────────────────┘

                                   │
                                   ▼

┌──────────────────────────────────────────────────────────────────┐
│               PER-APPLICATION WORKFLOW                           │
│                                                                  │
│  Input: Job Application URL                                     │
│         ↓                                                        │
│  ┌─────────────────────────────┐                               │
│  │  Job Intelligence Engine    │                               │
│  │  ────────────────────────    │                               │
│  │  1. Scrape job description  │                               │
│  │  2. Extract job requirements│                               │
│  │  3. Match resume to job     │                               │
│  │  4. Generate custom answers │                               │
│  └──────────┬──────────────────┘                               │
│             │                                                    │
│             ▼                                                    │
│  ┌───────────────────────────────┐                             │
│  │  generated_content.json       │                             │
│  │  ───────────────────────       │                             │
│  │  - why_company               │                             │
│  │  - why_role                  │                             │
│  │  - cover_letter              │                             │
│  │  - custom_answers            │                             │
│  │  - match_score: 0.92         │                             │
│  └──────────┬────────────────────┘                             │
│             │                                                    │
│             ▼                                                    │
│  ┌───────────────────────────────┐                             │
│  │   Stagehand Agent             │                             │
│  │   ─────────────────            │                             │
│  │   Inputs:                     │                             │
│  │   • profile_data.json         │                             │
│  │   • generated_content.json    │                             │
│  │   • Job application URL       │                             │
│  │                               │                             │
│  │   Actions:                    │                             │
│  │   1. Navigate to form         │                             │
│  │   2. Extract field info       │                             │
│  │   3. Detect pre-filled fields │                             │
│  │   4. Map fields to data       │                             │
│  │   5. Fill empty fields only   │                             │
│  │   6. Handle multi-page forms  │                             │
│  └──────────┬────────────────────┘                             │
│             │                                                    │
│             ▼                                                    │
│  ┌───────────────────────────────┐                             │
│  │  Review & Submit              │                             │
│  │  ───────────────               │                             │
│  │  • Pause for user review      │                             │
│  │  • Show filled fields         │                             │
│  │  • Allow edits                │                             │
│  │  • Submit on approval         │                             │
│  └───────────────────────────────┘                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+ (for Stagehand)
- OpenAI API key (for Stagehand's AI agent)

### Installation

1. **Clone and setup Python environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

2. **Install Stagehand**
```bash
# Install Stagehand via npm/npx or use their Python bindings
npm install @browserbasehq/stagehand
```

3. **Configure environment variables**
```bash
# Create .env file
cp .env.example .env

# Add your API keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here  # Optional, for Claude models
```

### Configuration

Create a `resume_data.json` file with your structured information:

```json
{
  "personal": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "phone": "+1 (123) 456-7890",
    "location": "City, State",
    "linkedin": "https://linkedin.com/in/yourprofile",
    "github": "https://github.com/yourusername",
    "portfolio": "https://yourportfolio.com"
  },
  "experience": [
    {
      "company": "Company Name",
      "title": "Your Title",
      "start_date": "Jan 2020",
      "end_date": "Present",
      "description": "What you did and achieved",
      "technologies": ["Python", "React", "AWS"]
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "degree": "Bachelor of Science in Computer Science",
      "graduation_date": "May 2020",
      "gpa": "3.8/4.0"
    }
  ],
  "skills": {
    "technical": ["Python", "JavaScript", "React", "Node.js"],
    "soft": ["Leadership", "Communication", "Problem Solving"]
  },
  "projects": [
    {
      "name": "Project Name",
      "description": "Brief description",
      "link": "https://github.com/...",
      "technologies": ["React", "Node.js"]
    }
  ]
}
```

## 💡 Key Features

### 1. Dynamic Question Discovery

The agent extracts all questions from the form by analyzing:
- Field labels (e.g., "First Name", "Why do you want to work here?")
- Placeholders (e.g., "Enter your email address")
- Help text and context around fields
- Field types (text input, textarea, dropdown, checkbox, file upload, date picker)
- Character/word limits
- Required vs. optional indicators

### 2. Question Categorization & Answer Strategy

For each discovered question, the agent determines the answer strategy:

**Static Data Questions** (Direct mapping from profile):
- Name, email, phone, location → Extract from `profile_data.personal`
- Work authorization, sponsorship → Extract from `profile_data.work_authorization`
- Education, GPA, graduation date → Extract from `profile_data.education`
- Compensation expectations → Extract from `profile_data.compensation`

**Selection Questions** (Intelligent choice from options):
- "Years of experience" dropdown → Calculate from `profile_data.experience_years`
- "Education level" dropdown → Select based on `profile_data.education`
- "Proficiency in X" dropdown → Analyze resume to determine level (Beginner/Expert)
- Work preferences (remote/hybrid/onsite) → Select from `profile_data.work_preferences`

**Open-Ended Questions** (LLM-generated, job-specific):
- "Why do you want to work here?" → Generate using company + job context + resume alignment
- "Why are you interested in this role?" → Generate using role requirements + relevant experience
- "Tell us about yourself" → Generate bio highlighting experiences relevant to this job
- "Describe a challenging project" → Select most relevant project from resume based on job needs
- "What are your career goals?" → Generate answer aligned with role trajectory

**Boolean Questions** (Yes/No or checkboxes):
- "Are you authorized to work in the US?" → Map to `profile_data.work_authorization.legally_authorized`
- "Willing to relocate?" → Map to `profile_data.work_preferences.willing_to_relocate`
- Skill checkboxes → Check skills that appear in both resume AND job description (prioritize job-required skills)

### 3. Pre-filled Field Detection

Before answering any question, the agent:
1. Checks if the field already contains data (from resume parsing or browser autofill)
2. If pre-filled → Skip and move to next field
3. If empty → Generate/retrieve appropriate answer and fill it
4. Logs all skipped fields for transparency

### 4. Field Type Handling Examples

The agent intelligently handles different field types by understanding context and generating appropriate answers:

#### Text Inputs
- **"First Name"** → Extract "Anish" from profile
- **"Email Address"** → Use anishgillella@gmail.com from profile
- **"LinkedIn URL"** → Use https://www.linkedin.com/in/anishgillella/ from profile

#### Text Areas (Dynamic Content)
- **"Why do you want to work here?"** → Generate custom answer using:
  - Company name and values from job description
  - Your aligned experiences (e.g., Theus LLM work for AI companies)
  - 2-3 sentences, respecting character limit
- **"Tell us about yourself"** → Generate bio highlighting:
  - Most relevant 2-3 roles based on job requirements
  - Key achievements that match job needs
  - Professional summary tailored to this position

#### Dropdowns (Intelligent Selection)
- **"Years of Experience"** [0-1, 1-3, 3-5, 5-10] → Calculate from profile (2.5 years → "1-3")
- **"Highest Education"** [HS, Bachelor's, Master's, PhD] → Select "Master's"
- **"Python Proficiency"** [Beginner, Intermediate, Advanced, Expert] → Analyze resume: 4 years + multiple projects → "Expert"
- **"Work Authorization"** [Citizen, Permanent Resident, Work Visa, etc.] → Select "Authorized to work" (no sponsorship needed)

#### Checkboxes & Boolean Fields
- **"Are you authorized to work in the US?"** → Check (true in profile)
- **"Do you require sponsorship?"** → Leave unchecked (false in profile)
- **"Willing to relocate?"** → Check (true in profile)
- **"Willing to travel?"** → Check (50% in profile)

#### Multi-Select Skill Checkboxes (Job-Aligned)
When form shows: "Select all languages you know: [ ] Python [ ] JavaScript [ ] Java [ ] C++ [ ] Ruby"
- Agent identifies: Your skills = [Python, TypeScript, SQL]
- Agent identifies: Job requires = [Python, JavaScript]
- **Decision**: Check Python (in both), Check JavaScript (required by job, general enough skill)
- **Strategy**: Prioritize skills mentioned in job description, check skills from resume that match

#### File Uploads
- **"Upload Resume"** → Upload "Dev Resume-2.pdf"
- **"Cover Letter (Optional)"** → Generate custom cover letter as text, convert to PDF, upload

#### Date Pickers
- **"Graduation Date"** → Extract "May 2024" from education → Select 05/2024
- **"Earliest Start Date"** → Profile says "Immediately" → Select today's date or "Immediately" option

#### Numeric/Salary Fields
- **"Desired Salary"** → Enter 150000 (from profile)
- **"Salary Currency"** → Select USD

#### Reference Fields
- When references are required → Notify user to manually enter (or use pre-configured references if available)
- Pause application for user to provide reference information

## 🎯 Usage

### Basic Usage

```python
from job_app_filler import JobApplicationFiller

# Initialize the filler
filler = JobApplicationFiller(
    resume_data_path="resume_data.json",
    resume_pdf_path="Dev Resume-2.pdf"
)

# Navigate to job application page
application_url = "https://company.com/careers/apply/job-id"

# Fill the application
result = filler.fill_application(
    url=application_url,
    submit=False,  # Set to True to auto-submit
    review_before_submit=True  # Pause before submission for review
)

print(f"Application filled: {result['success']}")
print(f"Fields filled: {result['filled_fields']}")
print(f"Fields skipped: {result['skipped_fields']}")
```

### Advanced Usage: Multi-page Forms

```python
# For multi-step applications
result = filler.fill_multi_step_application(
    url=application_url,
    max_steps=5,  # Maximum number of pages to fill
    pause_between_steps=2  # Seconds to wait between pages
)
```

### Batch Processing

```python
# Apply to multiple jobs
job_urls = [
    "https://company1.com/apply/123",
    "https://company2.com/apply/456",
    "https://company3.com/apply/789"
]

results = filler.batch_fill(
    urls=job_urls,
    submit=False,
    delay_between_apps=30  # Seconds between applications
)
```

## 🧠 Dynamic Question Extraction & Answer Generation

### The Agent's Workflow

For each job application, the agent follows this adaptive workflow:

1. **Extract All Questions**: Scan the entire form and extract every question/field
2. **Categorize Each Question**: Determine if it's static data, selection, or open-ended
3. **Generate Answers**: For each question, either retrieve from profile or generate custom response
4. **Fill & Validate**: Enter answers, respecting character limits and field constraints

### Real-World Example: Anthropic ML Engineer Application

**Discovered Questions** (Agent extracts these from the form):

| Question | Type | Answer Strategy |
|----------|------|-----------------|
| "Full Name" | Text input | Retrieve: `profile_data.personal.name` → "Anish Gillella" |
| "Email" | Text input | Retrieve: `profile_data.personal.email` → "anishgillella@gmail.com" |
| "Years of ML experience" | Dropdown | Calculate: `profile_data.experience_years.ai_ml` → Select "2-3 years" |
| "Why Anthropic?" | Text area (500 chars) | **Generate**: LLM creates answer using job context + resume<br/>→ "I'm drawn to Anthropic's focus on AI safety. At Theus, I built LLM pipelines and fine-tuned models, which aligns with your research on responsible AI development..." |
| "Describe a relevant project" | Text area (1000 chars) | **Generate**: LLM selects most relevant project from resume<br/>→ Describes Theus data pipeline project (10K+ sources, GPT-5, $500K seed raise) |
| "Proficient in Python?" | Checkbox | Retrieve: Check resume skills → Yes (4 years experience) |
| "Upload Resume" | File upload | Upload: "Dev Resume-2.pdf" |

**Key Insight**: The agent doesn't have a hardcoded list of questions to answer. Instead:
- It **discovers** whatever questions the form asks
- It **categorizes** each question to determine the best answer source
- It **generates** custom answers for open-ended questions based on THIS specific job

### Example: Unexpected Question Handling

If a form asks: **"What excites you most about working on Constitutional AI?"**

**Agent's Process**:
1. **Discovery**: Extracts question text and recognizes it's an open-ended question about a specific topic
2. **Categorization**: Not in profile → Needs LLM generation
3. **Context Building**: 
   - Job is at Anthropic (from job description)
   - Constitutional AI is Anthropic's research area
   - User has LLM experience at Theus and AIRRIVED
4. **Answer Generation**: 
   ```
   LLM Prompt: "Answer this application question using the candidate's background:
   Question: 'What excites you most about working on Constitutional AI?'
   Candidate Experience: [Theus LLM work, AIRRIVED AI safety...]
   Company: Anthropic
   Character Limit: 500"
   
   Generated Answer: "The opportunity to work on Constitutional AI excites me 
   because it addresses the critical challenge of AI alignment. At Theus, I worked 
   on training and distilling LLM models, and saw firsthand the importance of 
   building systems that are both powerful and aligned with human values..."
   ```

This approach handles **ANY** question, even ones not anticipated in advance.

## 🔒 Safety Features

- **No Auto-Submit by Default**: Review applications before submission
- **Logging**: All actions are logged for debugging and verification
- **Screenshots**: Captures screenshots before/after filling
- **Dry Run Mode**: Test field mapping without actually filling
- **Rollback**: Can clear filled data if needed

## 📋 Implementation Roadmap

The development is organized into 4 phases, each with detailed step-by-step instructions:

### [Phase 1: Foundation](PHASE_1_FOUNDATION.md) (Week 1) 🔴
Set up the basic infrastructure:
- Parse resume into structured `profile_data.json`
- Create static profile configuration
- Set up Stagehand browser automation
- Validate end-to-end flow

**[📖 View detailed Phase 1 guide →](PHASE_1_FOUNDATION.md)**

---

### [Phase 2: Job Intelligence Engine](PHASE_2_JOB_INTELLIGENCE.md) (Week 2) 🔴
Build the AI-powered job analysis system:
- Scrape job descriptions from any URL
- Extract structured job requirements using LLM
- Calculate resume-to-job alignment scores
- Generate custom screening answers for each job
- Dynamic answer generator for ANY question

**[📖 View detailed Phase 2 guide →](PHASE_2_JOB_INTELLIGENCE.md)**

---

### [Phase 3: Form Automation](PHASE_3_FORM_AUTOMATION.md) (Week 3) 🔴
Build the dynamic question discovery and form filling:
- Discover ALL questions on any form (no hardcoded list)
- Categorize questions (static/selection/open-ended)
- Generate appropriate answers for each discovered question
- Fill forms intelligently, skipping pre-filled fields
- Handle multi-page applications

**[📖 View detailed Phase 3 guide →](PHASE_3_FORM_AUTOMATION.md)**

---

### [Phase 4: Polish & Safety](PHASE_4_POLISH_SAFETY.md) (Week 4) 🔴
Production-ready features:
- Comprehensive logging and debugging
- Error handling and retry logic
- Safety features (dry-run, review, rollback)
- Platform testing (LinkedIn, Greenhouse, Workday)
- Analytics and reporting
- CLI improvements

**[📖 View detailed Phase 4 guide →](PHASE_4_POLISH_SAFETY.md)**

---

### Future Enhancements 🔮
- Batch processing multiple jobs
- Application status tracking
- Visual analytics dashboard
- Platform-specific templates
- A/B testing different strategies
- Reference management automation

---

## 🚀 Quick Start

```bash
# Phase 1: Setup
python src/resume_parser.py --input "Dev Resume-2.pdf"
node src/test_stagehand.js

# Phase 2: Test job intelligence
node src/test_job_intelligence.js "https://example.com/job"

# Phase 3: Fill an application
node src/apply.js "https://example.com/job"

# Phase 4: Check stats
node src/cli.js stats
```

Each phase builds on the previous one. **Start with Phase 1** and work through sequentially.

**📁 [View complete project structure →](PROJECT_STRUCTURE.md)**

## 🛠️ Technology Stack

- **Stagehand**: AI-powered browser automation with agent reasoning
- **Python**: Backend logic and data processing
- **PyMuPDF/OCR**: Resume parsing and extraction
- **Playwright**: Browser automation (underlying Stagehand)
- **OpenAI/Anthropic**: LLM for intelligent decision-making and content generation
- **TypeScript/Node.js**: Stagehand integration layer

## 🤖 LLM-Powered Content Generation

### How Dynamic Answers Are Generated

The Job Intelligence Engine uses a multi-step LLM workflow to create personalized answers:

#### Step 1: Job Description Analysis

```python
# Prompt to LLM
analyze_job_prompt = f"""
Analyze this job posting and extract structured information:

Job Posting:
{job_description_text}

Extract:
1. Company name
2. Role/position title
3. Required skills (technical)
4. Preferred skills (nice-to-have)
5. Key responsibilities
6. Company values/culture keywords
7. Education requirements
8. Experience level required

Return as JSON.
"""

job_data = llm.extract(analyze_job_prompt)
# → {company: "Anthropic", role: "ML Engineer", required_skills: [...], ...}
```

#### Step 2: Resume-to-Job Matching

```python
# Prompt to LLM
matching_prompt = f"""
Given this candidate's resume and job requirements, identify alignment:

Resume:
{resume_text}

Job Requirements:
{job_data}

For each of the candidate's experiences, rate relevance to this job (0-10).
Identify the top 3 most relevant experiences.
Calculate overall match score (0-1).
List matched skills and missing skills.

Return as JSON.
"""

match_analysis = llm.analyze(matching_prompt)
# → {
#     top_experiences: ["Theus (0.95)", "AIRRIVED (0.88)", "Cohezion (0.72)"],
#     matched_skills: ["Python", "LLMs", "RAG"],
#     missing_skills: ["Rust"],
#     match_score: 0.89
#   }
```

#### Step 3: Generate Custom "Why This Company?"

```python
# Prompt to LLM
why_company_prompt = f"""
Write a compelling 2-3 sentence answer to "Why do you want to work at {company}?"

Context:
- Candidate background: {resume_summary}
- Top relevant experiences: {match_analysis.top_experiences}
- Company: {company}
- Company values: {job_data.company_values}
- Role: {role}

Guidelines:
- Be authentic and specific
- Reference the candidate's actual experience that aligns with the company
- Mention specific company products/values/mission if known
- Maximum 500 characters
- First person voice

Answer:
"""

why_company = llm.generate(why_company_prompt)
# → "I'm particularly drawn to Anthropic's commitment to AI safety and 
#     responsible AI development. My experience at Theus building LLM 
#     pipelines with GPT-5 and fine-tuning models aligns closely with 
#     your focus on advanced language model research..."
```

#### Step 4: Generate Custom "Why This Role?"

```python
# Prompt to LLM
why_role_prompt = f"""
Write a compelling 2-3 sentence answer to "Why are you interested in this {role} role?"

Context:
- Candidate background: {resume_summary}
- Top relevant experiences: {match_analysis.top_experiences}
- Role responsibilities: {job_data.responsibilities}
- Required skills: {job_data.required_skills}

Guidelines:
- Connect specific experiences to role requirements
- Highlight matched skills
- Show enthusiasm for the work
- Maximum 500 characters
- First person voice

Answer:
"""

why_role = llm.generate(why_role_prompt)
# → "This role perfectly matches my background in AI research and engineering. 
#     At Theus, I developed data pipelines processing 10K+ sources and trained 
#     models on H100 GPUs. My work with RAG systems at AIRRIVED demonstrates 
#     my ability to scale AI systems for production..."
```

#### Step 5: Generate Cover Letter

```python
# Prompt to LLM
cover_letter_prompt = f"""
Write a professional cover letter for this application:

Candidate: Anish Gillella
Company: {company}
Role: {role}
Job Description: {job_description}
Resume: {resume_text}
Top 3 Relevant Experiences: {match_analysis.top_experiences}
Matched Skills: {match_analysis.matched_skills}

Structure:
1. Opening: Express interest in the role
2. Paragraph 1: Highlight most relevant experience (Theus or AIRRIVED)
3. Paragraph 2: Connect skills to job requirements
4. Paragraph 3: Show enthusiasm and cultural fit
5. Closing: Express desire for interview

Guidelines:
- Professional but conversational tone
- Use specific metrics and achievements from resume
- Reference actual projects/work that align with job
- Maximum 2500 characters
- Avoid clichés

Cover Letter:
"""

cover_letter = llm.generate(cover_letter_prompt)
```

### Field-Specific Answer Generation

For other screening questions, use dynamic templates:

```python
def generate_field_answer(field_label, field_context, char_limit):
    """
    Dynamically generate answer for any screening question
    """
    prompt = f"""
    Answer this job application question:
    
    Question: {field_label}
    Context: {field_context}
    
    Candidate Info:
    - Resume: {resume_text}
    - Job: {job_data}
    - Top Experiences: {match_analysis.top_experiences}
    
    Write a {char_limit}-character answer that:
    1. Is specific to the candidate's experience
    2. Aligns with the job requirements
    3. Is authentic and professional
    
    Answer:
    """
    
    answer = llm.generate(prompt)
    return truncate(answer, char_limit)

# Examples:
# "Tell us about a challenging project" → Selects most relevant project from resume
# "What are your salary expectations?" → Uses profile_data.compensation.desired_salary
# "What is your leadership experience?" → Pulls leadership examples from resume
```

### Caching Strategy

To reduce costs and latency:

```python
# Cache generated content per job
cache_key = f"{company}_{role}_{hash(job_description)}"

if cache_exists(cache_key):
    generated_content = load_from_cache(cache_key)
else:
    generated_content = generate_all_answers(job_data, resume_data)
    save_to_cache(cache_key, generated_content)
```

### Character Limit Handling

```python
def smart_truncate(text, limit):
    """
    Truncate while preserving complete sentences
    """
    if len(text) <= limit:
        return text
    
    # Try to end at sentence boundary
    truncated = text[:limit]
    last_period = truncated.rfind('.')
    
    if last_period > limit * 0.7:  # If we can preserve 70%+ content
        return truncated[:last_period + 1]
    else:
        return truncated[:limit-3] + "..."
```

## ⚠️ Important Considerations

### Ethical Use
- **Transparency**: Only use for legitimate job applications
- **Accuracy**: Ensure all information is truthful and from your resume
- **Terms of Service**: Respect website ToS regarding automation
- **Rate Limiting**: Don't spam applications

### Limitations
- Some applications use CAPTCHAs or bot detection
- Complex custom forms may require manual intervention
- File upload fields may need special handling
- Some sites may block automation

## 👤 Your Application Profile

### Fixed Information (Always the same)

```json
{
  "personal": {
    "name": "Anish Gillella",
    "email": "anishgillella@gmail.com",
    "phone": "469-867-4545",
    "location": "San Francisco, California, United States",
    "linkedin": "https://www.linkedin.com/in/anishgillella/",
    "github": "https://github.com/anishgillella",
    "pronouns": "He/Him"
  },
  "work_authorization": {
    "legally_authorized": true,
    "requires_sponsorship": false,
    "willing_background_check": true,
    "citizenship_status": "Authorized to work in the US"
  },
  "work_preferences": {
    "location_preference": "No preference (Remote/Hybrid/On-site)",
    "willing_to_relocate": true,
    "willing_to_travel": "Yes, up to 50%",
    "start_date": "Immediately",
    "currently_employed": true
  },
  "compensation": {
    "desired_salary": 150000,
    "currency": "USD"
  },
  "demographics": {
    "gender": "Male",
    "race_ethnicity": "Asian",
    "hispanic_latino": false,
    "veteran_status": "Not a veteran",
    "disability_status": "No disability"
  },
  "education": [
    {
      "institution": "University of Texas at Dallas",
      "degree": "Master of Science in Computer Science",
      "graduation_date": "May 2024",
      "gpa": "3.7/4.0"
    },
    {
      "institution": "Manipal Institute of Technology",
      "degree": "Bachelor of Science in Computer Science",
      "graduation_date": "April 2022",
      "gpa": "3.6/4.0"
    }
  ],
  "experience_years": {
    "total_professional": 2.5,
    "ai_ml": 2.5,
    "python": 4,
    "typescript": 2
  }
}
```

### Dynamic Information (Generated per job)

**🎯 INTELLIGENT APPROACH**: Instead of hardcoded screening answers, the agent will:

1. **Extract & Analyze Job Description**
   - Parse the job posting from the provided URL
   - Extract: Company name, role title, key requirements, preferred skills, company values
   - Identify: Must-have vs nice-to-have qualifications

2. **Resume-to-Job Alignment**
   - Map your resume experience to job requirements
   - Identify strongest matches (e.g., if job needs "LLM experience" → highlight Theus/AIRRIVED work)
   - Calculate relevance scores for each experience/skill

3. **Generate Tailored Responses**
   - Use LLM to craft custom answers based on the specific job
   - Examples:
     - **"Why do you want to work at [Company]?"** → Research company, mention specific products/values that align with your background
     - **"Why this role?"** → Connect job requirements with your specific experience (e.g., "I see you need someone with RAG pipeline experience—at Theus, I built...")
     - **Cover letter** → Dynamically generated, highlighting most relevant 2-3 experiences from your resume that match the job

4. **Adaptive Field Filling**
   - For "relevant experience" fields → Pick the most applicable job from your resume
   - For "key skills" checkboxes → Prioritize skills mentioned in the job description
   - For "Why are you a good fit?" → Generate custom response showing alignment

### How This Works in Practice

```python
# High-level workflow
job_url = "https://company.com/careers/apply/ml-engineer"

# Step 1: Extract job description from the page
job_data = extract_job_description(job_url)
# → {company: "Anthropic", role: "ML Engineer", requirements: [...], ...}

# Step 2: Analyze alignment between resume and job
alignment = analyze_resume_job_match(resume_data, job_data)
# → {matched_skills: ["Python", "LLM", "RAG"], 
#     relevant_experiences: ["Theus", "AIRRIVED"], 
#     match_score: 0.89}

# Step 3: Discover all questions on the form
form_questions = discover_form_questions(job_url)
# → [
#     {label: "Full Name", type: "text", required: true, prefilled: false},
#     {label: "Why Anthropic?", type: "textarea", char_limit: 500, prefilled: false},
#     {label: "Years of experience", type: "dropdown", options: ["0-1", "1-3", ...]}
#   ]

# Step 4: For each question, generate appropriate answer
answers = {}
for question in form_questions:
    if question.prefilled:
        continue  # Skip pre-filled fields
    
    # Categorize and generate answer
    if is_static_field(question):
        answers[question.label] = get_from_profile(question)
    elif is_selection_field(question):
        answers[question.label] = select_best_option(question, profile_data)
    else:  # Open-ended question
        answers[question.label] = generate_answer_with_llm(
            question=question,
            job_context=job_data,
            resume=resume_data,
            alignment=alignment
        )

# Step 5: Fill application with generated answers
fill_application(job_url, answers)
```

### Benefits of This Approach

✅ **Personalized**: Each application is tailored to the specific company and role  
✅ **Authentic**: Responses reference real experiences from your resume  
✅ **Competitive**: Shows genuine interest and research  
✅ **Scalable**: Works for any job without manual customization  
✅ **Smart**: Highlights most relevant experiences for each role

## 📝 Example Workflow

```bash
# 1. One-time setup: Extract and structure resume data
python setup.py --resume "Dev Resume-2.pdf" --profile profile_data.json

# 2. Apply to a job (with dynamic answer generation)
python apply.py --url "https://openai.com/careers/ml-engineer"

# What happens under the hood:
# ✓ Scrapes job description from the page
# ✓ Extracts: OpenAI, ML Engineer role, requirements (Python, LLMs, etc.)
# ✓ Matches your Theus/AIRRIVED experience to job requirements
# ✓ Generates custom "Why OpenAI?" answer mentioning their LLM work
# ✓ Creates tailored cover letter highlighting relevant projects
# ✓ Fills all form fields intelligently
# ✓ Detects pre-filled fields and skips them
# ✓ Pauses for your review before submission

# 3. Review the filled form
# [Browser stays open - you can see all filled fields]

# 4. Approve or edit
# [Type 'submit' to proceed, 'edit' to modify, or 'cancel' to abort]

# 5. View detailed logs
cat logs/openai_ml_engineer_2025_10_16.json
# Shows: fields filled, answers generated, match score, time taken
```

### Real Example Output

```json
{
  "job": {
    "company": "Anthropic",
    "role": "AI Research Engineer",
    "url": "https://anthropic.com/careers/...",
    "requirements": ["LLM experience", "RAG systems", "Python", "PyTorch"],
    "match_score": 0.92
  },
  "generated_content": {
    "why_company": "I'm particularly drawn to Anthropic's commitment to AI safety and responsible AI development. My experience at Theus building LLM pipelines with GPT-5 and fine-tuning models aligns closely with your focus on advanced language model research. The work you're doing on Constitutional AI resonates with my belief that AI systems should be both powerful and aligned with human values.",
    
    "why_role": "This role perfectly matches my background in AI research and engineering. At Theus, I developed data pipelines processing 10K+ sources and trained models on H100 GPUs, improving retrieval semantics by 35%. My work with RAG systems at AIRRIVED, where I reduced latency from 45s to 12s, demonstrates my ability to scale AI systems for production. I'm excited to bring this experience to Anthropic's cutting-edge research.",
    
    "cover_letter": "Dear Anthropic Hiring Team,\n\nI'm writing to express my strong interest in the AI Research Engineer position. As a Founding AI Engineer with 2.5 years of hands-on experience building LLM systems, RAG pipelines, and agentic workflows, I'm excited about the opportunity to contribute to Anthropic's mission of AI safety...\n\n[Full letter generated with specific examples from resume matched to job requirements]"
  },
  "fields_filled": {
    "name": "Anish Gillella",
    "email": "anishgillella@gmail.com",
    "phone": "469-867-4545",
    "linkedin": "https://www.linkedin.com/in/anishgillella/",
    "location": "San Francisco, California",
    "years_experience": "2-3 years",
    "python_proficiency": "Expert",
    "llm_experience": "Yes",
    "why_interested": "[Generated custom answer]",
    "resume_uploaded": true,
    "cover_letter": "[Generated custom letter]"
  },
  "fields_skipped": ["city", "state"],
  "reason_skipped": "Already pre-filled from resume parsing",
  "application_status": "Ready for review",
  "timestamp": "2025-10-16T14:30:00Z"
}
```

## 📝 Implementation Notes

This README outlines the **architecture and conceptual approach** for the job application automation system. The actual implementation will:

- Use Stagehand's agent capabilities for browser automation (specific method calls handled in code)
- Implement the dynamic question discovery and categorization logic
- Build the LLM-powered answer generation pipeline
- Handle all edge cases and platform-specific quirks

**Focus**: The system is designed to be **adaptive and question-agnostic**, discovering and answering whatever questions each specific form presents, rather than relying on hardcoded question templates.

## 🙏 Contributing

This is a personal automation project, but suggestions and improvements are welcome!

## 📄 License

MIT License - Use responsibly and ethically.

---

**Ready to Build**: This README provides the complete conceptual framework. Implementation can now proceed with the dynamic question extraction and LLM-powered answer generation at its core.

