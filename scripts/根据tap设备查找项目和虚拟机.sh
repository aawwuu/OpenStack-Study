#! /bin/sh

tap=$1
port_id=$(openstack port list -f value -c ID | grep ${tap})
project_id=$(openstack port show ${port_id} -c project_id -f value)

fixed_ip=$(openstack port show ${port_id} -c fixed_ips  -f value | awk -F "'" '{print $2}')
instance_id=$(openstack server list --project ${project_id} -f value | grep ${fixed_ip} | awk '{print $1}')

echo "project_id:   $project_id"
echo "instance_id:  $instance_id"