
ACTOR_MAP = {
    'Ai Sena' : 'Ai Hoshina',
    'Sana Imanaga':'Sana Matsunaga',
    'Hibiki Ootsuki': 'Hibiki Otsuki',
    'Saya Niiyama' : 'Saya Niyama',
    'Miho Tsuno' : 'Miho Tono',
    'Shiori Uehara': 'Yui Uehara',
    'Anju Minase':'Anju Kaise',
    'Ai Yuuzuki': 'Ai Yuzuki',
    'Yuuka Minase':'Yuka Minase',
    'Riri- Houshou':'Riri Hosho',
    'Miori Saiba' : 'Miori Ayaha',
    'Ririko Shiina' : 'Kanon Tachibana',
    'Satomi Sugihara' : 'Kanon Tachibana',
    'Yuna Shiina' : 'Yuna Shina',
    'Sari Kousaka' : 'Sari Kosaka',
    'Momose Yurina' :  'Yua Kuramochi',
    'Yuino' :  'Yua Kuramochi',
    'Rui Aya' : 'Satsuki',
    'Yuri Asada' : 'Yuri Fukada',
    'Emi Hoshii' : 'Emily Morohoshi'
}

def adjust_actor(name):
    if name in ACTOR_MAP:
        return ACTOR_MAP[name]
    else:
        return name