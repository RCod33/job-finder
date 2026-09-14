"""
Genera un resumen adaptado para UNA oferta del informe ya rankeado.

Uso:
    python generate_cv.py <indice_de_la_oferta>

Ejemplo: para la primera oferta del ranked_jobs.json (la de mayor score):
    python generate_cv.py 0
"""
import sys
import json
from llm_client import generat_adapted_summary

if __name__ == "__main__":
    
    print("1. All jobs resume\n"
          "2. Generate adapted summary for a specific index in ranked_jobs.json")

    selection = input("Select an option (1 or 2): ")

    if selection == "1":
        with open("ranked_jobs.json", "r", encoding="utf-8") as f:
            ofertas = json.load(f)

        with open("cv_base.txt", "r", encoding="utf-8") as f:
            cv_texto = f.read()

        for indice, oferta in enumerate(ofertas):
            print(f"Generando resumen adaptado para: {oferta['title']} — {oferta['company']}\n")

            resumen = generat_adapted_summary(cv_texto, oferta)
            print(resumen)

            # with open(f"resumen_oferta_{indice}.txt", "w", encoding="utf-8") as f:
            #     f.write(f"Oferta: {oferta['title']} — {oferta['company']}\n")
            #     f.write(f"Enlace: {oferta['url']}\n\n")
            #     f.write(resumen)

            print(f"\nGuardado en resumen_oferta_{indice}.txt\n")

    elif selection == "2":

        if len(sys.argv) < 2:
            print("Uso: python generate_cv.py <indice_de_la_oferta>")
            sys.exit(1)

        indice = int(sys.argv[1])

        with open("ranked_jobs.json", "r", encoding="utf-8") as f:
            ofertas = json.load(f)

        with open("cv_base.txt", "r", encoding="utf-8") as f:
            cv_texto = f.read()

        oferta = ofertas[indice]
        print(f"Generando resumen adaptado para: {oferta['title']} — {oferta['company']}\n")

        resumen = generat_adapted_summary(cv_texto, oferta)
        print(resumen)

        # with open(f"resumen_oferta_{indice}.txt", "w", encoding="utf-8") as f:
        #     f.write(f"Oferta: {oferta['title']} — {oferta['company']}\n")
        #     f.write(f"Enlace: {oferta['url']}\n\n")
        #     f.write(resumen)

        print(f"\nGuardado en resumen_oferta_{indice}.txt")