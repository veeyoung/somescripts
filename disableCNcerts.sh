#!/usr/bin/doas /bin/bash

# 证书标签列表
cert_labels=(
    "BJCA Global Root CA1"
    "CFCA EV ROOT"
    "GDCA TrustAUTH R5 ROOT"
    "Hongkong Post Root CA 3"
)

# 遍历证书标签列表
for cert_label in "${cert_labels[@]}"; do
    # 使用 trust list 命令获取证书列表
    cert_info=$(trust list | grep -B 3 "label: $cert_label")
    # 从证书信息中提取证书 ID
    cert_id=$(echo "$cert_info" | grep -oP '(?<=pkcs11:id=)[^;]+')
    # 如果找到了证书 ID
    if [ -n "$cert_id" ]; then
        rm -f "/etc/ca-certificates/trust-source/blocklist/${cert_label}.pem"
        # 将证书 ID 添加到黑名单
        trust extract --format=pem-bundle --filter="pkcs11:id=$cert_id;type=cert" "/etc/ca-certificates/trust-source/blocklist/${cert_label}.pem"
        echo "已将证书 $cert_label 添加到黑名单"
    else
        echo "未找到证书 $cert_label"
    fi
done

# 更新证书缓存
update-ca-trust

echo "已将所有证书添加到黑名单并更新证书缓存"
