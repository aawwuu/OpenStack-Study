#! /bin/bash

#set -ex

current_dir=$(cd $(dirname "$0") && pwd)
cd $current_dir
source $current_dir/init.conf

function usage()
{
    printf "\033[31m Please enter project name or id\n\033[0m"
    printf "usage: $0 <project> \n\n"
}

function get_vm_host()
{
    eval sed -i 's:ADMIN_OPENRC:${admin_openrc}:' $current_dir/get_vm_host.cmd
    eval sed -i 's:PROJECT_REPLACE:$project:' $current_dir/get_vm_host.cmd
    ssh $controller -l root "$(cat $current_dir/get_vm_host.cmd)" | sort -k2 > $current_dir/vm.txt
    if [ ! -s vm.txt ]; then
        printf "\033[31m Project $project has no instance\n\033[0m"
    exit 0
    fi
}

function check_qga()
{
    prefix=$(hostname | awk -F "e" '{print $1"."$2"."$3"."}')
    while read vm host; do
        suffix=${host##*e}
        host="${prefix}""${suffix}"
        eval sed -i 's/vm=VMID/vm=$vm/' $current_dir/qga_test.cmd
        printf "${host} \t"
        ssh $host -l root "$(cat qga_test.cmd)" < /dev/null
        eval sed -i 's/vm=$vm/vm=VMID/' $current_dir/qga_test.cmd
    done <vm.txt
}

function recover_configuration()
{
    eval sed -i 's:"${admin_openrc}":ADMIN_OPENRC:' $current_dir/get_vm_host.cmd
    eval sed -i 's:project=$project:project=PROJECT_REPLACE:' $current_dir/get_vm_host.cmd
    rm -f $current_dir/vm.txt
}

project=$1
[[ "${project}x" == "x" ]] && usage && exit 0

printf "Start checking Project ${project} .......""\n"
get_vm_host
printf %.s= {1..100}
printf "\n"
printf "    HOST\t\t\tID\t\t\tQEMU-GA\t    NETWORK\t\t HOSTNAME\n"
check_qga
recover_configuration
printf %.s= {1..100}
printf "\n"