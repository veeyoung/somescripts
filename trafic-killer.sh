#!/bin/sh

default_timeout_seconds=0
timeout_seconds="${1:-$default_timeout_seconds}"
start_time=$(date +%s)
UA="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
# 检查wget是否支持--limit-rate参数
if wget --help | grep -q -- "--limit-rate"; then
    LIMIT="--limit-rate=10m"
else
    LIMIT=""
fi
# 检查wget是否支持-t参数
if wget --help | grep -q -- "-t"; then
    TIME="-t2"
else
    TIME=""
fi

while true
do
    for killer in "http://dldir1.qq.com/qqfile/qq/QQNT/feb78c41/linuxqq_3.2.5-21159_x86_64.AppImage" \
        "http://issuecdn.baidupcs.com/issue/netdisk/apk/BaiduNetdiskSetup_wap_share.apk" \
        "http://gedown.360safe.com/gc/signed_com.360.browser-stable_13.3.1010.231-1_amd64.deb" \
        "http://www.kcna.kp/siteFiles/video/kp/202402/VID0003975.mp4" \
        "http://static.ffzww.com/download/flashcenter/FlashCenter_Site_Setup.exe" \
        "http://api.zhihu.com/client/download/zhihuwap"
    do
        wget "$killer" -U "$UA" "$LIMIT" --no-check-certificate --timeout=10 "$TIME" -O /dev/null && sleep 1 || sleep 5
    done

    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [ "$elapsed_time" -ge "$timeout_seconds" ]; then
        echo "Done"
        exit 0
    fi

done
