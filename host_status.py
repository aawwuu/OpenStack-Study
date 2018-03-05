#!/usr/bin/python
import re
import MySQLdb
from prettytable import PrettyTable


cpu_allocation_ratio = 1.5
disk_allocation_ratio = 1.0
ram_allocation_ratio = 1.0
mysql_connection = 'mysql+pymysql://nova:qazwsxedc@172.18.211.101:10024/nova'

def connect_db(connect_string):
    reobj = re.match('mysql\+pymysql://(?P<user>.*?):(?P<password>.*?)@(?P<ip>.*?):(?P<port>.*?)/(?P<db_name>\w*?)$',
                     mysql_connection)
    if not reobj:
        print "Wrong mysql connection"
        exit(-1)
    user = reobj.groupdict()['user']
    password = reobj.groupdict()['password']
    ip = reobj.groupdict()['ip']
    port = reobj.groupdict()['port']
    db_name = reobj.groupdict()['db_name']
    return MySQLdb.connect(host=ip, port=int(port),
                           user=user, passwd=password, db=db_name)

color_tbl = {
"grey": '\033[1;30m',
"green" :'\033[32m',
"blue" : '\033[34m',
"yellow" :'\033[33m',
"red" : '\033[31m',
}

def colorizer(num):
    if num <= 20:
        return "%s%.2f%%\033[0m" % (color_tbl['grey'], num)
    if num <= 40:
        return "%s%.2f%%\033[0m" % (color_tbl['green'], num)
    if num <= 60:
        return "%s%.2f%%\033[0m" % (color_tbl['blue'], num)
    if num <= 80:
        return "%s%.2f%%\033[0m" % (color_tbl['yellow'], num)
    return "%s%.2f%%\033[0m" % (color_tbl['red'], num)


def fetch_service():
    db = connect_db(mysql_connection)
    cursor = db.cursor()
    sql = "select updated_at,host,disabled,deleted,last_seen_up\
           from services where `binary`='nova-compute'"
    host_list = {}
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        updated_at,host,disabled,deleted,last_seen_up = row
        if deleted != 0:
            continue
        host_item = {}
        host_item['disabled'] = "%s%s\033[0m" % (color_tbl['red'], "disabled") if disabled != 0  else "enable"
        host_item['last_seen_up'] = last_seen_up
        host_list[host] = host_item
    return host_list

def fetch_resouce(host_list):
    db = connect_db(mysql_connection)
    cursor = db.cursor()
    sql = "select host,host_ip,vcpus,vcpus_used,memory_mb,memory_mb_used,\
           local_gb,local_gb_used,running_vms from compute_nodes"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        host,host_ip,vcpus,vcpus_used,memory_mb,memory_mb_used,local_gb,local_gb_used,running_vms = row
        if host not in host_list:
            print "%s not exist in compute_nodes" % host
        host_list[host]['ip'] = host_ip
        host_list[host]['cpu'] = str(vcpus_used) + "/" + str(vcpus)
        host_list[host]['cpu_ratio'] = colorizer(vcpus_used * 100.0 / (vcpus * cpu_allocation_ratio))
        host_list[host]['ram'] = str(memory_mb_used) + "/" + str(memory_mb)
        host_list[host]['ram_ratio'] = colorizer(memory_mb_used * 100.0 / (memory_mb * ram_allocation_ratio))
        host_list[host]['disk'] = str(local_gb_used) + "/" + str(local_gb)
        host_list[host]['disk_ratio'] = colorizer(local_gb_used * 100.0 / (local_gb * disk_allocation_ratio))
        host_list[host]['running_vms'] = running_vms
    return host_list

def draw_table(resource_list):
    tbl = PrettyTable(["hostname", "last_seen_up","ip", "status",  "cpu", "cpu_ratio",
                       "ram", "ram_ratio", "disk", "disk_ratio", "running_vms"])
    tbl.align['hostname'] = 'l'
    tbl.align['ip'] = 'l'
    for host,resource in resource_list.items():
        tbl.add_row([host,
                     resource['last_seen_up'],
                     resource['ip'],
                     resource['disabled'],
                     resource['cpu'], resource['cpu_ratio'],
                     resource['ram'], resource['ram_ratio'],
                     resource['disk'], resource['disk_ratio'],
                     resource['running_vms']])
    print tbl


host_list = fetch_service()
resource_list = fetch_resouce(host_list)
draw_table(resource_list)
