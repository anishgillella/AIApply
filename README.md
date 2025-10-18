# 🧠 stagehand-job-autofiller

Automate end-to-end job application submissions using [Stagehand](https://stagehand.dev) and TypeScript.  
This project launches a **local Chromium instance**, reads structured data from a **PDF resume**, dynamically fills form fields (text, dropdowns, checkboxes), and submits the application — all using the **Stagehand Agent**, not a computer-vision or API-driven agent.

---

## 🚀 Overview

**stagehand-job-autofiller** automates browser workflows for job applications using [Stagehand](https://docs.stagehand.dev/references/agent).  
It accepts a **job application link** as input, opens a **Chromium browser**, detects and fills form fields intelligently, uploads your resume, and finally submits the form — while streaming **step-by-step logs** locally in real time.

The agent is capable of:
- ✅ Text, dropdown, checkbox, and button interaction  
- ✅ Resume upload (from PDF)  
- ✅ Multi-step form handling  
- ✅ Dynamic answers using **Gemini 2.5 Flash** for reasoning  
- ✅ Step-level JSON logging (streamed incrementally)  
- ❌ No screenshots or vision-based inference  

---

## 🧠 Core Concept

The agent mimics how a human applicant interacts with forms:
1. Opens the application URL  
2. Reads and maps all form fields  
3. Fills static fields (from structured profile)  
4. Uses **Gemini 2.5 Flash** for open-ended and creative answers  
5. Uploads the resume PDF  
6. Handles multi-step navigation and confirmation  
7. Submits and logs every action in real time  

---

## ⚙️ Tech Stack

| Component | Description |
|------------|--------------|
| **Language** | TypeScript |
| **Automation Framework** | [Stagehand](https://stagehand.dev) |
| **Browser** | Local Chromium (visible mode) |
| **LLM Provider** | Gemini 2.5 Flash (via environment variable) |
| **Target Platform** | Greenhouse (initially), extensible to others |
| **Logs** | JSONL (line-delimited JSON) streamed to `/logs` |
| **Input** | CLI argument (`--url`) |
| **Agent Type** | Regular Stagehand Agent (non-computer-vision) |

---

## 🧩 Applicant Profile (Static Data)

These are pre-filled automatically unless overwritten dynamically:

```yaml
Full Name: Anish Gillella
Email: anishgillella@gmail.com
Phone: 469-867-4545
LinkedIn: https://linkedin.com/in/anishgillella
GitHub: https://github.com/anishgillella
University: The University of Texas at Dallas
Major: Computer Science (Bachelors & Masters)
Location: Scraped from job posting automatically
Work Authorization: Authorized to work in the U.S. (no sponsorship required)
Veteran Status: Not a veteran
Ethnicity: Asian, Non-Hispanic
Resume Path: ./data/resume.pdf
```

---

## 🧠 Dynamic LLM Reasoning

The reasoning engine uses **Gemini 2.5 Flash** with full resume context:

### How It Works
For each open-ended question in the application:
1. **Full resume text** is included in the prompt context
2. Gemini generates answers that intelligently blend:
   - Direct facts from your resume (projects, achievements, skills)
   - Domain expertise and professional knowledge
   - Natural, human-like phrasing that sounds authentic

### Example Prompts
**Question:** "Describe a project where you used LLMs"  
**Context:** Full resume including Theus GPT-5 pipeline work  
**Generated:** "At Theus, I developed data pipelines using Parallel with GPT-5 post-processing and prompt caching to source master data from 10K+ investor sites, directly supporting a $500K seed raise."

**Question:** "What motivates you to join our company?"  
**Context:** Full resume + company mission/values  
**Generated:** "I'm driven by solving complex automation problems that blend AI reasoning and engineering. Joining your team would let me apply that passion toward real impact at scale."

### Key Features
- ✅ **Aggressive continuation** - Retries 3x on LLM errors, uses "N/A" fallback
- ✅ **Auto-submit** - No manual confirmation required
- ✅ **Full context** - Entire resume text in every prompt for maximum relevance

---

## 🧱 Architecture

```
┌──────────────────────────────────────────────┐
│ CLI Input (--url)                            │
│ e.g., npm start --url="https://..."          │
└───────────────┬──────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────┐
│ Stagehand Agent                              │
│ - Launch local Chromium                       │
│ - Detect DOM fields                           │
│ - Fill, upload, click                         │
│ - Retry on element failure                    │
└───────────────┬──────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────┐
│ Gemini 2.5 Flash Reasoner                    │
│ - Uses resume context                        │
│ - Generates creative answers beyond resume   │
│ - Fills open-ended fields                    │
└───────────────┬──────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────┐
│ Local JSONL Logger                           │
│ - Streams logs step-by-step                  │
│ - Records reasoning, field fills, retries    │
└──────────────────────────────────────────────┘
```

---

## 📦 Setup

### 1. Clone and install

```bash
git clone https://github.com/anishgillella/stagehand-job-autofiller.git
cd stagehand-job-autofiller
npm install
```

### 2. Environment setup

Create `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
RESUME_PATH=./data/resume.pdf
HEADLESS=false
```

⚠️ **Note:** Stagehand runs locally with Chromium in **visible mode** so you can monitor progress.

---

## ▶️ Run

```bash
npm start --url="https://example.com/application-form"
```

---

## 📑 Streaming Logs

Each log entry is streamed in real-time to a JSONL file inside `/logs/`.

**Example** — `logs/2025-10-17T15-40-32.jsonl`:

```json
{"step":1,"action":"open_url","url":"https://example.com","status":"success"}
{"step":2,"action":"detect_fields","count":14,"status":"success"}
{"step":3,"action":"fill_field","field":"full_name","value":"Anish Gillella","status":"success"}
{"step":4,"action":"upload_resume","file":"./data/resume.pdf","status":"success"}
{"step":5,"action":"llm_answer","question":"What motivates you to join us?","answer":"I'm driven by solving complex automation problems...","context":"beyond_resume","status":"success"}
{"step":6,"action":"submit_form","status":"success"}
{"final_status":"submitted","timestamp":"2025-10-17T15:40:32Z"}
```

Watch progress live:

```bash
tail -f logs/latest.jsonl
```

---

## ⚠️ Error Handling

| Scenario | Behavior |
|----------|----------|
| Element not detected | **Aggressive retry** - 3 attempts, then use "N/A" and continue |
| Field type mismatch | Fills with "N/A", logs warning, continues |
| Resume missing | Logs "resume_not_found" and halts |
| LLM timeout | Retries 3x, then uses "N/A" fallback |
| LLM error | Aggressive retry (3x), continues with fallback |
| Multi-step forms | Detects "Next" and "Continue" buttons, auto-submits |
| Location field | Automatically scraped from job posting description |
| Final submission | **Auto-submits** without manual confirmation |

---

## 📋 Implementation Specifications

### Configuration
```typescript
// config.ts
export const config = {
  // LLM
  geminiApiKey: process.env.GEMINI_API_KEY!,
  modelName: 'gemini-2.5-flash',
  
  // Browser
  headless: false,  // Visible mode
  timeout: 30000,
  
  // Resume
  resumePath: './data/resume.pdf',
  resumeContextStrategy: 'full_text',  // Full text in every prompt
  
  // Error Handling
  maxRetries: 3,
  retryDelay: 2000,
  aggressiveContinuation: true,
  
  // Behavior
  autoSubmit: true,  // No manual confirmation
  scrapeLocation: true,
  
  // Platform
  targetPlatform: 'greenhouse',
  
  // Profile
  applicant: {
    fullName: 'Anish Gillella',
    email: 'anishgillella@gmail.com',
    phone: '469-867-4545',
    linkedin: 'https://linkedin.com/in/anishgillella',
    github: 'https://github.com/anishgillella',
    university: 'The University of Texas at Dallas',
    major: 'Computer Science',
    workAuth: 'Authorized to work in the U.S. (no sponsorship required)',
    veteran: false,
    ethnicity: 'Asian, Non-Hispanic'
  }
};
```

### LLM Prompt Template
```typescript
// reasoner.ts
const promptTemplate = `
You are an AI assistant helping to fill out a job application.

RESUME CONTEXT:
${fullResumeText}

JOB DETAILS:
Company: ${companyName}
Position: ${positionTitle}
Location: ${scrapedLocation}

QUESTION:
${questionText}

INSTRUCTIONS:
- Answer professionally and authentically
- Draw from the resume facts when relevant
- Keep responses concise (2-4 sentences)
- Sound natural and human-like
- Avoid generic corporate jargon

ANSWER:`;
```

### Retry Logic
```typescript
async function fillFieldWithRetry(field: Field, value: string) {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      await field.fill(value);
      logger.log({ field: field.name, value, status: 'success' });
      return;
    } catch (error) {
      logger.log({ field: field.name, attempt, status: 'retry' });
      await sleep(2000);
    }
  }
  
  // Aggressive: Use "N/A" and continue
  await field.fill('N/A');
  logger.log({ field: field.name, value: 'N/A', status: 'fallback' });
}
```

### Location Scraping
```typescript
async function scrapeLocation(page: Page): Promise<string> {
  try {
    const location = await page.evaluate(() => {
      // Try multiple selectors
      const selectors = [
        '[class*="location"]',
        '[data-qa="location"]',
        '.location',
        '[aria-label*="location"]'
      ];
      
      for (const selector of selectors) {
        const el = document.querySelector(selector);
        if (el?.textContent?.trim()) {
          return el.textContent.trim();
        }
      }
      return null;
    });
    
    return location || 'Dallas, TX';  // Fallback
  } catch {
    return 'Dallas, TX';
  }
}
```

---

## 🛠️ Development

### Project Structure

```
stagehand-job-autofiller/
├── src/
│   ├── index.ts              # Entry point
│   ├── agent.ts              # Stagehand agent logic
│   ├── reasoner.ts           # Gemini 2.5 Flash integration
│   ├── profile.ts            # Static applicant data
│   └── logger.ts             # JSONL streaming logger
├── data/
│   └── resume.pdf            # Your resume
├── logs/                     # Auto-generated logs
├── .env                      # API keys
├── package.json
└── README.md
```

### Key Dependencies

```json
{
  "dependencies": {
    "@browserbasehq/stagehand": "latest",
    "playwright": "latest",
    "@google/generative-ai": "latest",
    "pdf-parse": "latest",
    "dotenv": "latest"
  },
  "devDependencies": {
    "typescript": "latest",
    "@types/node": "latest",
    "tsx": "latest"
  }
}
```

---

## 🎯 Greenhouse-Specific Implementation

This initial version is optimized for **Greenhouse** job applications.

### Greenhouse Form Patterns
- Standard multi-step wizard (Basic Info → Resume → Questions → Review)
- Consistent field naming (`first_name`, `last_name`, `email`, etc.)
- Text areas for open-ended questions
- Dropdown selectors for demographics
- File upload for resume/cover letter
- "Continue" and "Submit Application" buttons

### Detection Strategy
```typescript
// Example: Detect Greenhouse form fields
const fields = await page.$$eval('input, textarea, select', elements => 
  elements.map(el => ({
    type: el.tagName.toLowerCase(),
    name: el.name,
    id: el.id,
    label: el.closest('label')?.textContent || '',
    required: el.required
  }))
);
```

### Location Scraping
```typescript
// Scrape location from job posting
const location = await page.evaluate(() => {
  const locationEl = document.querySelector('[class*="location"]');
  return locationEl?.textContent?.trim() || 'Dallas, TX';
});
```

### Future Platform Support
The architecture is extensible to:
- LinkedIn Easy Apply (Phase 2)
- Lever (different form structure)
- Workday (multi-page flows)
- Custom company sites

---

## 🚧 Roadmap

- [x] **Phase 1:** Greenhouse integration (current focus)
- [ ] **Phase 2:** LinkedIn Easy Apply support
- [ ] **Phase 3:** Lever, Workday, other ATS platforms
- [ ] Multi-resume support (per job type)  
- [ ] Analytics dashboard for application success rate  
- [ ] Email confirmation tracking  
- [ ] Smart location detection improvements  

---

## 📄 License

MIT License — feel free to use and modify.

---

## 🤝 Contributing

Pull requests welcome! Please open an issue first to discuss major changes.

---

## 👤 Author

**Anish Gillella**  
- LinkedIn: [linkedin.com/in/anishgillella](https://linkedin.com/in/anishgillella)  
- GitHub: [github.com/anishgillella](https://github.com/anishgillella)  
- Email: anishgillella@gmail.com

