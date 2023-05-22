import uuid
import random

names=[
    'joe',
    'gabi',
    'futye',
    'sandra',
    'gaborel',
    'salamanda',
    'simsalaboom',
    'harri joefury',
    'gay spacecommunism',
    'escalating espionage',
    'erna und harri rollmeyer',
    'die kurve wird immer größer',
    'aber jetzt reichts auch wirklich'
]

def beetl(
        slug:str='',
        method='',
        beetlmode='',
        title='',
        description='',
        target=0
    ):

    def _method() -> str:
        if method: return method 
        return random.choice(['percentage','stepwise'])
    def _beetlmode() -> str:
        if beetlmode: return beetlmode
        return random.choice(['public','private'])
    def _title() -> str:
        if title: return title
        return random.choice(['our rent','some goal','new fridge'])
    def _description() -> str:
        if description: return description
        return random.choice([
            'some weird description',
            'description of an epic goal',
            'some description description description'
        ])
    def _slug() -> str:
        if slug: return slug
        return 'some slug'
    def _target() -> int:
        if target != 0: return target
        return random.randint(200,4000)
    def _obfuscation() -> str:
        return str(uuid.uuid4())[:8]

    return {
        'obfuscation': _obfuscation(),
        'slug': _slug(),
        'method': _method(),
        'beetlmode': _beetlmode(),
        'title': _title(),
        'description': _description(),
        'target': _target(),
    }


def bid(
        beetl_obfuscation: str,
        beetl_slug: str,
        name: str = '',
        min: int = 0,
        mid: int = 0,
        max: int = 0,
    ):

    def _name():
        if name: return name
        return random.choice(names)
    def _min():
        if min: return min
        return random.randint(1,200)
    def _mid():
        if mid: return mid
        return random.randint(200,250)
    def _max():
        if max: return max
        return random.randint(250,333)

    return {
        'name': _name(),
        'min': _min(),
        'mid': _mid(),
        'max': _max(),
        'beetl_obfuscation': beetl_obfuscation,
        'beetl_slug': beetl_slug,
    }

def create_bids(
    beetl_obfuscation: str,
    beetl_slug: str,
    amount: int=5 
    ):

    return [ bid(
        beetl_obfuscation=beetl_obfuscation, 
        beetl_slug=beetl_slug,
        name=names[i]
    ) for i in range(amount) ]
