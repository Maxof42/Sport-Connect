"""Mapping du nom / objet RNA d'un club vers un sport (discipline)."""

# Ordre important: le premier motif trouve gagne.
KEYWORD_TO_SPORT = [
    (("tennis de table", "ping pong", "tennis table", "pongiste"), "Tennis de table"),
    (("padel",), "Padel"),
    (("tennis",), "Tennis"),
    (("football", "foot ", " foot", "futsal", "ballon rond"), "Football"),
    (("rugby", "ovalie", "xiii", " xv", "quinze", "treize"), "Rugby"),
    (("basket", "basket-ball", "basketball"), "Basketball"),
    (("handball", "hand ", " hand", "hand-ball"), "Handball"),
    (("volley", "beach volley"), "Volley-ball"),
    (("badminton", "volant"), "Badminton"),
    (("squash",), "Squash"),
    (("natation", "aquatique", "nageurs", "water polo", "water-polo", "aquagym"), "Natation"),
    (("plongee", "plongée", "subaquatique", "sous-marin", "apnee", "apnée"), "Plongee"),
    (("aviron", "canoe", "canoë", "kayak", "voile", "regate", "régate", "nautique", "peche"), "Sports nautiques"),
    (("athletisme", "athlétisme", "athletic", "coureurs", "course a pied", "course à pied", "marathon", "trail", "cross"), "Athletisme"),
    (("petanque", "pétanque", "boule", "quilles", "bouliste", "jeu provencal", "jeu provençal"), "Petanque"),
    (("equestre", "équestre", "equitation", "équitation", "cheval", "chevaux", "poney", "hippique", "attelage", "cavalier"), "Equitation"),
    (("golf",), "Golf"),
    (("skate", "roller", "bmx", "trottinette", "skateboard"), "Skate / Roller"),
    (("escalade", "grimpe", "alpinisme", "montagne", "speleo", "spéléo"), "Escalade"),
    (("danse", "dance", "twirling", "majorette", "country", "ballet", "chorégraph", "choregraph", "flamenco", "salsa", "zumba"), "Danse"),
    (("judo", "karate", "karaté", "taekwondo", "aikido", "aïkido", "kung fu", "wushu", "boxe", "lutte",
      "arts martiaux", "art martial", "jiu", "ju-jitsu", "jujitsu", "jujutsu", "krav", "viet vo", "sambo",
      "kick", "muay", "mma", "self defense", "self-defense", "kendo", "capoeira", "penchak", "qwan"), "Arts martiaux"),
    (("musculation", "fitness", "remise en forme", "cross training", "crossfit", "halterophilie", "haltérophilie", "haltero", "powerlifting", "force athletique"), "Fitness / Musculation"),
    (("cyclisme", "cyclo", "cycliste", "vtt", "bicross", "velo", "vélo"), "Cyclisme"),
    (("tir a l'arc", "tir à l'arc", "archers", "compagnie d'arc", "arc "), "Tir a l'arc"),
    (("tir sportif", "ball trap", "ball-trap", "carabine", "tir "), "Tir"),
    (("patinage", "patineurs", "roller in line", "hockey sur glace", "glace"), "Patinage"),
    (("pelote", "fronton", "trinquet", "cesta"), "Pelote basque"),
    (("baseball", "softball"), "Baseball"),
    (("hockey",), "Hockey"),
    (("gymnastique", "gym ", " gym", "gymnique", "trampoline", "acrosport", "aerobic", "aérobic"), "Gymnastique"),
    (("randonnee", "randonnée", "marcheurs", "pedestre", "pédestre", "marche nordique"), "Randonnee"),
    (("yoga", "tai chi", "tai-chi", "qi gong", "pilates", "relaxation", "sophrologie", "bien-etre", "bien-être"), "Yoga & bien-etre"),
    (("echecs", "échecs"), "Echecs"),
    (("escrime",), "Escrime"),
    (("triathlon", "duathlon"), "Triathlon"),
    (("aeromodel", "aéromodel", "modelisme", "modélisme", "aeromodélisme"), "Aeromodelisme"),
    (("parachut", "parapente", "vol libre", "ulm", "aviation", "vol a voile", "vol à voile"), "Sports aeriens"),
    (("billard",), "Billard"),
    (("bowling",), "Bowling"),
]

# Indices d'un club reellement multisport / omnisports
OMNI_KEYWORDS = (
    "omnisport", "omnisports", "multisport", "multisports", "toutes disciplines",
    "plusieurs disciplines", "diverses disciplines", "toutes les disciplines",
    "activites sportives", "activités sportives", "sports et loisirs", "sports divers",
    "sport pour tous", "sports pour tous", "diverses activites sportives",
)


import re
import unicodedata


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower()


def map_sport(*texts: str):
    """Retourne une discipline si un mot-cle (frontiere de mot) est trouve, sinon None."""
    blob = _norm(" ".join(t for t in texts if t))
    if not blob.strip():
        return None
    for keywords, sport in KEYWORD_TO_SPORT:
        for kw in keywords:
            k = _norm(kw).strip()
            if not k:
                continue
            if re.search(r"\b" + re.escape(k) + r"\b", blob):
                return sport
    return None


def is_omnisports(*texts: str) -> bool:
    blob = _norm(" ".join(t for t in texts if t))
    return any(_norm(kw) in blob for kw in OMNI_KEYWORDS)
