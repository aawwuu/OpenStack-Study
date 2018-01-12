#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
import requests
import sys
from ConfigParser import RawConfigParser


# login zabbix
def login(username, password):

    data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": username,
                "password": password
                },
            "id": 0
            }

    token = result(data)
    return token


def get_hostgroups(token):

    data = {
            "jsonrpc":"2.0",
            "method":"hostgroup.get",
            "params":{
                "output":["groupid","name"],
                },
            "auth":token, 
            "id":1,
            }

    host_group = {}
    for i in result(data):
        key = i['name']
        value = i['groupid']
        host_group[key] = value
    return host_group


def get_hosts(token, groupid):

    data = {
            "jsonrpc":"2.0",
            "method":"host.get",
            "params":{
                "output":["hostid","name"],
                "groupids":groupid,
                },
            "auth":token, 
            "id":1,
            }

    hosts = {}
    for i in result(data):
        key = i['name'].replace("e", ".")
        value = i['hostid']
        hosts[key] = value
    return hosts


def get_items(token, hostid):

    data = {
            "jsonrpc":"2.0",
            "method":"item.get",
            "params":{
                "output":["itemids","key_"],
                "hostids":hostid,
                },
            "auth":token, 
            "id":1,
            }

    items = {}
    for i in result(data):
        key = i['key_']
        value = i['itemid']
        items[key] = value
    return items


def get_history_data(token, itemid, time_from, history=3, limit=1):

    data = {
            "jsonrpc":"2.0",
            "method":"history.get",
            "params":{
                "output":"extend",
                "history":history,
                "itemids":itemid,
                "time_from":time_from,
                "limit":limit,
                "sortfield": "clock",
                "sortorder": "DESC",
                },
            "auth":token,
            "id":1,
            }

    history_data = {}
    for i in result(data):
        key = i['clock']
        value = float(i['value'])
        history_data[key] = value
    return history_data



def result(data):

    config = RawConfigParser()
    config.read('conf.cfg')

    headers = {'Content-Type': 'application/json-rpc'}
    url = 'http://%s/zabbix/api_jsonrpc.php' %config.get('zabbix', 'ip')
    request = requests.post(url=url,headers=headers,data=json.dumps(data))

    try:
        result = json.loads(request.text)
        return result['result']
    except Exception as e:
        print result['error']['message']
        print result['error']['data'], "\n"
        sys.exit(1)
[root@10e131e73e115 temp]# 
[root@10e131e73e115 temp]# ls
conf.cfg  main.py  NovaSql.py  zabbix.py
[root@10e131e73e115 temp]# cat NovaSql.py
#! /usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys
from ConfigParser import RawConfigParser
from prettytable import PrettyTable


def nova_sql():

    config = RawConfigParser()
    config.read('conf.cfg')

    cpu_ratio = float(config.get('default', 'cpu_ratio'))
    ram_ratio = float(config.get('default', 'ram_ratio'))

    host = config.get('nova_db', 'host')
    port = int(config.get('nova_db', 'port'))
    user = config.get('nova_db', 'user')
    passwd = config.get('nova_db', 'passwd')
    db = config.get('nova_db', 'db')
    con = mdb.connect(host = host, port = port, user = user, passwd = passwd, db = db)
    pt = PrettyTable()
    pt.field_names = ["host", "vcpus", "ratio_cpus", "vcpus_used", "ratio_ram", "ram_used", "running_vms"]
    with con:
        cur = con.cursor()
        sql = "select host_ip,vcpus,vcpus_used,memory_mb,memory_mb_used,running_vms,cpu_allocation_ratio,ram_allocation_ratio \
               from compute_nodes join services on compute_nodes.host=services.host \
               and compute_nodes.deleted='0' and services.deleted='0' \
               and services.binary='nova-compute'"
        cur.execute(sql)
        numrows = int(cur.rowcount)
        for i in range(numrows):
            host, vcpus, vcpus_used, mem, mem_used, running_vms, cpu_allocation_ratio, ram_allocation_ratio = cur.fetchone()
            if not cpu_allocation_ratio:
                cpu_allocation_ratio = cpu_ratio
            if not ram_allocation_ratio:
                ram_allocation_ratio = ram_ratio
            ratio_cpus = int(vcpus * cpu_allocation_ratio)
            ratio_ram = int(mem * ram_allocation_ratio) >> 10
	    mem_used = mem_used >> 10
            row = [host, vcpus, ratio_cpus, vcpus_used, ratio_ram, mem_used, running_vms]
            pt.add_row(row)
    return pt.get_string(sortby="host")
