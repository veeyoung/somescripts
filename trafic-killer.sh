#!/bin/sh
while true
do
    for killer in "http://dldir1.qq.com/qqfile/qq/QQNT/feb78c41/linuxqq_3.2.5-21159_x86_64.AppImage" \
        "http://issuecdn.baidupcs.com/issue/netdisk/apk/BaiduNetdiskSetup_wap_share.apk" \
        "http://gedown.360safe.com/gc/signed_com.360.browser-stable_13.3.1010.231-1_amd64.deb" \
        "http://ssl-hw-pc.ludashi.com/pc/appstore/website_products/AImark.apk" \
        "http://static.ffzww.com/download/flashcenter/FlashCenter_Site_Setup.exe"
    do
        wget $killer -O /dev/null && sleep 1 || sleep 5
    done
done

