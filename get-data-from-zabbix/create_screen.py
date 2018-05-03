#! /usr/bin/env python
# -*- coding:utf-8 -*-

import zabbix


z = zabbix.Zabbix()
host_group = z.get_hostgroups()


def create_screen(screen_name, hostgroup, item_key, col_num=3):

    groupid = host_group[hostgroup]
    hosts = z.get_hosts(groupid)
    host_list = hosts.keys()
    host_list.sort()

    graphs = []

    for host in host_list:
        hostid = hosts[host]
        items = z.get_items(hostid)
        itemid = items[item_key]
        graphs.append(z.get_graph(hostids=hostid, itemids=itemid))

    a, b = 0, 0
    row_num = len(graphs) / col_num + 1
    screenitems = []

    for graph in graphs:
        x = a % col_num
        y = int(b / col_num)
        group_item = {
                            "resourcetype": 0,
                            "resourceid": graph,
                            "rowspan": 0,
                            "colspan": 0,
                            "x": x,
                            "y": y,
                            "colspan": "1",
                            "rowspan": "1",
                            "elements": "0",
                            "valign": "0",
                            "halign": "0",
                            "style": "0",
                            "dynamic": "1"
                        }

        screenitems.append(group_item)

        a += 1
        b += 1

    return z.create_screen(screen_name, col_num, row_num, screenitems)



def create_disk_screen(hostgroup):

    groupid = host_group[hostgroup]
    hosts = z.get_hosts(groupid)
    host_list = hosts.keys()
    host_list.sort()

    for host in host_list:
        graphs = []
        hostid = hosts[host]
        items = z.get_items(hostid)
        disk_items = []
        for item in items.keys():
            if "disk." in item:
                disk_items.append(item)
        disk_items.sort(key=lambda x: x[-2])
        for item in disk_items:
            itemid = items[item]
            graphs.append(z.get_graph(hostids=hostid, itemids=itemid))

        a, b = 0, 0
        screenitems = []

        for graph in graphs:
            x = a % col_num
            y = int(b / col_num)
            group_item = {
                                "resourcetype": 0,
                                "resourceid": graph,
                                "rowspan": 0,
                                "colspan": 0,
                                "x": x,
                                "y": y,
                                "colspan": "1",
                                "rowspan": "1",
                                "elements": "0",
                                "valign": "0",
                                "halign": "0",
                                "style": "0",
                                "dynamic": "1"
                            }

            screenitems.append(group_item)

            a += 1
            b += 1
        col_num = 5
        row_num = len(graphs) / col_num + 1
        z.create_screen('Disk.%s'%host, col_num, row_num, screenitems)

'''
create_screen('cluster-01-cpu', 'cluster-one', 'system.cpu.util[,idle]', col_num=3)
create_screen('cluster-02-cpu', 'cluster-two', 'system.cpu.util[,idle]', col_num=3)
create_screen('cluster-03-cpu', 'cluster-three', 'system.cpu.util[,idle]', col_num=3)

create_screen('cluster-01-memory', 'cluster-one', 'vm.memory.size[available]', col_num=3)
create_screen('cluster-02-memory', 'cluster-two', 'vm.memory.size[available]', col_num=3)
create_screen('cluster-03-memory', 'cluster-three', 'vm.memory.size[available]', col_num=3)

create_screen('cluster-01-network', 'cluster-one', 'net.if.in[bond0]', col_num=3)
create_screen('cluster-02-network', 'cluster-two', 'net.if.in[bond0]', col_num=3)
create_screen('cluster-03-network', 'cluster-three', 'net.if.in[bond0]', col_num=3)


create_screen('jumpserver-01-cpu', 'Jumpservers_01', 'perf_counter[\Processor(_Total)\% Processor Time]', col_num=3)
create_screen('jumpserver-02-cpu', 'Jumpservers_02', 'perf_counter[\Processor(_Total)\% Processor Time]', col_num=3)
create_screen('jumpserver-03-cpu', 'Jumpservers_03', 'perf_counter[\Processor(_Total)\% Processor Time]', col_num=3)

create_screen('jumpserver-01-memory', 'Jumpservers_01', 'vm.memory.size[free]', col_num=3)
create_screen('jumpserver-02-memory', 'Jumpservers_02', 'vm.memory.size[free]', col_num=3)
create_screen('jumpserver-03-memory', 'Jumpservers_03', 'vm.memory.size[free]', col_num=3)

create_screen('jumpserver-01-network', 'Jumpservers_01', 'net.if.in[Intel(R) PRO/1000 MT Network Connection]', col_num=3)
create_screen('jumpserver-02-network', 'Jumpservers_02', 'net.if.in[Intel(R) PRO/1000 MT Network Connection]', col_num=3)
create_screen('jumpserver-03-network', 'Jumpservers_03', 'net.if.in[Intel(R) PRO/1000 MT Network Connection]', col_num=3)
'''

create_screen('cluster-01-cpuload', 'cluster-one', 'system.cpu.load[percpu,avg1]', col_num=3)
create_screen('cluster-02-cpuload', 'cluster-two', 'system.cpu.load[percpu,avg1]', col_num=3)
create_screen('cluster-03-cpuload', 'cluster-three', 'system.cpu.load[percpu,avg1]', col_num=3)
create_screen('jumpserver-01-cpuload', 'Jumpservers_01', 'system.cpu.load[percpu,avg1]', col_num=3)
create_screen('jumpserver-02-cpuload', 'Jumpservers_02', 'system.cpu.load[percpu,avg1]', col_num=3)
create_screen('jumpserver-03-cpuload', 'Jumpservers_03', 'system.cpu.load[percpu,avg1]', col_num=3)