#! /bin/bash

PROJECT_NAME=($project_name test_project)
USER_NAME=($PROJECT_NAME test_project)
USER_PASSWORD=($PROJECT_NAME test_project)
external_network=($ext_net ext-net)

current_dir=$(cd $(dirname "$0") && pwd)
cd $current_dir
[[ ! -s ${current_dir}/admin_openrc ]] &&  echo "!!!!! error admin_openrc !!!!!" && exit 1
admin_openrc="${current_dir}/admin_openrc"


create_project()
{
    project_id=$(openstack project create -f value -c id $PROJECT_NAME)
    user_id=$(openstack user create -f value -c id --project $PROJECT_NAME --password $USER_PASSWORD $USER_NAME)
    openstack role add --user $user_id --project $PROJECT_NAME user
    project_openrc="${current_dir}/${PROJECT_NAME}_openrc"
    echo "
    +--------------+------------------------------------------+
    PROJECT NAME   |  $PROJECT_NAME
    PROJECT ID     |  $project_id
    USER NAME      |  $USER_NAME
    USER ID        |  $user_id
    OPENRC FILE    |  $project_openrc
    +--------------+------------------------------------------+
    "
    # create project_openrc file
    cat >> ${current_dir}/${PROJECT_NAME}_openrc << EOF
    export OS_PROJECT_DOMAIN_NAME=default
    export OS_USER_DOMAIN_NAME=default
    export OS_PROJECT_NAME=$PROJECT_NAME
    export OS_USERNAME=$USER_NAME
    export OS_PASSWORD=$USER_PASSWORD
    export OS_AUTH_URL=$OS_AUTH_URL
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2
    EOF
}

create_network()
{
    # create router
    router_id=$(openstack router create -f value -c id ${PROJECT_NAME}_router)
    openstack router set --external-gateway $external_network $router_id

    # create network
    net_id=$(openstack network create -f value -c id ${PROJECT_NAME}_net)
    subnet_id=$(openstack subnet create --subnet-range 10.10.10.0/24 --network $net_id \
                --dns-nameserver 114.114.114.114 -f value -c id ${PROJECT_NAME}_subnet)
    openstack router add subnet $router_id $subnet_id

    # create security group rule
    openstack security group rule create --remote-ip 0.0.0.0/0 \
        --ingress --protocol tcp --dst-port 22:22 default
    openstack security group rule create --remote-ip 0.0.0.0/0 --ingress --protocol icmp default
}

create_keypair()
{
    echo "keypair file : ${PROJECT_NAME}_key"
    openstack keypair create ${PROJECT_NAME}_key 2>&1 | tee ${PROJECT_NAME}_key
}

source $admin_openrc
create_project
source $project_openrc
create_network
create_keypair

################################################################################
################################################################################

#! /bin/bash

current_dir=$(cd $(dirname "$0") && pwd)
cd $current_dir
[[ ! -s ${current_dir}/admin_openrc ]] &&  echo "!!!!! error admin openrc !!!!!" && exit 1
[[ ! -s ${current_dir}/${PROJECT_NAME}_openrc ]] &&  echo "!!!!! error project openrc !!!!!" && exit 1
admin_openrc="${current_dir}/admin_openrc"
project_openrc="${current_dir}/${PROJECT_NAME}_openrc"


create_server()
{
    project=$name
    user=$name
    vmpass=password
    conf="${current_dir}/conf/${name}.cfg"
    source $admin_openrc
    openstack role add --user $user --project $project admin
    source ${name}_rc
    while read net vmname flavor image fix_ip fip host; do
        nova boot \
        --flavor $flavor \
        --security-group default \
        --availability-zone nova:$host  \
        --nic net-id=$net,v4-fixed-ip=$fix_ip \
        --block-device id=$image,source=image,dest=volume,volume_type=default,bootindex=0,size=100,shutdown=remove \
        --meta admin_pass=$vmpass \
        --meta vif_model=virtio \
        $vmname
        openstack floating ip create --floating-ip-address $fip $external_network
        openstack server add floating ip $vmname $fip
    done < $conf
    source admin_openrc
    openstack role remove --user $user --project $project admin
}

for name in {project1,project2,project3,project4,project5}; do
    create_server
done