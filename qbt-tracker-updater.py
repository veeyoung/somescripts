#!/usr/bin/env python
#Ref: https://www.52pojie.cn/thread-1776097-1-1.html
import os
import requests

append = False
 
# 获取当前用户的目录
USER_DIR = os.path.expanduser("~")
# qBittorrent 的设置保存目录
QB_DIR = os.path.join(USER_DIR, ".config", "qBittorrent")
# qBittorrent 配置文件的路径
CONFIG_FILE = os.path.join(QB_DIR, "qBittorrent.conf")
# Tracker 列表地址
TRACKER_URL = "https://cf.trackerslist.com/all.txt"
 
# 读取 Tracker 列表
r = requests.get(TRACKER_URL)
trackers = r.text.split("\n")
# 去除空行和注释
trackers = [t.strip() for t in trackers if t and not t.startswith("#")]
 
# 如果 qBittorrent 的设置保存目录不存在，则创建该目录
if os.path.exists(CONFIG_FILE):
    # 更新 qBittorrent 的 Tracker 列表
    with open(CONFIG_FILE, "r") as f:
        lines = f.readlines()
    
    with open(CONFIG_FILE, "w") as f:
        for line in lines:
            # 找到 Session\AdditionalTrackers= 选项所在的行，并在该行的末尾添加 Tracker 列表
            if line.strip().startswith("Session\AdditionalTrackers="):
                if not append:
                    line = "Session\AdditionalTrackers="
                line = line.strip()
                if line.endswith(";"):
                    line = line[:-1]
                line += "\\n".join(trackers)
                f.write(line + "\n")
            else:
                f.write(line)
# 提示信息
print("提示", "Tracker 列表更新成功！") 
