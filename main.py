import os
import requests
import json
from dotenv import load_dotenv
from get_jobs import get_jobs

load_dotenv()

URL_ARBEITNOW = "https://www.arbeitnow.com/api/job-board-api"
URL_REMOTIVE = "https://remotive.com/api/remote-jobs"
URL_THEMUSE = "https://www.themuse.com/api/public/jobs"
URL_ADZUNA_TEMPLATE = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"

if __name__ == "__main__":
    data = []

    # --- Remotive ---
    resp = get_jobs(URL_REMOTIVE)
    data.extend(resp.get("jobs", []))
    with open("remotive_jobs.json", "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=4)

    # --- Arbeitnow (pagina con "page") ---
    for page in range(1, 6):  # Obtener las primeras 5 páginas
        resp = get_jobs(URL_ARBEITNOW, page=page)
        data.extend(resp.get("data", []))
        with open("arbeitsnow_jobs.json", "w", encoding="utf-8") as f:
                json.dump(resp, f, ensure_ascii=False, indent=4)

    #TODO: LLevar mas afondo las peticiones de the muse, ampliando la categoria y quizas las paginas
    # --- The Muse (una llamada por nivel: Entry Level e Internship) ---
    for level in ["Entry Level", "Internship"]:
        resp = get_jobs(
            URL_THEMUSE,
            params_extra={"category": "Software Engineering", "level": level, "page": 0},
        )
        data.extend(resp.get("results", []))
        with open("muse_jobs.json", "w", encoding="utf-8") as f:
                json.dump(resp, f, ensure_ascii=False, indent=4)

        app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if app_id and app_key:
        for country in ["es", "gb", "de", "us", "fr"]: 
            url = URL_ADZUNA_TEMPLATE.format(country=country)
            resp = get_jobs(
                url,
                params_extra={
                    "app_id": app_id,
                    "app_key": app_key,
                    "what": "junior developer",
                    "category": "it-jobs",
                    "results_per_page": 50,
                    "content-type": "application/json",
                },
            )
            data.extend(resp.get("results", []))
            with open("aduzna_jobs.json", "w", encoding="utf-8") as f:
                    json.dump(resp, f, ensure_ascii=False, indent=4)
    else:
        print("Adzuna: sin ADZUNA_APP_ID/ADZUNA_APP_KEY en .env, se omite esta fuente.")

    with open("all_jobs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Ofertas encontradas: {len(data)}")