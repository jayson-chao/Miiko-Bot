TORTOISE_ORM = {
    'connections': {'default': 'postgres://postgres:postgres@localhost:5432/miiko_test_tortoise'},
    'apps':{
        'models': {
            'models': ['models'],
            'default_connection': 'default',
        },
    },
}
