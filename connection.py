#!/usr/bin/python

# http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/openstack/connection.py

from openstack import connection

auth_args = {
    'auth_url': 'http://172.18.211.101:10006/v3',
    'project_name': 'll',
    'username': 'll',
    'password': 'll',
    'user_domain_name': 'default',
    'project_domain_name': 'default',
}
conn = connection.Connection(**auth_args)
