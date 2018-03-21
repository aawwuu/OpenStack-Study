# 虚拟机跨域迁移后无法绑定浮动ip

### 问题

OpenStack 环境有两个 `availability zone`   ： nova 和 test

计算节点下线，由于 libvirt 版本不一致，只能执行冷迁移。虚拟机由 test 迁移到 nova 后无法绑定浮动 ip ，提示找不到 fix ip 

```shell
# openstack server add floating ip smart003 36.111.0.129
Unable to associate floating IP 36.111.0.129 to fixed IP 10.0.0.14 for instance 349cdda9-88a1-4e7d-9e2a-2519e1ccbd4b. Error: Fixed IP not found for address 10.0.0.14. (HTTP 400) (Request-ID: req-f6af7d21-88ce-4c67-a342-85cc4b47802a)
```

### 处理过程

看日志 nova-api.log

```python
2018-03-21 14:28:50.402 44660 DEBUG nova.api.openstack.wsgi [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] Action: 'action', calling method: <function _add_floating_ip at 0x7d215f0>, body: {"addFloatingIp": {"address": "36.111.0.129"}} _process_stack /usr/lib/python2.7/site-packages/nova/api/openstack/wsgi.py:609
2018-03-21 14:28:50.406 44660 DEBUG nova.compute.api [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] [instance: 349cdda9-88a1-4e7d-9e2a-2519e1ccbd4b] Fetching instance by UUID get /usr/lib/python2.7/site-packages/nova/compute/api.py:2279
2018-03-21 14:28:50.414 44660 DEBUG oslo_concurrency.lockutils [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] Lock "cbd50649-94e9-45f2-8270-02d704f271fc" acquired by "nova.context.get_or_set_cached_cell_and_set_connections" :: waited 0.000s inner /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:270
2018-03-21 14:28:50.414 44660 DEBUG oslo_concurrency.lockutils [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] Lock "cbd50649-94e9-45f2-8270-02d704f271fc" released by "nova.context.get_or_set_cached_cell_and_set_connections" :: held 0.000s inner /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:282
2018-03-21 14:28:50.460 44660 DEBUG oslo_concurrency.lockutils [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] Acquired semaphore "refresh_cache-349cdda9-88a1-4e7d-9e2a-2519e1ccbd4b" lock /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:212
2018-03-21 14:28:50.511 44660 DEBUG oslo_concurrency.lockutils [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] Releasing semaphore "refresh_cache-349cdda9-88a1-4e7d-9e2a-2519e1ccbd4b" lock /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:225
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] Unable to associate floating IP 36.111.0.129 to fixed IP 10.0.0.14 for instance 349cdda9-88a1-4e7d-9e2a-2519e1ccbd4b. Error: Fixed IP not found for address 10.0.0.14.: FixedIpNotFoundForAddress: Fixed IP not found for address 10.0.0.14.
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips Traceback (most recent call last):
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips   File "/usr/lib/python2.7/site-packages/nova/api/openstack/compute/floating_ips.py", line 267, in _add_floating_ip
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips     fixed_address=fixed_address)
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips   File "/usr/lib/python2.7/site-packages/nova/network/base_api.py", line 83, in wrapper
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips     res = f(self, context, *args, **kwargs)
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips   File "/usr/lib/python2.7/site-packages/nova/network/neutronv2/api.py", line 1759, in associate_floating_ip
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips     fixed_address)
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips   File "/usr/lib/python2.7/site-packages/nova/network/neutronv2/api.py", line 1744, in _get_port_id_by_fixed_address
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips     raise exception.FixedIpNotFoundForAddress(address=address)
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips FixedIpNotFoundForAddress: Fixed IP not found for address 10.0.0.14.
2018-03-21 14:28:50.512 44660 ERROR nova.api.openstack.compute.floating_ips 
2018-03-21 14:28:50.513 44660 INFO nova.api.openstack.wsgi [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] HTTP exception thrown: Unable to associate floating IP 36.111.0.129 to fixed IP 10.0.0.14 for instance 349cdda9-88a1-4e7d-9e2a-2519e1ccbd4b. Error: Fixed IP not found for address 10.0.0.14.
2018-03-21 14:28:50.514 44660 DEBUG nova.api.openstack.wsgi [req-f6af7d21-88ce-4c67-a342-85cc4b47802a 07cb97c6e04b464db033677095ad0906 11ce0521d0b64cf78b3c6a87176df3ba - default default] Returning 400 to user: Unable to associate floating IP 36.111.0.129 to fixed IP 10.0.0.14 for instance 349cdda9-88a1-4e7d-9e2a-2519e1ccbd4b. Error: Fixed IP not found for address 10.0.0.14. __call__ /usr/lib/python2.7/site-packages/nova/api/openstack/wsgi.py:1029
```

错误信息在 `"/usr/lib/python2.7/site-packages/nova/network/neutronv2/api.py", line 1744`

因此看 `nova/network/neutronv2/api.py`

```python
class API(base_api.NetworkAPI):
    def _get_port_id_by_fixed_address(self, client,
                                      instance, address):
        """Return port_id from a fixed address."""
        zone = 'compute:%s' % instance.availability_zone
        search_opts = {'device_id': instance.uuid,
                       'device_owner': zone}
        data = client.list_ports(**search_opts)
        ports = data['ports']
        port_id = None
        for p in ports:
            for ip in p['fixed_ips']:
                if ip['ip_address'] == address:
                    port_id = p['id']
                    break
        if not port_id:
            raise exception.FixedIpNotFoundForAddress(address=address)
        return port_id

```

看到

```python
        zone = 'compute:%s' % instance.availability_zone
        search_opts = {'device_id': instance.uuid,
                       'device_owner': zone}
```

虚拟机由 test 迁移到 nova，这里 `zone = nova`

分别看虚拟机信息和端口信息，可以看到 虚拟机在 nova ，而 端口还在 test

instance信息`OS-EXT-AZ:availability_zone | nova`

port信息 `device_owner          | compute:test`

### 解决办法

手动更新 port 信息

```shell
# openstack port set --device-owner compute:nova  39b2c037-1952-41f7-814c-3e55e429e543
```

### 预防

迁移之前更新计算节点 `availability zone` 信息，只在同一个 zone 内迁移。