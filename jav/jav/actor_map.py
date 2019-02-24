
ACTOR_MAP = {
    'Ai Sena' : 'Ai Hoshina',
    'Sana Imanaga':'Sana Matsunaga',
    'Hibiki Ootsuki': 'Hibiki Otsuki',
    'Saya Niiyama' : 'Saya Niyama',
    'Miho Tsuno' : 'Miho Tono',
    'Shiori Uehara': 'Yui Uehara',
    'Anju Minase':'Anju Kaise'
}

def adjust_actor(name):
    if name in ACTOR_MAP:
        return ACTOR_MAP[name]
    else:
        return name