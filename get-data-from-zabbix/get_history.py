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


def get_host_state(host_type):

    groupid = host_group[host_type]
    hosts = z.get_hosts(groupid)
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
        w.writerow(["CPU使用情况"])
        w.writerow(cpu_fields)

        for host in host_list:
            items = z.get_items(hosts[host])
            cpu_itemid = items['cpureal.idletime']
            cpu_idle = z.get_history_data(cpu_itemid, time_from, history=0, limit=None)
            cpu_values = cpu_idle.values()
            cpu_usage_latest = '{:.2%}'.format(1-cpu_values[0])
            cpu_usage_max = '{:.2%}'.format(1-min(cpu_values))
            cpu_usage_min = '{:.2%}'.format(1-mix(cpu_values))
            cpu_usage_avg = '{:.2%}'.format(1-sum(cpu_values) / len(cpu_values))
            cpu_row = [host, cpu_usage_latest, cpu_usage_max, cpu_usage_min, cpu_usage_avg]
            w.writerow(cpu_row)
        '''
        for host in host_list:
            items = z.get_items(hosts[host])
            cpu_itemid = items['system.cpu.load[percpu,avg15]']
            cpu_load = z.get_history_data(cpu_itemid, time_from, history=0, limit=None)
            cpu_values = cpu_load.values()
            cpu_load_latest = '{:.2%}'.format(cpu_values[0])
            cpu_load_max = '{:.2%}'.format(max(cpu_values))
            cpu_load_min = '{:.2%}'.format(min(cpu_values))
            cpu_load_avg = '{:.2%}'.format(sum(cpu_values) / len(cpu_values))
            cpu_row = [host, cpu_load_latest, cpu_load_max, cpu_load_min, cpu_load_avg]
        
            w.writerow(cpu_row)
        '''
        print("Complete {0} CPU resource".format(host_type))

        w.writerow([" "])
        w.writerow(["内存使用情况"])
        w.writerow(mem_fields)
        for host in host_list:
            items = z.get_items(hosts[host])
            mem_total_itemid = items['vm.memory.size[total]']
            mem_avail_itemid = items['vm.memory.size[available]']
            mem_total = z.get_history_data(mem_total_itemid, time_from=None, limit=1)
            mem_avail = z.get_history_data(mem_avail_itemid, time_from, limit=None)
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


def get_nic_data(host_type):

    groupid = host_group[host_type]
    hosts = z.get_hosts(groupid)
    host_list = hosts.keys()
    host_list.sort()
    
    nic_fields = ['nic', 'in_max', 'in_min', 'in_avg', 'out_max', 'out_min', 'out_avg']

    if host_type == 'Compute node':
        nics = ['enp7s0f0.1224', 'enp7s0f0.3303', 'enp130s0f0', 'enp130s0f1', 'enp2s0f0.1221']
    elif host_type == 'Ceph':
        nics = ['enp5s0f0', 'enp7s0f0.3302', 'enp2s0f0.1221']
    elif host_type == 'Controller node':
        nics = ['eth0', 'eth1', 'eth2']
    elif host_type == 'Discovered hosts':
        nics = ['bond0']
    
    with open('report/%s.csv'%date, 'a+') as f:
        w = csv.writer(f)
        w.writerow(nic_fields)

        for host in host_list:
            w.writerow(["{0}".format(host)])
            items = z.get_items(hosts[host])

            for nic in nics:

                if not 'net.if.in[%s]'%nic in items.keys():
                    continue
                in_itemid = items['net.if.in[%s]' %nic]
                out_itemid = items['net.if.out[%s]' %nic]
                #packets_in_itemid = items['net.if.out[%s,packets]' %nic]
                #packets_out_itemid = items['net.if.out[%s,packets]' %nic]
                #speed_itemid = items['net.speed.get[%s]' %nic]

                in_data = z.get_history_data(in_itemid, time_from, limit=None)
                out_data = z.get_history_data(out_itemid, time_from, limit=None)
                #packets_in_data = zabbix.get_history_data(token, packets_in_itemid, time_from, limit=None)
                #packets_out_data = zabbix.get_history_data(token, packets_out_itemid, time_from, limit=None)
                #speed_data = zabbix.get_history_data(token, speed_itemid, time_from, limit=None)

                in_values = map(lambda x : round(x / (1024**2), 2), in_data.values())
                in_max = max(in_values)
                in_min = min(in_values)
                in_avg = sum(in_values) / len(in_values)

                out_values = map(lambda x : round(x / (1024**2), 2), out_data.values())
                out_max = max(out_values) 
                out_min = min(out_values) 
                out_avg = sum(out_values) / len(out_values)
                """
                packets_in_values = map(lambda x : round(x / 1024, 2), packets_in_data.values())
                packets_in_max = max(packets_in_values)
                packets_in_min = min(packets_in_values)
                packets_in_avg = sum(packets_in_values) / len(packets_in_values)

                packets_out_values = map(lambda x : round(x / 1024, 2), packets_out_data.values())
                packets_out_max = max(packets_out_values)
                packets_out_min = min(packets_out_values)
                packets_out_avg = sum(packets_out_values) / len(packets_out_values)

                speed_values = map(lambda x : round(x / 1024, 2), speed_data.values())
                speed_max = max(speed_values)
                speed_min = min(speed_values)
                speed_avg = sum(speed_values) / len(speed_values)
                """
                nic_row = [nic, in_max, in_min, in_avg, out_max, out_min, out_avg]
                w.writerow(nic_row)
                print("Complete", host, nic)
            w.writerow([" "])
            print("Complete {0} network traffic data".format(host))

def main():
    '''
    print("本程序运行时间较长，请耐心等待")
    with open('report/%s.csv'%date, 'a+') as f:
        w = csv.writer(f)
        w.writerow(["虚拟机资源使用情况"])
        w.writerows(NovaSQL.nova_sql())
        w.writerow([" "])
    '''
    #get_host_state('Compute node')
    #get_host_state('Controller node')
    #get_host_state('Ceph')
    get_host_state('Discovered hosts')
    get_nic_data('Discovered hosts')
    get_host_state('Windows_jumpservers')
    #get_nic_data('Controller node')
    print("Complete!!!!!!!!!!!!!!!!!!!!\n")
    print("Check the report: report/%s.csv"%date)


if __name__ == '__main__':
    main()