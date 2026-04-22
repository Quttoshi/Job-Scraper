from fastapi import FastAPI, Query
from jobspy import scrape_jobs
from typing import Optional
import math
import pandas as pd

app = FastAPI(title="JobSpy Scraper API")


def clean(value):
    if value is None:
        return None
    try:
        if math.isnan(float(value)):
            return None
    except (TypeError, ValueError):
        pass
    return value


@app.get("/jobs")
def get_jobs(
    search:      str           = Query(..., description="Job title or keywords"),
    location:    str           = Query("remote", description="Location or 'remote'"),
    sites:       str           = Query("indeed,linkedin,glassdoor", description="Comma-separated site list"),
    results:     int           = Query(20, ge=1, le=100, description="Results per site"),
    hours_old:   Optional[int] = Query(72, description="Max age of postings in hours"),
):
    site_list = [s.strip() for s in sites.split(",")]

    df = None
    errors = []
    for site in site_list:
        try:
            result = scrape_jobs(
                site_name=[site],
                search_term=search,
                location=location,
                results_wanted=results,
                hours_old=hours_old,
                country_indeed="USA",
            )
            if result is not None and not result.empty:
                df = result if df is None else pd.concat([df, result], ignore_index=True)
        except Exception as e:
            errors.append({"site": site, "error": str(e)})

    if errors:
        print(f"Scrape errors (partial results returned): {errors}")

    if df is None or df.empty:
        return {"success": True, "count": 0, "data": []}

    # Build full job list first
    all_jobs = []
    for _, row in df.iterrows():
        job_id = str(clean(row.get("id")) or row.get("job_url") or "")
        if not job_id:
            continue
        all_jobs.append({
            "job_id":      job_id,
            "title":       str(clean(row.get("title")) or ""),
            "company":     str(clean(row.get("company")) or ""),
            "location":    str(clean(row.get("location")) or ""),
            "tags":        str(clean(row.get("job_type")) or ""),
            "salary_min":  clean(row.get("min_amount")),
            "salary_max":  clean(row.get("max_amount")),
            "url":         str(clean(row.get("job_url")) or ""),
            "apply_url":   str(clean(row.get("job_url_direct")) or clean(row.get("job_url")) or ""),
            "description": str(clean(row.get("description")) or "")[:2000],
            "posted_at":   str(clean(row.get("date_posted"))) if clean(row.get("date_posted")) else None,
            "source":      str(clean(row.get("site")) or ""),
            "is_remote":   bool(clean(row.get("is_remote"))) if clean(row.get("is_remote")) is not None else False,
        })

    return {"success": True, "count": len(all_jobs), "data": all_jobs}
