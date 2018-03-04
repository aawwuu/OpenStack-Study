#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import csv
import NovaSQL
import time
import zabbix
from datetime import datetime
from datetime import timedelta
from ConfigParser import RawConfigParser


config = RawConfigParser()
config.read('conf.cfg')
token = zabbix.login(config.get('zabbix', 'username'), config.get('zabbix', 'password'))
start_time = (datetime.now() - timedelta(days = int(config.get('default', 'days'))))
date = str(datetime.now())[:10]

time_from = int(time.mktime(start_time.timetuple()))
host_group = zabbix.get_hostgroups(token)


def get_host_state(host_type):

    groupid = host_group[host_type]
    hosts = zabbix.get_hosts(token, groupid)
    host_list = hosts.keys()
    host_list.sort()
    #cpu_fields = ["host", "cpu_load_latest", "cpu_load_max", "cpu_load_min", "cpu_load_avg"]
    #mem_fields = ["host", "mem_total(G)", "mem_used_latest(G)", "mem_usage_latest","mem_used_max(G)",
    #    "mem_usage_max", "mem_used_min(G)", "mem_usage_min", "mem_used_avg(G)", "mem_usage_avg"]

    cpu_fields = ['主机', 'CPU负载', '最大值', '最小值', '平均值']
    mem_fields = ["主机", "总内存(G)", "内存使用(G)", "内存使用率","内存最大使用(G)",
        "内存最大使用率", "内存最小使用(G)", "内存最小使用率", "内存平均使用(G)", "内存平均使用率"]
    with open('report/%s.csv'%date, 'a+') as f:
        w = csv.writer(f)
        w.writerow(["{0}".format(host_type)])
        w.writerow(cpu_fields)
        for host in host_list:
            items = zabbix.get_items(token, hosts[host])
            cpu_itemid = items['system.cpu.load[percpu,avg15]']
            cpu_load = zabbix.get_history_data(token, cpu_itemid, time_from, history=0, limit=None)
            cpu_values = cpu_load.values()
            cpu_load_latest = '{:.2%}'.format(cpu_values[0])
            cpu_load_max = '{:.2%}'.format(max(cpu_values))
            cpu_load_min = '{:.2%}'.format(min(cpu_values))
            cpu_load_avg = '{:.2%}'.format(sum(cpu_values) / len(cpu_values))
            cpu_row = [host, cpu_load_latest, cpu_load_max, cpu_load_min, cpu_load_avg]
            w.writerow(cpu_row)
        print("Complete {0} CPU resource".format(host_type))

        w.writerow([" "])
        w.writerow(mem_fields)
        for host in host_list:
            items = zabbix.get_items(token, hosts[host])
            mem_total_itemid = items['vm.memory.size[total]']
            mem_avail_itemid = items['vm.memory.size[available]']
            mem_total = zabbix.get_history_data(token, mem_total_itemid, time_from=None, limit=1)
            mem_avail = zabbix.get_history_data(token, mem_avail_itemid, time_from, limit=None)
            mem_total = round(mem_total.values()[0] / (1024 ** 3), 2) 
            mem_avail_list = map(lambda x : round(x / (1024 ** 3), 2),  mem_avail.values())
            mem_used_latest = mem_total - mem_avail_list[0]
            mem_used_min = mem_total - (max(mem_avail_list))
            mem_used_max = mem_total - (min(mem_avail_list)) 
            mem_used_avg = round(mem_total - sum(mem_avail_list) / len(mem_avail_list), 2)
            mem_usage_latest = '{:.2%}'.format(mem_used_latest / mem_total)
            mem_usage_min = '{:.2%}'.format(mem_used_min / mem_total)
            mem_usage_max = '{:.2%}'.format(mem_used_max / mem_total)
            mem_usage_avg = '{:.2%}'.format(mem_used_avg / mem_total)         
            mem_row = [host, mem_total, mem_used_latest, mem_usage_latest, mem_used_max, mem_usage_max,
                mem_used_min, mem_usage_min, mem_used_avg, mem_usage_avg]
            w.writerow(mem_row)
        w.writerow([" "])
        print("Complete {0} memory resource".format(host_type))

def main():
    print("该程序运行时间较长，请耐心等待")
    with open('report/%s.csv'%date, 'a+') as f:
        w = csv.writer(f)
        w.writerow(["vm resource"])
        w.writerows(NovaSQL.nova_sql())

    get_host_state('Compute node')
    get_host_state('Controller node')
    get_host_state('Ceph')
    print("Complete!!!!!!!!!!!!!!!!!!!!")

if __name__ == '__main__':
    main()