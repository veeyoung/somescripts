#!/bin/bash

function security() {
    # 设置要监控的登录失败次数，超过该次数则会被阻止
    MAX_ATTEMPTS="$1"

    # 获取所有登录失败的IP并计数
    IP_COUNT=$(lastb | awk '{print $3}' | sort | uniq -c | awk '$1 >= '$MAX_ATTEMPTS' {print $2}')

    # 遍历所有登录失败次数超过阈值的IP并将其阻止
    for IP in ${IP_COUNT}
    do
        # 检查IP是否已经在iptables策略中
        if ! iptables -C INPUT -s $IP -j DROP &> /dev/null; then
            echo "`date +"%F %H:%M:%S"`  阻止 $IP，登录失败次数超过 $MAX_ATTEMPTS 次。"
            iptables -A INPUT -s $IP -j DROP
        else
            echo "`date +"%F %H:%M:%S"`  $IP 已经被阻止。" > /dev/null 2>&1
        fi
    done
}

# 调用函数并传入最大登录失败次数参数
security 5

