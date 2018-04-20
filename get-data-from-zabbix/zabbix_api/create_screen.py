#! /usr/bin/env python
# -*- coding:utf-8 -*-

import zabbix


z = zabbix.Zabbix()
host_group = z.get_hostgroups()


def create_screen(screen_name, hostgroup, item_key, col_num, row_num):

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



def create_disk_screen(screen_name, hostgroup, item_key, col_num, row_num):

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

create_screen('HP_mem_screen', 'HP', 'vm.memory.size[available]', 3, 10)
create_screen('Dell_mem_256g_screen', 'Dell_256g', 'vm.memory.size[available]', 3, 5)
create_screen('Dell_mem_512g_screen', 'Dell_512g', 'vm.memory.size[available]', 3, 30)