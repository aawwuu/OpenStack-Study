#! /usr/bin/env python
# -*- coding:utf-8 -*-

import NovaSql
import time
import zabbix
from datetime import datetime
from datetime import timedelta
from ConfigParser import RawConfigParser
from prettytable import PrettyTable


config = RawConfigParser()
config.read('conf.cfg')
token = zabbix.login(config.get('zabbix', 'username'), config.get('zabbix', 'password'))
start_time = (datetime.now() - timedelta(days = int(config.get('default', 'days'))))

time_from = int(time.mktime(start_time.timetuple()))
host_group = zabbix.get_hostgroups(token)


def get_host_state(host_type):

    groupid = host_group[host_type]
    hosts = zabbix.get_hosts(token, groupid)
    pt = PrettyTable()
    pt.field_names = ["host", "cpu_load_max", "cpu_load_min", "cpu_load_avg", "mem_total(Mb)", "mem_avail(Mb)"]
    for host in hosts:
        items = zabbix.get_items(token, hosts[host])
        cpu_itemid = items['system.cpu.load[percpu,avg15]']
        mem_total_itemid = items['vm.memory.size[total]']
        mem_avail_itemid = items['vm.memory.size[available]']

        cpu_load = zabbix.get_history_data(token, cpu_itemid, time_from, history=0, limit=None)
        cpu_values = list(cpu_load.values())
        cpu_load_max = max(cpu_values)
        cpu_load_min = min(cpu_values)
        cpu_load_avg = round(sum(cpu_values) / len(cpu_values), 4)
        mem_total = zabbix.get_history_data(token, mem_total_itemid, time_from=None, limit=1)
        mem_avail = zabbix.get_history_data(token, mem_avail_itemid, time_from=None, limit=1)
        mem_total = int(mem_total.values()[0]) >>10>>10
        mem_avail = int(mem_avail.values()[0]) >>10>>10
        row = host, cpu_load_max, cpu_load_min, cpu_load_avg, mem_total, mem_avail
        pt.add_row(row)

    print("\n =============== {0} ===============".format(host_type))
    return pt.get_string(sortby='host')

print("\n =============== vm resource ===============")
print(NovaSql.nova_sql())
print(get_host_state('Compute node'))
print(get_host_state('Controller node'))
print(get_host_state('Ceph'))
