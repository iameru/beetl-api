import uuid
import random

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
