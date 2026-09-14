"""
Normaliza las ofertas de cada fuente a un esquema común:
{title, company, location, description, url, remote, source}
"""
import re
import html


def clean_text(raw):
    """Quita etiquetas HTML y decodifica entidades (&amp;, &nbsp;, etc.)."""
    if not raw:
        return ""
    sin_tags = re.sub(r"<[^>]+>", " ", raw)          # elimina <p>, <br>, etc.
    decodificado = html.unescape(sin_tags)             # &amp; → &, &nbsp; → espacio
    return re.sub(r"\s+", " ", decodificado).strip()   # colapsa espacios/saltos repetidos


def normalize_arbeitnow(job):
    tags = job.get("tags", []) or []
    job_types = job.get("job_types", []) or []
    return {
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": job.get("location", ""),
        "description": clean_text(job.get("description", "")),
        "url": job.get("url", ""),
        "remote": bool(job.get("remote", False)),
        "tags": tags + job_types,
        "source": "Arbeitnow",
    }


def normalize_remotive(job):
    location = job.get("candidate_required_location", "")
    return {
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": location,
        "description": clean_text(job.get("description", "")),
        "url": job.get("url", ""),
        "remote": True,  # Remotive es 100% remoto por definición
        "tags": job.get("tags", []) or [],
        "source": "Remotive",
    }


def normalize_themuse(job):
    locations = job.get("locations", []) or []
    location_str = ", ".join(l.get("name", "") for l in locations)
    levels = job.get("levels", []) or []
    level_str = ", ".join(l.get("name", "") for l in levels)
    company = job.get("company") or {}
    refs = job.get("refs") or {}
    return {
        "title": job.get("name", ""),
        "company": company.get("name", ""),
        "location": location_str,
        "description": clean_text(job.get("contents", "")),
        "url": refs.get("landing_page", ""),
        "remote": "remote" in location_str.lower(),
        "tags": [level_str] if level_str else [],
        "source": "The Muse",
    }


def normalize_adzuna(job, country=""):
    company = job.get("company") or {}
    location = job.get("location") or {}
    category = job.get("category") or {}
    return {
        "title": job.get("title", ""),
        "company": company.get("display_name", ""),
        "location": location.get("display_name", ""),
        "description": clean_text(job.get("description", "")),
        "url": job.get("redirect_url", ""),
        "remote": "remote" in (job.get("title", "") + job.get("description", "")).lower(),
        "tags": [category.get("label", "")] if category.get("label") else [],
        "source": f"Adzuna ({country.upper()})" if country else "Adzuna",
    }


def normalize_all(raw_by_source):
    """
    raw_by_source: dict tipo
    {
        "arbeitnow": [job, job, ...],
        "remotive": [job, job, ...],
        "themuse": [job, job, ...],
        "adzuna": [(job, country), (job, country), ...],
    }
    """
    normalized = []
    normalized += [normalize_arbeitnow(j) for j in raw_by_source.get("arbeitnow", [])]
    normalized += [normalize_remotive(j) for j in raw_by_source.get("remotive", [])]
    normalized += [normalize_themuse(j) for j in raw_by_source.get("themuse", [])]
    normalized += [normalize_adzuna(j, c) for j, c in raw_by_source.get("adzuna", [])]
    return normalized