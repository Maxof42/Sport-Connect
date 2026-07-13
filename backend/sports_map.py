"""Mapping des types d'equipements Data-ES vers des sports / federations."""

# Ordre important: le premier motif trouve gagne.
KEYWORD_TO_SPORT = [
    (("tennis de table", "ping"), "Tennis de table"),
    (("court de tennis", "tennis"), "Tennis"),
    (("football", "foot"), "Football"),
    (("rugby",), "Rugby"),
    (("basket",), "Basketball"),
    (("handball", "hand "), "Handball"),
    (("volley",), "Volley-ball"),
    (("badminton",), "Badminton"),
    (("squash",), "Squash"),
    (("bassin", "piscine", "natation", "nage"), "Natation"),
    (("athletisme", "piste d'athle", "aire de lancer", "aire de saut"), "Athletisme"),
    (("boulodrome", "petanque", "jeu de boules", "boules"), "Petanque"),
    (("equestre", "manege", "carriere", "equitation", "hippodrome"), "Equitation"),
    (("golf", "practice"), "Golf"),
    (("skate", "roller", "bmx"), "Skate / Roller"),
    (("escalade", "sae", "mur d'escalade", "bloc"), "Escalade"),
    (("danse",), "Danse"),
    (("dojo", "arts martiaux", "judo", "karate", "boxe", "lutte"), "Arts martiaux"),
    (("musculation", "salle de forme", "fitness", "cardio"), "Fitness / Musculation"),
    (("cyclisme", "velodrome", "piste cyclable", "vtt"), "Cyclisme"),
    (("tir a l'arc", "pas de tir", "stand de tir", "tir sportif"), "Tir"),
    (("aviron", "nautique", "voile", "canoe", "kayak", "plan d'eau"), "Sports nautiques"),
    (("patinoire", "patinage", "glace"), "Patinage"),
    (("pelote", "fronton", "trinquet"), "Pelote basque"),
    (("baseball", "softball"), "Baseball"),
    (("hockey",), "Hockey"),
    (("gymnase", "salle multisport", "multisports", "salle omnisport"), "Multisports"),
    (("gymnastique", "trampoline"), "Gymnastique"),
    (("terrain de grands jeux", "stade", "plateau eps"), "Multisports"),
]


def map_sport(*texts: str) -> str:
    blob = " ".join(t for t in texts if t).lower()
    for keywords, sport in KEYWORD_TO_SPORT:
        for kw in keywords:
            if kw in blob:
                return sport
    return "Autres sports"
