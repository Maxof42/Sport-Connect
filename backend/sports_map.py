"""Mapping du nom / adresse d'un club vers un sport (discipline)."""

# Ordre important: le premier motif trouve gagne.
KEYWORD_TO_SPORT = [
    (("tennis de table", "ping pong", "tennis table"), "Tennis de table"),
    (("padel",), "Padel"),
    (("tennis",), "Tennis"),
    (("football", "foot ", "f.c", "fc ", " fc", "futsal"), "Football"),
    (("rugby", "ovalie", "xiii", "xv "), "Rugby"),
    (("basket", "b.c", "bc "), "Basketball"),
    (("handball", "hand ", "hbc", "h.b.c"), "Handball"),
    (("volley", "beach volley"), "Volley-ball"),
    (("badminton", "bad "), "Badminton"),
    (("squash",), "Squash"),
    (("natation", "nautique aqua", "aquatique", "swimming", "nageurs"), "Natation"),
    (("plongee", "subaquatique", "sous-marin"), "Plongee"),
    (("aviron", "canoe", "kayak", "voile", "nautique"), "Sports nautiques"),
    (("athletisme", "athletic", "courir", "coureurs", "marathon", "trail"), "Athletisme"),
    (("petanque", "boule", "quilles", "jeu de boule"), "Petanque"),
    (("equestre", "equitation", "cheval", "poney", "hippique", "attelage"), "Equitation"),
    (("golf",), "Golf"),
    (("skate", "roller", "bmx", "trottinette"), "Skate / Roller"),
    (("escalade", "grimpe", "montagne", "alpin club", "alpinisme"), "Escalade"),
    (("danse", "dance", "twirling", "majorette", "country"), "Danse"),
    (("judo", "karate", "taekwondo", "aikido", "kung fu", "wushu", "boxe", "lutte",
      "arts martiaux", "jiu", "ju-jitsu", "jujitsu", "krav", "viet vo", "sambo",
      "kick", "muay", "mma", "self defense", "kendo", "capoeira"), "Arts martiaux"),
    (("musculation", "fitness", "forme", "cross training", "crossfit", "haltero", "powerlifting"), "Fitness / Musculation"),
    (("cyclisme", "cyclo", "velo", "cycliste", "vtt", "bicross"), "Cyclisme"),
    (("tir a l'arc", "archers", "compagnie d'arc", "arc "), "Tir a l'arc"),
    (("tir sportif", "ball trap", "tir "), "Tir"),
    (("patinage", "patineurs", "glace", "hockey glace"), "Patinage"),
    (("pelote", "fronton", "trinquet", "cesta"), "Pelote basque"),
    (("baseball", "softball"), "Baseball"),
    (("hockey",), "Hockey"),
    (("gymnastique", "gym ", "gymnique", "trampoline", "acrosport"), "Gymnastique"),
    (("randonnee", "rando", "marcheurs", "pedestre"), "Randonnee"),
    (("yoga", "tai chi", "qi gong", "pilates"), "Yoga & bien-etre"),
    (("echecs",), "Echecs"),
    (("escrime",), "Escrime"),
    (("triathlon", "duathlon"), "Triathlon"),
    (("omnisport", "multisport", "amicale laique", "patronage", "sports pour tous"), "Multisports"),
]


def map_sport(*texts: str) -> str:
    blob = " ".join(t for t in texts if t).lower()
    for keywords, sport in KEYWORD_TO_SPORT:
        for kw in keywords:
            if kw in blob:
                return sport
    return "Multisports"
