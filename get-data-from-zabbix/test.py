import zabbix


z = zabbix.Zabbix()
print z.get_graph(hostids=10089, itemids=23976)