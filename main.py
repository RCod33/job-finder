import os
import json
import config
from scorer import rank_jobs
from get_jobs import get_jobs
from dotenv import load_dotenv
from report import write_report
from normalize import normalize_all
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

URL_ARBEITNOW = "https://www.arbeitnow.com/api/job-board-api"
URL_REMOTIVE = "https://remotive.com/api/remote-jobs"
URL_THEMUSE = "https://www.themuse.com/api/public/jobs"
URL_ADZUNA_TEMPLATE = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"


def build_tasks():
    """Cada tarea es (nombre_fuente, funcion_sin_argumentos, extra)
    'extra' guarda info que necesitamos después (ej. el país para Adzuna)."""
    tasks = []

    tasks.append(("remotive", lambda: get_jobs(
        URL_REMOTIVE, params_extra={"category": "software-development"}
    ), None))

    for page in range(1, 6):
        tasks.append(("arbeitnow", lambda p=page: get_jobs(URL_ARBEITNOW, page=p), None))

    for level in ["Entry Level", "Internship"]:
        tasks.append(("themuse", lambda l=level: get_jobs(
            URL_THEMUSE,
            params_extra={"category": "Software Engineering", "level": l, "page": 0},
        ), None))

    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if app_id and app_key:
        for country in ["es", "gb", "de", "us", "fr"]:
            url = URL_ADZUNA_TEMPLATE.format(country=country)
            tasks.append(("adzuna", lambda u=url, c=country: get_jobs(
                u,
                params_extra={
                    "app_id": app_id,
                    "app_key": app_key,
                    "what": "developer",
                    "category": "it-jobs",
                    "results_per_page": 50,
                },
            ), country))
    else:
        print("Adzuna: sin ADZUNA_APP_ID/ADZUNA_APP_KEY en .env, se omite esta fuente.")

    return tasks


def fetch_all_parallel():
    tasks = build_tasks()
    raw = {"arbeitnow": [], "remotive": [], "themuse": [], "adzuna": []}

    # max_workers=8: suficientes hilos para que las ~13 peticiones se solapen,
    # sin lanzar tantas a la vez que abrumemos alguna API.
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_task = {
            executor.submit(func): (source, extra)
            for source, func, extra in tasks
        }

        for future in as_completed(future_to_task):
            source, extra = future_to_task[future]
            try:
                resp = future.result()
            except Exception as e:
                print(f"  [{source}] error: {e}")
                continue

            if source == "arbeitnow":
                raw["arbeitnow"].extend(resp.get("data", []))
            elif source == "remotive":
                raw["remotive"].extend(resp.get("jobs", []))
            elif source == "themuse":
                raw["themuse"].extend(resp.get("results", []))
            elif source == "adzuna":
                raw["adzuna"].extend((j, extra) for j in resp.get("results", []))

    return raw

if __name__ == "__main__":
    raw = fetch_all_parallel()
    data = normalize_all(raw)

    print(f"Ofertas obtenidas: {len(data)}")

    ranked = rank_jobs(data, config)

    print(f"Ofertas rankeadas: {len(ranked)}")

    with open("ranked_jobs.json", "w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)
    md_path, csv_path = write_report(ranked)
    print(f"Informe generado:\n  {md_path}\n  {csv_path}")
