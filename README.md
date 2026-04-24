# AI Job Scraper

Automatically scrapes AI/ML job postings from Indeed and LinkedIn every hour for jobs based in Pakistan and saves them to Google Sheets. Built with JobSpy, FastAPI, and n8n.

## How It Works

```text
n8n (scheduler) → JobSpy API → Indeed / LinkedIn → Google Sheets
```

1. n8n triggers every hour and fires 8 search queries (different roles + Pakistan cities)
2. The JobSpy API scrapes each job board and returns normalized job data
3. n8n deduplicates results, filters by AI keywords, drops jobs requiring 2+ years of experience, and appends to Google Sheets

## Filters Applied

| Filter | Rule |
| --- | --- |
| Location | Pakistan only (Islamabad, Rawalpindi, Lahore, Karachi) |
| Keywords | AI Engineer, ML Engineer, Junior AI, Agentic, etc. |
| Experience | Less than 2 years — if mentioned; passes through if not mentioned |

## Stack

- **[JobSpy](https://github.com/Bunsly/JobSpy)** — Python job scraping library
- **FastAPI + Uvicorn** — REST API wrapper around JobSpy
- **n8n** — workflow automation (scheduling, filtering, Google Sheets)
- **Docker Compose** — runs both services on a shared network

## Project Structure

```text
.
├── docker-compose.yml        # Defines n8n + jobspy services
├── schema.sql                # PostgreSQL schema (optional, not used by default)
├── .env.example              # Environment variable template
├── jobspy/
│   ├── Dockerfile
│   ├── main.py               # FastAPI app — GET /jobs endpoint
│   └── requirements.txt
└── workflows/
    └── jobspy_jobs.json      # n8n workflow — import this into n8n
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/job-scraper.git
cd job-scraper
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password
TIMEZONE=Asia/Karachi
```

### 3. Start services

```bash
docker compose up -d
```

- JobSpy API: `http://localhost:8000`
- n8n: `http://localhost:5678`

### 4. Import the workflow into n8n

1. Open n8n at `http://localhost:5678`
2. Go to **Workflows → Import**
3. Upload `workflows/jobspy_jobs.json`
4. Connect your **Google Sheets** credential in the `Sheets - AI Jobs` node
5. Activate the workflow

## API Reference

### `GET /jobs`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `search` | string | required | Job title or keywords |
| `location` | string | `remote` | City, country, or `remote` |
| `sites` | string | `indeed,linkedin,glassdoor` | Comma-separated site list |
| `results` | int | `20` | Results per site (max 100) |
| `hours_old` | int | `72` | Max age of postings in hours |

**Example:**

```bash
curl "http://localhost:8000/jobs?search=AI+Engineer&location=Islamabad,+Pakistan&sites=indeed,linkedin&results=25"
```

**Response:**

```json
{
  "success": true,
  "count": 12,
  "data": [
    {
      "job_id": "...",
      "title": "AI Engineer",
      "company": "...",
      "location": "Islamabad, Pakistan",
      "tags": "full-time",
      "salary_min": null,
      "salary_max": null,
      "url": "...",
      "apply_url": "...",
      "description": "...",
      "posted_at": "2026-04-21",
      "source": "indeed",
      "is_remote": false
    }
  ]
}
```

## Environment Variables

| Variable | Description |
| --- | --- |
| `N8N_BASIC_AUTH_USER` | n8n login username |
| `N8N_BASIC_AUTH_PASSWORD` | n8n login password |
| `TIMEZONE` | Timezone for the scheduler (e.g. `Asia/Karachi`) |

## Customizing Searches

Edit the **Define Searches** Code node in n8n (or directly in `workflows/jobspy_jobs.json`) to change search terms or locations:

```js
return [
  { json: { search: 'AI Engineer', location: 'Islamabad, Pakistan' } },
  { json: { search: 'ML Engineer', location: 'Lahore, Pakistan' } },
  // add more...
];
```
