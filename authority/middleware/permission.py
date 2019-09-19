# -*- coding: utf-8 -*-

def initial_permission(user, request):
    permissions = user.groups.all().values('permission__url', 'permission__action', 'permission__group_id').distinct()
    permissions_dict = {}
    for k in permissions:
        gid = k.get('permission__group_id')
        if gid not in permissions_dict:
            permissions_dict[gid] = {
                'urls': [k.get('permission__url'), ],
                'actions': [k.get('permission__action', )]
            }
        else:
            permissions_dict[gid]["urls"].append(k.get('permission__url'))
            permissions_dict[gid]["actions"].append(k.get('permission__action'))
    request.session['user_id'] = user.id
    request.session['permissions'] = permissions_dict
    request.session.set_expiry(3600)
