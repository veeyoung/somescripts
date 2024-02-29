#!/usr/bin/env python
# visit https://tool.lu/pyc/ for more information
# Version: Python 3.6

import requests
import re
import time
import os
import random
requests.packages.urllib3.disable_warnings()
import chardet

def make_txt(data):
    f = open('%s%s%s.txt' % (path, os.sep, time.strftime('%Y%m%d', time.localtime(time.time()))), 'a', 'utf-8', **('encoding',))
    f.write('央视,#genre#\n')
    for line in data[0]:
        f.write(f'''{line}\n''')

    f.write('卫视,#genre#\n')
    for line in data[1]:
        f.write(f'''{line}\n''')

    f.write('地方,#genre#\n')
    for line in data[2]:
        f.write(f'''{line}\n''')

    f.close()


def url_test(url):

    try:
        if 'https' not in url and 'udp' not in url:
            rsp = requests.get(url, headers, 3, **('headers', 'timeout')).status_code
            if int(rsp) == 200:
                print(f'''连接测试 {url}  状态码:{rsp} 有效连接！''')
                return True
            None(f'''连接测试 {url}  无效连接！''')
            return False
        return False
    except:
        print(f'''连接测试 {url}  无效连接！''')
        return False
        return None



def main(ipport):
    ys = []
    ws = []
    df = []
    headers['accept-language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
    headers['Referer'] = f'''https://www.foodieguide.com/iptvsearch/hotellist.html?s={ipport}%3A18888&Submit=+'''
    rsp = requests.get(f'''https://www.foodieguide.com/iptvsearch/alllist.php?s={ipport}''', False, headers, **('url', 'verify', 'headers'))
    rsp = rsp.content.decode(chardet.detect(rsp.content)['encoding'])
    channel = re.findall('left;">(.*?)</div>', rsp)
    m3u8url = re.findall('copyto\\("(.*?)"\\)', rsp)
    number = len(m3u8url)
    if number != 0:
        print(f'''获取IP {ipport}频道数:{number}个！''')
        print('检查频道是否有效?')
    else:
        print(f'''失效地址：{ipport}''')
    result = []
    if number >= 3:
        for index in range(3):
            if 'rtp' not in m3u8url[index] and 'rtsp' not in m3u8url[index] and 'udp' not in m3u8url[index]:
                if url_test(m3u8url[index]):
                    result.append(True)
                    break
                else:
                    result.append(False)
                continue
            result.append(True)

    if result != [
        False,
        False,
        False]:
        data = list(zip(channel, m3u8url))
        for line in data:
            line = '%s,%s' % (line[0], line[1])
            line = line.replace('/udp//', '/udp/').replace('/rtp//', '/rtp/').replace('/rtsp//', '/rtsp/')
            print(f'''当前地址:{line}''')
            if 'CCTV' in line.upper() and '中央' in line.upper() or 'CETV' in line.upper():

                try:
                    (name, url) = line.split(',')
                    name = re.findall('\\w\\w\\w\\w\\d{1,2}|\\w\\w\\w\\w-\\d{1,2}|\\w\\w\\w\\w-\\w{1,4}|\\w\\w\\w\\w\\w{1,8}|中央\\d{1,2}', name)[0]
                    name = name.replace('-', '').replace('高清', '').replace('HD', '').replace('-CM-IPTV', '').replace('-Tel', '').replace(' ', '').replace('标清', '').replace('中央', 'CCTV')
                    ys.append(f'''{name},{url}''')
                except:
                    continue

            elif '卫视' in line.upper():
                line = line.replace('高清', '').replace('HD', '').replace('-CM-IPTV', '').replace('-Tel', '').replace(' ', '').replace('+', '').replace('标清', '').replace('-', '')
                ws.append(line)
            elif '<br>' not in line.upper():
                line = line.replace('高清', '').replace('HD', '').replace('-CM-IPTV', '').replace('-Tel', '').replace(' ', '').replace('+', '').replace('标清', '').replace('YD', '').replace('-', '')
                df.append(line)
            else:
                print(f'''错误类别地址:不写入 {line}''')

    if len(ys) != 0 and len(ws) != 0 or len(df) != 0:
        print('当前共计获取到节目   YS:%d个  WS:%d个  DF:%d个' % (len(ys), len(ws), len(df)))
        make_txt((ys, ws, df))


def run():
    url = 'https://www.foodieguide.com/iptvsearch/'
    rsp = requests.get(url, headers, False, 30, **('url', 'headers', 'verify', 'timeout'))
    info = re.findall('href="(.*?\\d{1,4}\\.\\d{1,4}\\.\\d{1,4}\\.\\d{1,4})"', rsp.text)
    for link in info:
        rsp = requests.get(f'''{url}''' + link, 30, False, **('url', 'timeout', 'verify')).text
        data = set(re.findall('\\d{1,4}\\.\\d{1,4}\\.\\d{1,4}\\.\\d{1,4}:\\d{1,5}', rsp))
        for line in data:
            if line not in used_list:
                used_list.append(line)
                sleep_time = float(random.uniform(0, 5))
                time.sleep(sleep_time)

                try:
                    main(line)
                except Exception:
                    e = None

                    try:
                        print(f'''ERROR:{e}''')
                    finally:
                        e = None
                        del e



            print(f'''{line}该地址已经获取过了不再获取，请等待地址更新...''')




def get_pwd():
    rsp = requests.get('http://120.79.4.185/passwd/autoscan', **('url',)).text
    return rsp.strip()

if __name__ == '__main__':
    path = os.path.dirname(sys.executable)
    used_list = []
    print('-' * 50)
    print('直接或间接使用本仓库或者软件内容的个人和组织，仅仅用作学习交流！\n应在24小时内完成学习和研究，并及时删除！！\n数据接口均来自于互联网，禁止商业行为，一切与商业有关违法行为与本人无关\n')
    print('-' * 50)
    print('不要长时间运行，容易导致ip被封，之后无法运行，限制运行次数最大10次')
    print('-' * 50)
    print('防失联关注公众号【码点小干货】，后续持续更新相关教程和工具')
    print('防止滥用，一段时间会更新一次密码！密码到公众号【码点小干货】获取，回复【240229】获取工具和密码')
    print('若无法使用，可能是源站点有更新，程序需要适配更新')
    print('-' * 50)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36' }
    passwd = input('请输入运行密码！')
    if True:

        try:
            number = int(input('请输入运行次数:\n'))
        except:

            try:
                number = int(input('请输入数字！重新输入:\n'))
            except:
                print('依旧输出错误！默认1次获取！')
                nmuber = 1


        if number >= 10:
            number = 10
        for i in range(1, number + 1):

            try:
                print(f'''({i}/%d)正在进行当前时间点 %s 数据的爬取...''' % (number + 1, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
                run()
            except Exception:
                e = None

                try:
                    print(f'''ERROR:{e} 可能被限制了，请等待一段时间再运行！''')
                finally:
                    e = None
                    del e

            finally:
                print(f'''({i}/%d)运行完成，等待600秒后将再次运行！请勿关闭窗口\n输出文件为当前文件夹下的:%s.txt\n下次运行数据将持续写入到当前文件中''' % (number + 1, time.strftime('%Y%m%d', time.localtime(time.time()))))
                time.sleep(600)


    else:
        input('密码错误! 回车结束，获取密码到公众号【码点小干货】中回复【240229】获取工具和密码')
