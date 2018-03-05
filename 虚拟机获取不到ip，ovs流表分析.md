## 虚拟机获取不到ip，ovs流表分析

创建了一台虚拟机，没有获取到IP地址，虚拟机信息如下：

vm id： 9f3a9c1f-30f0-478d-9004-97a1f81db5c7
nework： 3bf84212-0b9a-4c4b-aa16-0be8757af78c
port：   1e4eca87-2c1d-40e9-9135-502d1bea8e60
compute node：172.28.8.31

查看虚拟机的console log：

```shell
# openstack console log show 9f3a9c1f-30f0-478d-9004-97a1f81db5c7
[   40.109150] cloud-init[689]: 2017-12-11 16:54:13,493 - util.py[WARNING]: Route info failed: Unexpected error while running command.
[   40.109355] cloud-init[689]: Command: ['netstat', '-rn']
[   40.109488] cloud-init[689]: Exit code: 1
[   40.109613] cloud-init[689]: Reason: -
[   40.109737] cloud-init[689]: Stdout: Kernel IP routing table^M
……
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Route info failed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

登录到计算节点上，查看虚拟机的tap设备

```shell
# virsh dumpxml 9f3a9c1f-30f0-478d-9004-97a1f81db5c7 | grep tap
tap1e4eca87-2
```

看一下dhcp agent

```shell
# openstack network agent list --network 3bf84212-0b9a-4c4b-aa16-0be8757af78c
+------------+--------------+-------------------+-------+-------+--------------------+
| Agent Type | Host         | Availability Zone | Alive | State | Binary             |
+------------+--------------+-------------------+-------+-------+--------------------+
| DHCP agent | 10e131e73e25 | nova              | :-)   | UP    | neutron-dhcp-agent |
| DHCP agent | 10e131e73e24 | nova              | :-)   | UP    | neutron-dhcp-agent |
+------------+--------------+-------------------+-------+-------+--------------------+
```

dhcp对应的vxlan设备，是 vxlan-0a834818 和 vxlan-0a834819

```shell
# ovs-vsctl show | grep vxlan
        Port "vxlan-0a834818"
            Interface "vxlan-0a834818"
                type: vxlan
                options: {df_default="true", in_key=flow, local_ip="10.131.72.31", out_key=flow, remote_ip="10.131.72.24"}
        Port "vxlan-0a834819"
            Interface "vxlan-0a834819"
                type: vxlan
                options: {df_default="true", in_key=flow, local_ip="10.131.72.31", out_key=flow, remote_ip="10.131.72.25"}
```

vxlan设备对应的port，记录一下，port 8和25

```shell
# ovs-ofctl show br-tun | grep vxlan-0a834818
 8(vxlan-0a834818): addr:5a:2e:50:94:56:d4
# ovs-ofctl show br-tun | grep vxlan-0a834819
 25(vxlan-0a834819): addr:52:eb:7c:fd:58:d0
```

虚拟机tap设备的vlan tag

```shell
# ovs-vsctl show | grep tap1e4eca87-2c -C 1
                type: internal
        Port "tap1e4eca87-2c"
            tag: 21
            Interface "tap1e4eca87-2c"
        Port "qr-6a267914-fd"

```

看一下vlan21的流表，看到table22的ouput中没有dhcp需要的port 8和25

```shell
# ovs-ofctl dump-flows br-tun|grep dl_vlan=21
 cookie=0x3ee2a455fb2713e2, duration=62760.252s, table=22, n_packets=4816, n_bytes=1045304, idle_age=7, priority=1,dl_vlan=21 actions=strip_vlan,load:0x27->NXM_NX_TUN_ID[],output:28,output:29,output:5
```

所以虚拟机没有获取到IP地址的原因就是流表丢失，关于流表丢失的原因，还需要看代码

到这里可以重启dhcp agent服务，或者手动添加流表

添加流表的命令：

```shell
# ovs-ofctl add-flow br-tun "cookie=0x3ee2a455fb2713e2, table=22, priority=1,dl_vlan=21 actions=strip_vlan,load:0x27->NXM_NX_TUN_ID[],output:28,output:29,output:5,output:8,output:25"
```

删除流表命令：

```shell
# ovs-ofctl del-flow br-tun "table=22, dl_vlan=21"
```

