"""
Parsea el mensaje semanal del canal de WhatsApp de ofertas junior.

Uso:
    1. Copia el mensaje completo del canal en un archivo ofertas_whatsapp.txt
    2. python parse_whatsapp.py
"""
import re
import json

URL_PATTERN = re.compile(r"https?://\S+")
NUMBERING_PATTERN = re.compile(r"^\d+\.\s*")

# Banderas, emojis y el "zero-width joiner" que forma emojis compuestos (🧑‍💻)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # banderas de países
    "\U0001F300-\U0001FAFF"  # emojis varios
    "\u2600-\u27BF"          # símbolos varios (⚠️, ✅, etc.)
    "\uFE0F"                 # variation selector (hace "🇪🇸" en vez de texto)
    "\u200D"                 # zero-width joiner (emojis compuestos tipo 🧑‍💻)
    "]+",
    flags=re.UNICODE,
)

# Verbos/frases típicas del canal, de más específico a más genérico
# (el orden importa: "necesita incorporar a" debe probarse antes que "necesita")
VERB_PATTERNS = [
    r"est[áa] interesad[oa] en incorporar a",
    r"est[áa] interesad[oa] en contratar a",
    r"est[áa] interesad[oa] en",
    r"quiere contratar a",
    r"quiere incorporar a",
    r"necesita incorporar a",
    r"necesita contratar a",
    r"necesita encontrar a",
    r"tiene disponibles? sus?",
    r"tiene una oferta de",
    r"tiene abierto un",
    r"ha publicado su",
    r"est[áa] buscando",
    r"tambi[ée]n busca(?:ndo)?",
    r"busca(?:ndo)? tambi[ée]n",
    r"buscando",
    r"\bquiere\b",
    r"\bnecesita\b",
    r"\bbusca\b",
    r"\btiene\b",
    r"\bofrece\b",
]
VERB_REGEX = re.compile("|".join(VERB_PATTERNS), flags=re.IGNORECASE)


def parse_line(line):
    url_match = URL_PATTERN.search(line)
    if not url_match:
        return None
    url = url_match.group().rstrip("*")  # algunas líneas del canal traen un * pegado al final

    texto = line[:url_match.start()]
    texto = NUMBERING_PATTERN.sub("", texto)
    texto = EMOJI_PATTERN.sub("", texto)
    texto = texto.strip().rstrip(":").strip()
    if not texto:
        return None

    verb_match = VERB_REGEX.search(texto)
    if verb_match:
        company = texto[:verb_match.start()].strip().rstrip(",")
        resto = texto[verb_match.end():].strip()
        resto = re.sub(r"^(a\s+)?(un|una|otro|otra)\s+", "", resto, flags=re.IGNORECASE)
        resto = re.sub(r"^sus?\s+", "", resto, flags=re.IGNORECASE)
        title = resto
    else:
        # No se reconoció ningún verbo — nos quedamos con el texto completo,
        # el matcher/scorer igual puede evaluarlo por keywords.
        company = ""
        title = texto

    remote = "remoto" in texto.lower() or "remote" in texto.lower()

    return {
        "title": title,
        "company": company,
        "location": "",
        "description": texto,  # texto completo — red de seguridad si la separación falló
        "url": url,
        "remote": remote,
        "source": "WhatsApp",
    }


def parse_whatsapp_file(path):
    ofertas = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            oferta = parse_line(line)
            if oferta:
                ofertas.append(oferta)
    return ofertas


if __name__ == "__main__":
    ofertas = parse_whatsapp_file("ofertas_whatsapp.txt")
    print(f"Ofertas parseadas: {len(ofertas)}")
    for o in ofertas[:10]:
        print(f"  [{o['company']!r:25}] {o['title']}")

    with open("whatsapp_jobs.json", "w", encoding="utf-8") as f:
        json.dump(ofertas, f, ensure_ascii=False, indent=4)