#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: chaichunyang@outlook.com
# https://github.com/chaichunyang/m3u-tester

import json
import os
import sys
import time
from urllib.request import urlopen
import signal

flag = True

def signal_handler(signal, frame):
    global flag
    flag = False

class Item:
    def __init__(self, extinf, url):
        self.extinf = extinf
        self.url = url
        self.speed = -1

    def __json__(self):
        return {'extinf': self.extinf, 'url': self.url, 'speed': self.speed}


class ItemJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__json__"):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


class Downloader:
    def __init__(self, url):
        self.url = url
        self.startTime = time.time()
        self.recive = 0
        self.endTime = None

    def getSpeed(self):
        if self.endTime and self.recive != -1:
            return self.recive / (self.endTime - self.startTime)
        else:
            return -1


def getAllM3UItems(dir):
    print('获取 %s 目录下的".m3u"文件...' % dir)
    files = []
    filenames = os.listdir(dir)
    pathnames = [os.path.join(dir, filename) for filename in filenames]
    for file in pathnames:
        if file.endswith('.m3u') and os.path.isfile(file):
            files.append(file)
    # 解析m3u文件
    items = []
    for file in files:
        with open(file, 'r+', encoding='utf-8') as f:
            extinf = ''
            for line in f:
                if line.startswith('#EXTM3U'):
                    continue
                if extinf:
                    items.append(Item(extinf.strip(), line.strip()))
                    extinf = ''
                if line.startswith('#EXTINF'):
                    extinf = line
    return items


def getStreamUrl(m3u8):
    urls = []
    try:
        prefix = m3u8[0:m3u8.rindex('/') + 1]
        with urlopen(m3u8, timeout=2) as resp:
            top = False
            second = False
            firstLine = False
            for line in resp:
                line = line.decode('utf-8')
                line = line.strip()
                # 不是M3U文件，默认当做资源流
                if firstLine and not '#EXTM3U' == line:
                    urls.append(m3u8)
                    firstLine = False
                    break
                if top:
                    # 递归
                    if not line.lower().startswith('http'):
                        line = prefix + line
                    urls += getStreamUrl(line)
                    top = False
                if second:
                    # 资源流
                    if not line.lower().startswith('http'):
                        line = prefix + line
                    urls.append(line)
                    second = False
                if line.startswith('#EXT-X-STREAM-INF:'):
                    top = True
                if line.startswith('#EXTINF:'):
                    second = True
            resp.close()
    except BaseException as e:
        if log:
            print('get stream url failed! %s' % e)
    return urls


def downloadTester(downloader: Downloader):
    chunck_size = 10240
    try:
        with urlopen(downloader.url, timeout=2) as resp:
            # max 5s
            while(time.time() - downloader.startTime < 5):
                chunk = resp.read(chunck_size)
                if not chunk:
                    break
                downloader.recive = downloader.recive + len(chunk)
    except BaseException as e:
        if log:
            print("downloadTester got an error %s" % e)
        downloader.recive = -1
    downloader.endTime = time.time()


def start():
    global flag
    path = os.getcwd()
    items = getAllM3UItems(path)
    if not len(items):
        print('没有找到任何源，退出。')
        sys.exit(0)
    print('发现项: %d' % len(items))
    # 循环测速
    i = 0
    for item in items:
        if not flag:
            break
        i += 1
        idx = item.extinf.rindex(',') + 1
        if log:
            print('测试：%s' % item.extinf[idx:])
        else:
            print("\r", end="")
            print("测试进度: {}%: ".format(i * 100 // len(items)), "▓" * (i * 50 // len(items)), end="")
            sys.stdout.flush()
        url = item.url
        stream_urls = []
        if url.lower().endswith('.flv'):
            stream_urls.append(url)
        else:
            stream_urls = getStreamUrl(url)
        # 速度默认-1
        speed = -1
        if len(stream_urls) > 0:
            if log:
                for stream in stream_urls:
                    print('\t流：%s' % stream)
            stream = stream_urls[0]
            downloader = Downloader(stream)
            downloadTester(downloader)
            speed = downloader.getSpeed()
        item.speed = speed
        if log:
            print('\t速度：%d bytes/s' % item.speed)

    if save_josn:
        try:
            # 包含测试结果，存入json
            with open('result.json', 'w+', encoding='utf-8') as f:
                json.dump(items, f, cls=ItemJSONEncoder)
        except BaseException as e:
            print('保存json失败 %s' % e)

    # 优质资源写入新文件
    with open('excellent.m3u', 'w+', encoding='utf-8') as f:
        print('#EXTM3U', file=f)
        for item in items:
            # 速度大于1MB
            if item.speed > output_speed * 1024:
                print(item.extinf, file=f)
                print(item.url, file=f)


save_josn = False
log = False
output_speed = 800
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    start()
