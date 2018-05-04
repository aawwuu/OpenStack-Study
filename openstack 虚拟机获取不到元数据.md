## openstack 虚拟机获取不到元数据

虚拟机获取到 ip 地址，不能获取主机名和密码。

修改虚拟机密码

```
# nova set-password test
```

登录虚拟机，检查 ip 地址，路由网关，发现网络都是通的

```
# ip address
# ip route
# ping 100.10.10.1
# curl 169.254.169.254
```

重启虚拟机，仍然不能获取元数据

```
[  117.784985] cloud-init[733]: 2018-05-03 19:04:02,188 - url_helper.py[WARNING]: Calling 'http://169.254.169.254/2009-04-04/meta-data/instance-id' failed [104/120s]: request error [('Connection aborted.', error(113, 'No route to host'))]
[  125.793064] cloud-init[733]: 2018-05-03 19:04:10,196 - url_helper.py[WARNING]: Calling 'http://169.254.169.254/2009-04-04/meta-data/instance-id' failed [112/120s]: request error [('Connection aborted.', error(113, 'No route to host'))]
[  132.803663] cloud-init[733]: 2018-05-03 19:04:17,207 - url_helper.py[WARNING]: Calling 'http://169.254.169.254/2009-04-04/meta-data/instance-id' failed [119/120s]: request error [HTTPConnectionPool(host='169.254.169.254', port=80): Max retries exceeded with url: /2009-04-04/meta-data/instance-id (Caused by ConnectTimeoutError(<requests.packages.urllib3.connection.HTTPConnection object at 0x1c56950>, 'Connection to 169.254.169.254 timed out. (connect timeout=2.0)'))]
[  137.808162] cloud-init[733]: 2018-05-03 19:04:22,208 - DataSourceEc2.py[CRITICAL]: Giving up on md from ['http://169.254.169.254/2009-04-04/meta-data/instance-id'] after 124 seconds
[  140.815048] cloud-init[733]: 2018-05-03 19:04:25,218 - url_helper.py[WARNING]: Calling 'http://100.10.10.1/latest/meta-data/instance-id' failed [3/120s]: request error [('Connection aborted.', error(113, 'No route to host'))]
[  143.820917] cloud-init[733]: 2018-05-03 19:04:28,224 - url_helper.py[WARNING]: Calling 'http://100.10.10.1/latest/meta-data/instance-id' failed [6/120s]: request error [('Connection aborted.', error(113, 'No route to host'))]
```

查看虚拟机连接的router

```
# neutron router-list
# neutron router-show  a23d4085-a9b3-4f07-85a8-544799ae534f 
# neutron l3-agent-list-hosting-router a23d4085-a9b3-4f07-85a8-544799ae534f 
```

连接 router 所在的节点，检查配置，发现是

```shell
# vim /etc/neutron/neutron.conf 
# ip netns list
# ps -ef|grep haproxy

# ip netns exec qrouter-a23d4085-a9b3-4f07-85a8-544799ae534f ip a
# vim /etc/neutron/metadata_agent.ini 
# vim /var/log/neutron/metadata-agent.log 

# vim /etc/neutron/metadata_agent.ini 
[DEFAULT]
nova_metadata_ip = 172.18.211.69
metadata_proxy_shared_secret = METADATA_SECRETf
verbose = True
metadata_workers = 8
nova_metadata_port = 10012
```

发现是`/etc/neutron/metadata_agent.ini `中的`metadata_proxy_shared_secret`  写错了，要与控制节点中 `/etc/nova/nova.conf` 的对应配置相同

修改后重新创建路由和网络，创建虚拟机获取元数据成功

systemctl restart neutron-metadata-agent