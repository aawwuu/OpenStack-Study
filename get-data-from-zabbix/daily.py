#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import csv
import time
import zabbix
from datetime import datetime
from datetime import timedelta
from ConfigParser import RawConfigParser


config = RawConfigParser()
config.read('conf.cfg')

days=int(config.get('default', 'days'))
hours=int(config.get('default', 'hours'))
start_time = datetime.now() - timedelta(days=days, hours=hours)
date = str(datetime.now())[:10]

time_from = int(time.mktime(start_time.timetuple()))

z = zabbix.Zabbix()
host_group = z.get_hostgroups()


def get_linux_cpu_data(host_type='Discovered hosts', item_key='cpureal.idletime'):

    groupid = host_group[host_type]
    hosts = z.get_hosts(groupid)
    host_list = hosts.keys()
    host_list.sort()

    cpu_fields = ['主机', 'CPU_usage', '平均值']

    cpu1 = ''   # 10%~50%
    cpu2 = ''   # 50%~100%

    with open('report/%s.csv'%date, 'a+') as f:
        w = csv.writer(f)
        w.writerow(["{0}".format(host_type)])
        w.writerow(["CPU使用情况"])
        w.writerow(cpu_fields)
        for host in host_list:
            items = z.get_items(hosts[host])
            cpu_itemid = items[item_key]
            cpu_idle = z.get_history_data(cpu_itemid, time_from, history=0, limit=None)
            cpu_values = cpu_idle.values()
            cpu_usage_latest = '{:.2%}'.format(100-cpu_values[0])
            cpu_usage = round(100-sum(cpu_values) / len(cpu_values), 2)

            if 10<cpu_usage<50:
                cpu1 += '%s\t%s%%\n'%(host, cpu_usage_avg)
            elif 50<=cpu_usage:
                cpu2 += '%s\t%s%%\n'%(host, cpu_usage_avg)

            cpu_row = [host, cpu_usage_latest, cpu_usage_avg]
            w.writerow(cpu_row)
    if cpu1:
        print('CPU usage 10%~50%：')
        print(cpu1)
    elif cpu2:
        print('CPU usage more than 50%：')
        print(cpu2)

        
def get_linux_mem_data(host_type='Discovered hosts'):

    groupid = host_group[host_type]
    hosts = z.get_hosts(groupid)
    host_list = hosts.keys()
    host_list.sort()

    mem_fields = ["主机", "总内存(G)", "内存使用(G)", "内存使用率", "内存平均使用(G)", "内存平均使用率"]

    mem1 = ''   # 10%~50%
    mem2 = ''   # 50%~100%

    with open('report/%s.csv'%date, 'a+') as f:
        w = csv.writer(f)
        w.writerow([" "])
        w.writerow(["内存使用情况"])
        w.writerow(mem_fields)
        for host in host_list:
            items = z.get_items(hosts[host])
            mem_total_itemid = items['vm.memory.size[total]']
            mem_avail_itemid = items['vm.memory.size[available]']
            if host_type == 'Windows_jumpservers':
                mem_avail_itemid = items['vm.memory.free[percent]']

            mem_total = z.get_history_data(mem_total_itemid, time_from=None, limit=1)
            mem_avail = z.get_history_data(mem_avail_itemid, time_from, limit=None)
            mem_total = round(mem_total.values()[0] / (1024 ** 3), 2) 
            mem_avail_list = map(lambda x : round(x / (1024 ** 3), 2),  mem_avail.values())
            mem_used_latest = mem_total - mem_avail_list[0]
            mem_used_avg = round(mem_total - sum(mem_avail_list) / len(mem_avail_list), 2)
            mem_usage_latest = '{:.2%}'.format(mem_used_latest / mem_total)
            mem_usage = round(mem_used_avg / mem_total, 2)
            mem_usage_avg = '{:.2%}'.format(mem_used_avg / mem_total)
            if 0.1<mem_usage<0.5:
                mem1 += '%s\t%s\n'%(host, cpu_usage_avg)
            elif 0.5<=mem_usage:
                mem2 += '%s\t%s\n'%(host, cpu_usage_avg)
            mem_row = [host, mem_total, mem_used_latest, mem_usage_latest, mem_used_avg, mem_usage_avg]
            w.writerow(mem_row)
        w.writerow([" "])
    if mem1:
        print('Memory usage 10%~50% :')
        print(mem1)
    if mem2:
        print('emory usage more than 50% :')
        print(mem2)


def get_linux_nic_data(host_type='Discovered hosts'):

    groupid = host_group[host_type]
    hosts = z.get_hosts(groupid)
    host_list = hosts.keys()
    host_list.sort()
    
    nic_fields = ['host', 'nic', 'in_avg', 'out_avg']

    
    with open('report/%s.csv'%date, 'a+') as f:
        w = csv.writer(f)
        w.writerow(nic_fields)

        for host in host_list:            
            items = z.get_items(hosts[host])

            in_itemid = items['net.if.in[%s]' %nic]
            out_itemid = items['net.if.out[%s]' %nic]

            in_data = z.get_history_data(in_itemid, time_from, limit=None)
            out_data = z.get_history_data(out_itemid, time_from, limit=None)

            in_values = map(lambda x : round(x / (1024**2), 2), in_data.values())
            in_avg = sum(in_values) / len(in_values)
            out_values = map(lambda x : round(x / (1024**2), 2), out_data.values())
            out_avg = sum(out_values) / len(out_values)

            nic_row = [host, nic, in_max, in_min, in_avg, out_max, out_min, out_avg]
            w.writerow(nic_row)
            w.writerow([" "])


def get_win_cpu_data(host_type='Windows_jumpservers',
        item_key='perf_counter[\Processor(_Total)\% Processor Time]'):

    groupid = host_group[host_type]
    hosts = z.get_hosts(groupid)
    host_list = hosts.keys()
    host_list.sort()

    cpu_fields = ['主机', 'CPU_usage', '平均值']

    cpu1 = ''   # 10%~50%
    cpu2 = ''   # 50%~100%

    with open('report/%s.csv'%date, 'a+') as f:
        w = csv.writer(f)
        w.writerow(["{0}".format(host_type)])
        w.writerow(["CPU使用情况"])
        w.writerow(cpu_fields)
        for host in host_list:
            items = z.get_items(hosts[host])
            cpu_itemid = items[item_key]
            cpu_usage = z.get_history_data(cpu_itemid, time_from, history=0, limit=None)
            cpu_values = cpu_usage.values()
            cpu_usage_latest = cpu_values[0]
            cpu_usage = round(sum(cpu_values) / len(cpu_values), 2)

            if 10<cpu_usage<50:
                cpu1 += '%s\t%s%%\n'%(host, cpu_usage)
            elif 50<=cpu_usage:
                cpu2 += '%s\t%s%%\n'%(host, cpu_usage)

            cpu_row = [host, '%s%%'%cpu_usage_latest, '%s%%'%cpu_usage]
            w.writerow(cpu_row)
    if cpu1:
        print('CPU usage 10%~50%：')
        print(cpu1)
    elif cpu2:
        print('CPU usage more than 50%：')
        print(cpu2)

def main():
    #get_host_state('Discovered hosts')
    #get_nic_data('Discovered hosts')
    #get_host_state('Windows_jumpservers')
    get_linux_cpu_data()
    get_win_cpu_data()
    print("Complete!!!!!!!!!!!!!!!!!!!!\n")
    print("Check the report: report/%s.csv"%date)


if __name__ == '__main__':
    main()


#'vm.memory.free[percent]'