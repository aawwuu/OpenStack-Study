#! /bin/bash

ip_prefix="36.111.0"

list_floating_ip()
{
    if [ -n $(openstack floating ip list -f value -c ID) ];then
        echo "*******************************************************************"
        echo "floating ip"
        echo "*******************************************************************"
        # Active floating ip
        echo "ip    server_id   server_name     host"
        openstack server list --all --long -f value -c ID -c Name  -c Networks -c Host | awk '/'${ip_prefix}'/ {print $4,$1,$2,$5}' | column -t

        # Down floating ip
        if [ -n $(openstack floating ip list -f value --status "DOWN") ];then
            echo "*************"
            echo "Floating ip which status is DOWN"
            echo "ip project_id"
            openstack floating ip list -c "Floating IP Address" -c "Project" -c "Status" --status "DOWN"
        fi
    else
        echo "No floating ip in use"
    fi
}


list_router_gateway()
{
    if [ -n $(openstack port list --long -c ID --device-owner network:router_gateway -f value | wc -l) ];then
        openstack router list --long -c Project -c "External gateway info" -f value | \
        awk '/'${ip_prefix}'/ {print $1,$10}' | awk -F "\"" '{print $2,$1}' | column -t > router_gateway.txt
        echo "*******************************************************************"
        echo "router_gateway"
        echo "*******************************************************************"
        echo "ip        project_id              project_name"

        while read ip project_id;do
            printf "$ip \t $project_id \t"
            openstack project show $project_id -f value -c name
        done < router_gateway.txt
        rm -f router_gateway.txt
    else
        echo "No router gateway"
    fi
}


list_floatingip_agent_gateway()
{
    echo "\n *******************************************************************"
    echo "floatingip_agent_gateway"
    echo "*******************************************************************"
    openstack port list --long -c ID -c "Fixed IP Addresses" -c Status -c "Device Owner" --device-owner network:floatingip_agent_gateway
    for i in $(openstack port list --long -c "ID" -f value --device-owner network:floatingip_agent_gateway);do
        openstack port show $i -f value -c binding_host_id -c fixed_ips | xargs; done | awk '{print $2,$1}' | sort
    done
}

list_floating_ip
list_router_gateway
list_floatingip_agent_gateway