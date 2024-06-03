#!/bin/bash
interface="wlan0"
echo "Enter network:"
read subnet
# 数组存储有响应的 IP 地址
responsive_ips=()


# 将有响应的 IP 地址保存到数组并输出
while IFS= read -r ip; do
  responsive_ips+=("$ip")
  echo "$ip"
done < <(for ip in $(seq 1 254); do
    (if \ping -c 1 -W 1 $subnet.$ip | grep -q "64 bytes"; then echo "$subnet.$ip"; fi) &
  done; wait)

# 遍历数组中的 IP 地址并执行 arping 命令
#for ip in "${responsive_ips[@]}"; do
#  sudo arping -I $interface -c 1 $ip
#done

# 等待 ARP 请求完成
sleep 5

# 查看 ARP 缓存
grep -v "00:00:00:00:00:00" /proc/net/arp
