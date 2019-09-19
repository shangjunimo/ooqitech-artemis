# -*- coding: utf-8 -*-

import string
from random import choice, randint


def get_random_string_from_random(length=None, mix_type=None):
    if mix_type is not None:
        if mix_type == 'LU':
            characters = string.uppercase
        elif mix_type == 'LL':
            characters = string.lowercase
        elif mix_type == 'LUL':
            characters = string.uppercase + string.lowercase
        elif mix_type in ['LUD', 'DLU']:
            characters = string.uppercase + string.digits
        elif mix_type in ['LLD', 'DLL']:
            characters = string.lowercase + string.digits
        elif mix_type in ['LUDP']:
            characters = string.uppercase + string.digits + string.punctuation
        elif mix_type in ['LLDP']:
            characters = string.lowercase + string.digits + string.punctuation
        elif mix_type in ['DP', 'PD']:
            characters = string.punctuation + string.digits
        elif mix_type in ['LD', 'DL']:
            characters = string.ascii_letters + string.digits
        else:
            characters = string.ascii_letters + string.digits + string.punctuation
    else:
        characters = string.ascii_letters + string.digits

    if length is not None:
        length = length
    else:
        length = 8

    if mix_type is not None:
        mix_type = mix_type

    return ''.join(choice(characters) for x in range(randint(length, length)))
