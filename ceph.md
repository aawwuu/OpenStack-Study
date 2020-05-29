# ceph运维命令总结

## 一、查看状态信息

查询命令后加上"-fjson-pretty"可以输出更多详细信息

ceph osd 使用率

```shell
ceph df
ceph osd df
```

ceph 状态

```
ceph -v 			#version
ceph -s							#查看ceph状态，正常所有osdmap是up和in，pgmap是active+clean
ceph health detail
ceph osd tree						#查看所有磁盘
ceph osd pool get <pool> size|min_size|pg_num|pgp_num		#查看ceph副本数
ceph -w
ceph stat
ceph mon|osd stat
ceph daemon <osd.id> status
ceph mon|osd|pg dump
ceph quorum_status
ceph osd pool stats
ceph pg dump_stuck stale|inactive|unclean|undersized|degraded
ceph pg <pg> list_missing

ceph daemon <osd|mon> perf dump
ceph daemon osd.0 config show
```

查看pool

```
ceph osd lspools
ceph osd pool ls
rados lspools
```

ceph 进程

```
service ceph-osd-all status
service ceph-mon-all status

sudo systemctl status ceph-osd.target
sudo systemctl status ceph-mon.target
sudo systemctl status ceph-mds.target
```

查看rbd

```
rbd -p $pool_name ls -l							# rbd 列表
rbd -p $pool_name children $image_name			# 子image
rbd info $pool_name/image_name					# 详细信息
rbd du $image_name								# 实际占用空间
```

## 二、启停进程

启停mon进程

```
ssh $mon-node  #进入对应的mon节点
#批量操作所有节点
service ceph-mon-all status|stop|start|restart
#单个节点
service ceph-mon status|start|stop id=$node_id
```

启停osd进程

```
ssh $osd-node
service ceph-osd-all stop|start|restart
service ceph-osd status|start|stop id=$node_id
```

启停radosgw进程

```
ssh $radosgw-node
service radosgw-all stop|start
service apache2 stop|start
```

## 三、常见问题

#### 1. ceph pg repair

```
ceph -s 
ceph health detail
ceph pg repair <$pgid>
```

#### 2. 删除故障osd

```
/etc/init.d/ceph stop <$osd_id>
ceph stop osd.10
ceph osd crush remove osd.10
ceph auth del osd.10
ceph osd rm 10
umount /var/lib/ceph/osd/ceph-10
```

#### 3. scrub 与deep-scrub校验

白天压力大时，集群自动关闭scrub与deep-scrub校验，夜间压力小时自动开启。

#### 4.查看延时

```bash
watch -n1 -d "ceph osd perf | sort -k3nr | head"
```

可以用这个命令看延时  网宿科技的经验值是500客户就有明显卡顿

起OSD的时候也能用watch -n1 "ceph -s |egrep 'slow|block|request'"查看异常  不能长时间停在block 如果有卡可以尝试先重启对应OSD

#### 5. Openstack配置多ceph-backend后上传镜像

手动上传镜像到ceph集群

1）创建uuid

```
uuidgen  # 记录该uuid，将本地镜像命名至该uuid
```

2）记录镜像大小

```
ls -l /path/to/CentOS7.6.raw
```

3）上传至ceph集群images pool中

```
rbd import <image file> images/<uuid> 
```

4）创建镜像快照

```
rbd -p images snap create --image <uuid> --snap snap
rbd -p images snap protect --image <uuid> --snap snap
rbd -p images ls -l
rbd info images/<uuid>
```

通过glance上传镜像，指定location以及size

```
glance --os-image-api-version 1 image-create \
--id <uuid> --name <name> \
--store rbd --disk-format raw --container-format bare \
--location rbd://ceph_fsid/images/<uuid>/snap \
--size <size>
```

检查镜像

```
glance image-list
```

## 四、Glance

ceph在openstack中使用rbd管理块设备，在ceph中称为image，openstack中叫volume。image都放在pool中，不同的pool可以定义不同的副本数、pg数、放置策略等。image的命名一般是`pool_name/image_name@snap`形式。

如果镜像为非raw格式，Nova创建虚拟机时不支持clone操作，因此必须从Glance中下载镜像。这就是为什么Glance使用Ceph存储时，镜像必须转化为raw格式的原因。

#### 1. 上传镜像

```
rbd -p ${GLANCE_POOL} create --size ${SIZE} ${IMAGE_ID}
rbd -p ${GLANCE_POOL} snap create ${IMAGE_ID}@snap
rbd -p ${GLANCE_POOL} snap protect ${IMAGE_ID}@snap
```

#### 2. 删除镜像

```
rbd -p ${GLANCE_POOL} snap unprotect ${IMAGE_ID}@snap
rbd -p ${GLANCE_POOL} snap rm ${IMAGE_ID}@snap
rbd -p ${GLANCE_POOL} rm ${IMAGE_ID}
```

## 五、 Nova

#### 1 创建虚拟机

```
rbd clone ${GLANCE_POOL}/${IMAGE_ID}@snap ${NOVA_POOL}/${SERVER_ID}_disk
```

#### 2 创建虚拟机快照

```
# Snapshot the disk and clone it into Glance's storage pool
rbd -p ${NOVA_POOL} snap create ${SERVER_ID}_disk@${RANDOM_UUID}
rbd -p ${NOVA_POOL} snap protect ${SERVER_ID}_disk@${RANDOM_UUID}
rbd clone ${NOVA_POOL}/${SERVER_ID}_disk@${RANDOM_UUID} ${GLANCE_POOL}/${IMAGE_ID}
# Flatten the image, which detaches it from the source snapshot
rbd -p ${GLANCE_POOL} flatten ${IMAGE_ID}
# all done with the source snapshot, clean it up
rbd -p ${NOVA_POOL} snap unprotect ${SERVER_ID}_disk@${RANDOM_UUID}
rbd -p ${NOVA_POOL} snap rm ${SERVER_ID}_disk@${RANDOM_UUID}
# Makes a protected snapshot called 'snap' on uploaded images and hands it out
rbd -p ${GLANCE_POOL} snap create ${IMAGE_ID}@snap
rbd -p ${GLANCE_POOL} snap protect ${IMAGE_ID}@snap
```

#### 3 删除虚拟机

```
for image in $(rbd -p ${NOVA_POOL} ls | grep "^${SERVER_ID}");
    do rbd -p ${NOVA_POOL} rm "$image";
done
```

## 六、 Cinder

#### 1 创建volume

(1) 创建空白卷

```
rbd -p ${CINDER_POOL} create --new-format --size ${SIZE} volume-${VOLUME_ID}
```

(2) 从快照中创建

```
rbd clone \
${CINDER_POOL}/volume-${SOURCE_VOLUME_ID}@snapshot-${SNAPSHOT_ID} \
${CINDER_POOL}/volume-${VOLUME_ID}
rbd resize --size ${SIZE} openstack/volume-${VOLUME_ID}
```

(3) 从volume中创建

```
# Do full copy if rbd_max_clone_depth <= 0.
if [[ "$rbd_max_clone_depth" -le 0 ]]; then rbd copy \
    ${CINDER_POOL}/volume-${SOURCE_VOLUME_ID} ${CINDER_POOL}/volume-${VOLUME_ID}
    exit 0
fi
# Otherwise do COW clone.
# Create new snapshot of source volume
rbd snap create \
${CINDER_POOL}/volume-${SOURCE_VOLUME_ID}@volume-${VOLUME_ID}.clone_snap
rbd snap protect \
${CINDER_POOL}/volume-${SOURCE_VOLUME_ID}@volume-${VOLUME_ID}.clone_snap
# Now clone source volume snapshot
rbd clone \
${CINDER_POOL}/volume-${SOURCE_VOLUME_ID}@volume-${VOLUME_ID}.clone_snap \
${CINDER_POOL}/volume-${VOLUME_ID}
# If dest volume is a clone and rbd_max_clone_depth reached,
# flatten the dest after cloning.
depth=$(get_clone_depth ${CINDER_POOL}/volume-${VOLUME_ID})
if [[ "$depth" -ge "$rbd_max_clone_depth" ]]; then
    # Flatten destination volume
    rbd flatten ${CINDER_POOL}/volume-${VOLUME_ID}
    # remove temporary snap
    rbd snap unprotect \
    ${CINDER_POOL}/volume-${SOURCE_VOLUME_ID}@volume-${VOLUME_ID}.clone_snap
    rbd snap rm \
    ${CINDER_POOL}/volume-${SOURCE_VOLUME_ID}@volume-${VOLUME_ID}.clone_snap
fi
```

(4) 从镜像中创建

```
rbd clone ${GLANCE_POOL}/${IMAGE_ID}@snap ${CINDER_POOL}/volume-${VOLUME_ID}
if [[ -n "${SIZE}" ]]; then rbd resize --size ${SIZE} ${CINDER_POOL}/volume-${VOLUME_ID}
fi
```

#### 2 创建快照

```
rbd -p ${CINDER_POOL} snap create volume-${VOLUME_ID}@snapshot-${SNAPSHOT_ID}
rbd -p ${CINDER_POOL} snap protect volume-${VOLUME_ID}@snapshot-${SNAPSHOT_ID}
```

#### 3 创建备份

(1) 第一次备份

```
rbd -p ${BACKUP_POOL} create --size \
${VOLUME_SIZE} volume-${VOLUME_ID}.backup.base
NEW_SNAP=volume-${VOLUME_ID}@backup.${BACKUP_ID}.snap.${TIMESTAMP}
rbd -p ${CINDER_POOL} snap create ${NEW_SNAP}
rbd export-diff ${CINDER_POOL}/volume-${VOLUME_ID}${NEW_SNAP} - \
| rbd import-diff --pool ${BACKUP_POOL} - volume-${VOLUME_ID}.backup.base
```

(2) 增量备份

```
rbd -p ${CINDER_POOL} snap create \
volume-${VOLUME_ID}@backup.${BACKUP_ID}.snap.${TIMESTAMP}
rbd export-diff  --pool ${CINDER_POOL} \
--from-snap backup.${PARENT_ID}.snap.${LAST_TIMESTAMP} \
${CINDER_POOL}/volume-${VOLUME_ID}@backup.${BACKUP_ID}.snap.${TIMESTRAMP} - \
| rbd import-diff --pool ${BACKUP_POOL} - \
${BACKUP_POOL}/volume-${VOLUME_ID}.backup.base
rbd -p ${CINDER_POOL} snap rm \
volume-${VOLUME_ID}.backup.base@backup.${PARENT_ID}.snap.${LAST_TIMESTAMP}
```

#### 4 备份恢复

```
rbd export-diff --pool ${BACKUP_POOL} \
volume-${SOURCE_VOLUME_ID}.backup.base@backup.${BACKUP_ID}.snap.${TIMESTRAMP} - \
| rbd import-diff --pool ${CINDER_POOL} - volume-${DEST_VOLUME_ID}
rbd -p ${CINDER_POOL} resize --size ${new_size} volume-${DEST_VOLUME_ID}
```
