CREATE TABLE IF NOT EXISTS jobs (
    id          SERIAL PRIMARY KEY,
    job_id      TEXT UNIQUE NOT NULL,       -- RemoteOK's unique job ID
    title       TEXT NOT NULL,
    company     TEXT,
    tags        TEXT,
    salary_min  INTEGER,
    salary_max  INTEGER,
    url         TEXT,
    apply_url   TEXT,
    description TEXT,
    posted_at   TIMESTAMPTZ,
    scraped_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jobs_title    ON jobs (title);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs (posted_at DESC);
