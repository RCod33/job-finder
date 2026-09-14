"""
Llama a Gemini para generar un resumen profesional adaptado a una oferta
concreta, basado ÚNICAMENTE en tu CV real (para no inventar experiencia).
"""

import time
from google import genai
from google.genai._gaos.lib.compat_errors import RateLimitError
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()  # lee GEMINI_API_KEY del entorno automáticamente

MODEL = "gemini-3.1-flash-lite"
MAX_REINTENTOS = 3


def generat_adapted_summary(cv_texto, oferta):
    prompt = f"""Eres un asistente que ayuda a adaptar un CV a una oferta de
empleo concreta. Trabajas ÚNICAMENTE con la información del CV que te doy
abajo — no inventes experiencia, tecnologías ni logros que no aparezcan ahí.

CV BASE:
{cv_texto}

OFERTA DE EMPLEO:
Título: {oferta.get('title', '')}
Empresa: {oferta.get('company', '')}
Descripción: {oferta.get('description', '')}

Tarea: escribe un resumen profesional de 3-4 líneas, en español, para
poner al principio del CV, adaptado específicamente a esta oferta —
resalta las habilidades y experiencia del CV que más encajan con lo que
pide la descripción.

Reglas de estilo (importante, esto es lo que más se suele fallar):
- Escribe como lo escribiría la propia persona, no como una IA describiendo
  a un candidato en tercera persona genérica.
- PROHIBIDO usar frases hechas de relleno tipo: "sólida base técnica",
  "destacada trayectoria", "entornos exigentes", "alta capacidad analítica",
  "complementada con", "cuento con experiencia en". Si te sale una de estas
  al escribir, bórrala y dilo de forma más directa y concreta.
- Prefiere frases cortas y datos concretos (proyectos reales, tecnologías
  exactas) antes que adjetivos vacíos.
- No repitas literalmente frases de la oferta, y no añadas nada que no
  esté respaldado por el CV base.
- Varía la estructura de las frases — no encadenes todo con gerundios
  ("incluyendo...", "complementada con...", "garantizando...")."""

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            interaction = client.interactions.create(
                model=MODEL,
                input=prompt,
            )
            return interaction.output_text
        except RateLimitError as e:
            if intento == MAX_REINTENTOS:
                raise
            espera = 45  # el free tier de Gemini suele resetear por minuto
            print(f"  Límite de cuota alcanzado (intento {intento}/{MAX_REINTENTOS}). "
                  f"Esperando {espera}s antes de reintentar...")
            time.sleep(espera)