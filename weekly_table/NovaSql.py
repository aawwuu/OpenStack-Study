
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
    pt.field_names = ["host", "vcpus", "ratio_cpus", "vcpus_used", "ratio_mem", "mem_used", "running_vms"]
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
