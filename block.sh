#!/bin/bash

# 安装和配置安全脚本

function install_and_configure_security_script() {
    # 安装脚本
    cat << 'EOF' > /usr/local/bin/security_script
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
EOF

    chmod +x /usr/local/bin/security_script

    # 添加定时任务，每小时执行一次
    (crontab -l ; echo "0 * * * * /usr/local/bin/security_script") | crontab -

    echo "安装完成。"
}

# 执行安装和配置
install_and_configure_security_script
