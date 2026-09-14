"""
Escribe las ofertas ya rankeadas (rank_jobs) en un informe Markdown + CSV.
"""
import csv
import os
import datetime

OUTPUT_DIR = "informes"


def write_report(jobs):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

    md_path = os.path.join(OUTPUT_DIR, f"ofertas_{timestamp}.md")
    csv_path = os.path.join(OUTPUT_DIR, f"ofertas_{timestamp}.csv")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Ofertas encontradas — {timestamp}\n\n")
        f.write(f"Total: {len(jobs)}\n\n")
        for j in jobs:
            f.write(f"## {j['title']} — {j['company']}\n")
            f.write(f"- **Score:** {j['score']}/100\n")
            f.write(f"- **Ubicación:** {j['location']}{' (remoto)' if j.get('remote') else ''}\n")
            f.write(f"- **Fuente:** {j['source']}\n")
            f.write(f"- **Skills detectadas:** {', '.join(j.get('_matched_skills', [])) or '—'}\n")
            f.write(f"- **Enlace:** {j['url']}\n\n")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "score", "title", "company", "location", "remote", "source", "url"
        ])
        writer.writeheader()
        for j in jobs:
            writer.writerow({k: j.get(k, "") for k in writer.fieldnames})

    return md_path, csv_path