
cheese_schema = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string'},
        'name': {'type': 'string'},
        'producer': {'type': 'string'},
        'age': {'type': 'number'},
        'weight': {
            'type': 'string',
            'pattern': '^[1-9][0-9]*(kg|pound|g|oz)'
        },
        'taste': {'type': 'string'},
        'valid_through': {
            'type': 'string',
            'pattern': '^[0-9]{4}/[0-9]{2}/[0-9]{2}',
        },
    },
    'required': ['type', 'name', 'valid_through', 'weight'],
}

zone_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'temperature': {'type': 'string', 'pattern': '^[1-9][0-9]*c$'},
        'humidity': {'type': 'string', 'pattern': '[1-9][0-9]?%'},
        'light': {'type': 'string', 'pattern': '^(full-light|semi-darkness|darkness)'},
    },
    'required': ['temperature', 'humidity', 'light'],
}

zone_transfer_schema = {
    'type': 'object',
    'properties': {
        'cheese_id': {'type': 'string'},
        'from_zone_id': {'type': 'string'},
        'to_zone_id': {'type': 'string'},
    },
    'required': ['cheese_id', 'from_zone_id', 'to_zone_id'],
}

zone_assignment_schema = {
    'type': 'object',
    'properties': {
        'cheese_id': {'type': 'string'},
        'zone_id': {'type': 'string'},
    },
    'required': ['cheese_id', 'zone_id'],
}