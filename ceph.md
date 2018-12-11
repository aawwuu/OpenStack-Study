# ceph运维命令总结

## 一、查看状态信息

ceph osd 使用率

```shell
# ceph df
# ceph osd df
```

ceph 健康状态

```
# ceph osd tree						#查看所有磁盘
# ceph osd pool get rbd size		#查看ceph副本数
# ceph -s							#查看ceph状态，正常所有osdmap是up和in，pgmap是active+clean
# ceph -w
```

查看pool

```
# ceph osd lspools
# ceph osd pool ls
# rados lspools
```

ceph 进程

```
sudo systemctl status ceph-osd.target
sudo systemctl status ceph-mon.target
sudo systemctl status ceph-mds.target
```

查看rbd

```
rbd -p $pool_name ls -l							# rbd 列表
rbd -p $pool_name children $image_name			# 子image
rbd info $pool_name/image_name							# 详细信息
rbd du $image_name								# 实际占用空间
```

ceph在openstack中使用rbd管理块设备，在ceph中称为image，openstack中叫volume。image都放在pool中，不同的pool可以定义不同的副本数、pg数、放置策略等。image的命名一般是`pool_name/image_name@snap`形式。

如果镜像为非raw格式，Nova创建虚拟机时不支持clone操作，因此必须从Glance中下载镜像。这就是为什么Glance使用Ceph存储时，镜像必须转化为raw格式的原因。

## 二、Glance

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

## 三、 Nova

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

## 四、 Cinder

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



systemctl stop ceph-osd@{osd.num} 