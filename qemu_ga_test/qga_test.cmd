#! /bin/bash

function check_qga()
# check qemu-ga
{
    qemu_ga=$(virsh qemu-agent-command ${vm} '{"execute": "guest-ping"}' 2>/dev/null)
    [[ "${qemu_ga}x" == "x" ]] && printf "\033[31m ${vm}\t inactive\n\033[0m" && exit 0
    printf "\033[32m ${vm}\t active\t\033[0m"
}

function check_ip()
# check ip addess
{
    ip=$(virsh qemu-agent-command ${vm} '{"execute":"guest-network-get-interfaces"}' | python -mjson.tool | grep -B 1  "\"ip-address-type\": \"ipv4\"" | grep "\"ip-address\":" | grep -v "127.0.0.1" | sed 's/"/ /g' | awk '{print $3}')
    if [ -z $ip ]; then
        printf "\033[31m none\t\t\t\033[0m"
    else
        printf "\033[32m $ip\t\t\033[0m"
    fi
}

function check_hostname()
# check hostname
{
    pid=$(virsh qemu-agent-command ${vm} '{"execute":"guest-exec", "arguments":{"path":"cat","arg":["/etc/hostname"],"capture-output":true}}' | python -mjson.tool | grep pid | awk '{print $2}')
    hostname=$(virsh qemu-agent-command ${vm} '{"execute":"guest-exec-status", "arguments":{"pid":'${pid}'}}' | python -mjson.tool | grep out-data | awk '{print $2}' | sed 's/"//g')
    hostname=$(printf ${hostname} | base64 -d)
    if [ $hostname == host-*-*-*-* ]; then
        printf "\033[31m ${hostname}\n\033[0m"
    elif [ $hostname == "unassigned-hostname" ]; then
        printf "\033[31m ${hostname}\n\033[0m"
    else
        printf "\033[32m ${hostname}\n\033[0m"
    fi
}

vm=VMID
check_qga
check_ip
check_hostname