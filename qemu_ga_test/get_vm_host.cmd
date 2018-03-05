#!/bin/bash

function get_vm_host() 
{
    openstack server list --long --project $project --status active -f value -c ID -c Host
}
project=PROJECT_REPLACE
source ADMIN_OPENRC
get_vm_host