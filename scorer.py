"""
Filtra (restricciones duras) y puntúa (score) las ofertas ya normalizadas.
Requiere: pip install langdetect
"""
import re
from langdetect import detect, LangDetectException


def tokenize(text):
    """Convierte el texto en una lista de 'palabras', conservando símbolos
    típicos de tecnologías (c++, c#, node.js)."""
    return re.findall(r"[a-z0-9+#.]+", text.lower())


# Detecta "5+ years", "3-5 years of experience", "5 años de experiencia", etc.
YEARS_EXPERIENCE_PATTERN = re.compile(
    r"(\d+)\s*\+?\s*(?:years?|años?)\s*(?:of)?\s*(?:experience|exp|de experiencia)?",
    re.IGNORECASE,
)


def pide_demasiada_experiencia(text, max_years):
    for match in YEARS_EXPERIENCE_PATTERN.finditer(text):
        if int(match.group(1)) > max_years:
            return True
    return False


def contains_keyword(tokens, keyword):
    """True si TODAS las palabras del keyword están presentes como
    tokens completos (evita el falso positivo 'java' dentro de 'javascript')."""
    kw_words = keyword.lower().split()
    return all(w in tokens for w in kw_words)


# --- Filtro duro (sí/no) — se aplica ANTES del scoring ---

def cumple_restricciones(job, config):
    location = (job.get("location") or "").lower()
    es_espana = any(k in location for k in ["spain", "españa", "tenerife", "canari"])
    es_remoto = job.get("remote", False)

    if not (es_espana or es_remoto):
        return False  # presencial fuera de España → descartada siempre

    texto = f"{job.get('title', '')} {job.get('description', '')}".strip()
    if not texto:
        return True  # sin texto suficiente para detectar idioma, no descartamos por eso

    try:
        idioma = detect(texto)
    except LangDetectException:
        return True

    return idioma in config.ALLOWED_LANGUAGES


# --- Scoring (0-100) ---

def score_job(job, config):
    title = job.get("title", "")
    text = f"{title} {job.get('description', '')}"
    title_tokens = tokenize(title)
    tokens = tokenize(text)

    # El excluyente se comprueba SOLO en el título — así "manager"/"lead"
    # dentro de la descripción (ej. "coordinarás con el product manager")
    # no descarta una oferta de desarrollador legítima.
    for bad in config.EXCLUDE_KEYWORDS:
        if contains_keyword(title_tokens, bad):
            return 0

    # Estos sí se comprueban en toda la descripción, porque son señales
    # explícitas de seniority del puesto en sí, no de gente mencionada de paso.
    text_lower = text.lower()
    for phrase in config.EXCLUDE_DESCRIPTION_PHRASES:
        if phrase in text_lower:
            return 0

    if pide_demasiada_experiencia(text, config.MAX_YEARS_JUNIOR):
        return 0

    role_score = 0
    for role in config.ROLE_KEYWORDS:
        if contains_keyword(tokens, role):
            role_score = 15
            break

    matched_skills = [s for s in config.SKILLS if contains_keyword(tokens, s)]
    matched_phrases = [p for p in config.SKILL_PHRASES if p in text.lower()]
    skill_score = min((len(matched_skills) + len(matched_phrases)) * 4, 40)

    # Sin NINGÚN indicio de rol o skill relevante, no hay nada que puntuar —
    # aunque esté en España o sea remoto, se descarta. Esto es lo que antes
    # dejaba pasar ofertas de "Business Developer" o "SAP Developer" con
    # score 20 solo por ubicación, sin relación real con tu perfil.
    if role_score == 0 and skill_score == 0:
        job["_matched_skills"] = []
        return 0

    score = role_score + skill_score

    if job.get("remote"):
        score += 15

    location = (job.get("location") or "").lower()
    if any(k in location for k in ["spain", "españa", "tenerife", "canari"]):
        score += 20

    if any(contains_keyword(tokens, k) for k in ["intern", "practica", "becario", "trainee", "graduate"]):
        score += 10

    job["_matched_skills"] = matched_skills + matched_phrases
    return min(score, 100)


# --- Deduplicado + ranking final ---

def dedupe(jobs):
    seen = set()
    unique = []
    for job in jobs:
        key = (job.get("title", "").strip().lower(), job.get("company", "").strip().lower())
        if key not in seen and job.get("title"):
            seen.add(key)
            unique.append(job)
    return unique


def rank_jobs(jobs, config):
    jobs = dedupe(jobs)
    jobs = [j for j in jobs if cumple_restricciones(j, config)]

    for job in jobs:
        job["score"] = score_job(job, config)

    jobs = [j for j in jobs if j["score"] >= config.MIN_SCORE]
    jobs.sort(key=lambda j: j["score"], reverse=True)
    return jobs