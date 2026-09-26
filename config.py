# Configuración del perfil — ajusta libremente

SKILLS = [

    # Lenguajes de programación
    "c++","java","javascript","typescript","ts","python",

    # Desarrollo web
    "html","css","jquery","react","bootstrap","tailwind",

    # Backend
    "node","node.js","express",

    # Bases de datos
    "mongodb","sql",

    # Control de versiones
    "git","github",

    # Herramientas / tecnologías
    "vite","vercel","dns","seo",

    # APIs / formatos
    "json",

    # Arquitectura y patrones
    "mvc","model-view-controller",

    # Programación orientada a objetos
    "oop","poo","object-oriented programming","programación orientada a objetos",

    # Algoritmos y estructuras de datos
    "algorithms","algoritmos","data structures","estructuras de datos",

    # Programación competitiva
    "competitive programming","programación competitiva","icpc",
]

# Frases técnicas que solo cuentan si aparecen tal cual, seguidas
# (evita que "rest" y "api" sueltas en cualquier parte del texto puntúen).
SKILL_PHRASES = [
    "rest api",
]

ROLE_KEYWORDS = [
    "junior developer", "junior software engineer", "junior programmer",
    "graduate developer", "entry level developer", "trainee developer",
    "software engineer intern", "developer intern", "internship developer",
    "programador junior", "desarrollador junior", "practicas programacion",
    "becario programacion", "becario desarrollo",
    # Títulos genéricos — sin "junior" explícito, pero el filtro de años de
    # experiencia y liderazgo ya descarta las que en realidad son senior.
    "software developer", "web developer", "backend developer",
    "frontend developer", "full stack developer", "software engineer",
    "programador", "desarrollador", "ingeniero de software",
    "desarrollador web", "desarrollador backend", "desarrollador frontend",
    "desarrollador full stack", "software engineer", "frontend engineer", "backend engineer", 
    "full stack engineer",
]

# Se comprueban SOLO contra el título de la oferta (ver scorer.py) —
# así una palabra como "manager" en la descripción no descarta una oferta
# de desarrollador legítima que solo la menciona de pasada.
EXCLUDE_KEYWORDS = [
    "senior", "lead", "staff engineer", "principal engineer",
    "manager", "director", "consultant", "analyst",
    "sales", "marketing", "recruiter", "copywriter", "writer",
    "support", "assistant", "reviewer", "tester",
]

# Frases en la DESCRIPCIÓN (no solo el título) que indican que el puesto
# no es junior, aunque el título no lo diga explícitamente.
EXCLUDE_DESCRIPTION_PHRASES = [
    "team lead", "lead a team", "lead the team", "leading a team",
    "manage a team", "managing a team", "leadership experience",
    "liderar un equipo", "gestionar un equipo",
]

# Si la oferta pide más años de experiencia que este número, se descarta
# (se detecta con una expresión regular tipo "5+ years", "3 años de experiencia")
MAX_YEARS_JUNIOR = 3

# Idiomas aceptados (códigos ISO que devuelve langdetect)
ALLOWED_LANGUAGES = ["es", "en"]

MIN_SCORE = 20