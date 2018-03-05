#! /bin/bash

create_backups()
{
    #批量创建备份，只对数据盘创建备份，忽略系统盘（系统盘name为空）
    for i in $(openstack volume list -f value -c Name | sort -r | uniq -u); do
        openstack volume backup create --force --name ${i}_backup1 $i
    done
}

restore_backups()
{
    #批量恢复
    openstack volume backup list --long -f value -c ID -c Volume | while read ID Volume; do
        openstack volume backup restore ${ID} ${Volume}
    done
}


openstack volume backup list --long -f value -c ID -c Name -c Volume | grep backup2 | while read ID Name Volume; do
    openstack volume backup restore ${ID} ${Volume}
done
