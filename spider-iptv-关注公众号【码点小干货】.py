from datetime import datetime
from bs4 import BeautifulSoup
import re,os
import time
import socket
import json
import requests
import subprocess
from requests.exceptions import RequestException
socket.setdefaulttimeout(5.0)

class Tools(object):

    def __init__(self):
        pass

    # 校验是否为ip地址
    def check_ip(self, ip):
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return bool(re.match(pattern, ip))

    # 检查URL的有效性
    def check_url(self, url, timeout):
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            return response.status_code == 200
        except RequestException:
            return False

    # 检查IPTV的有效性
    def check_iptv(self, url, delay):
        try:
            rsp = requests.get(url=url,timeout=delay)
            if rsp.status_code == 200:
                return True
        except:
            return False

    # 解析IPTV分辨率等信息
    def get_ffprobe_info(self, url):
        command = ['ffprobe', '-print_format', 'json', '-show_format', '-show_streams', '-v', 'quiet', url]
        try:
            # 设置超时时间为10秒
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            output = result.stdout
            data = json.loads(output)
            # 获取视频流信息
            video_streams = data['streams']
            width = 0.00
            height = 0
            frame = 0.00

            if len(video_streams) > 0:
                stream = video_streams[0]
                # 提取宽度和高度
                width = stream.get('width')
                if width is None:
                    frame = 0
                height = stream.get('height')
                if height is None:
                    height = 0
                # 提取帧速率
                frame = stream.get('r_frame_rate')
                if frame != '0/0' and frame != '':
                    frame = eval(frame)
                else:
                    frame = 0.0
            if width == 0 or height == 0 or frame == 0.0:
                return []
            return [width, height, frame]
        except KeyError:
            # print('无法提取视频流信息：找不到 streams 键')
            return []
        except json.JSONDecodeError:
            # print('无法解析 ffprobe 输出为 JSON 格式')
            return []
        except subprocess.CalledProcessError as e:
            # print("Error: 视频信息无效，解析失败")
            return []
        except subprocess.TimeoutExpired:
            # print("Error: 执行超时")
            return []

    # 获取IPTV播放速度信息
    def get_speed(self, url, fornum):
        try:
            speeds = []
            average_speed = 0

            for _ in range(fornum):
                start_time = time.time()
                response = requests.get(url, stream=True, timeout=10)
                total_bytes = 0

                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        total_bytes += len(chunk)

                response.close()

                current_time = time.time()
                elapsed_time = current_time - start_time
                speed = total_bytes / elapsed_time / 1024  # 计算网速，单位为 Kbps
                speeds.append(speed)
                # print(f"当前网速：{speed:.2f} Kbps")

                time.sleep(2)  # 等待2秒

            average_speed = sum(speeds) / len(speeds)
            # 格式化平均网速为两位小数
            average_speed = f"{average_speed:.2f}"
            # print(f"平均网速：{average_speed} Kbps")
            return average_speed
        except requests.Timeout:
            # print("请求超时")
            return 0.00
        except requests.RequestException as e:
            # print("请求发生异常:", str(e))
            return 0.00


def spider_source():
    # 获取工具类
    T = Tools()
    ys = []
    ws = []
    df = []
    # 爬取ZB源引擎
    for group_addr in groups:
        # 获取当前时间
        current_time = datetime.now()
        page = 1
        number = 0
        timeout_cnt = 0
        # 初始化集合数据
        data_list = []
        ch_list = []
        # 生成数据格式
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}
        url = "http://tonkiang.us"
        # 获取Cookie
        for _ in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                cookie = response.headers['Set-Cookie']
                headers['Cookie'] = cookie
                headers['Host'] = "tonkiang.us"
                break
            except:
                print('获取Cookie失败！重试中...')
                time.sleep(3)

        for index in range(1,set_page+1):
            try:
                url = engine_url + "?page=" + str(index) + "&s=" + group_addr
                response = requests.get(url,headers=headers,timeout=3)
                # 处理响应
                response.raise_for_status()
                # 检查请求是否成功
                html_content = response.text

                print(f"{current_time} 搜索频道ZB源：{url}")

                # 使用BeautifulSoup解析网页内容
                soup = BeautifulSoup(html_content, "html.parser")

                # 查找所有class为"result"的<div>标签
                result_divs = soup.find_all("div", class_="result")

                # 循环处理每个结果<div>标签
                for result_div in result_divs:

                    m3u8_name = ""
                    m3u8_link = ""
                    # 获取m3u8名称
                    channel_div = result_div.find("div", class_="channel")
                    if channel_div is not None:
                        name_div = channel_div.find("div", style="float: left;")
                        if name_div is not None:
                            m3u8_name = name_div.text.strip()
                        else:
                            counts_text = channel_div.text.strip()
                            # 提取数字部分
                            counts = int(''.join(filter(str.isdigit, counts_text)))
                            print(f"{current_time} 总记录数：{counts}")
                            page_count = int(counts) // 30
                            if counts / 30 > page_count:
                                page_count += 1
                            print(f"{current_time} 总页码数：{page_count}")
                            if index >= page_count:
                                break

                        # 获取m3u8链接
                        m3u8_div = result_div.find("div", class_="m3u8")
                        if m3u8_div is not None:
                            m3u8_link = m3u8_div.find("td", style="padding-left: 6px;").text.strip()
                            if m3u8_link.endswith('?'):
                                m3u8_link = m3u8_link[:-1]

                        if "http" not in m3u8_link:
                            # 继续下一次循环迭代
                            continue
                        if m3u8_name.upper() != group_addr.upper():
                            break
                        # 获取频道分类
                        if 'udp' not in m3u8_link and 'rtp' not in m3u8_link and 'rtsp' not in m3u8_link and iptvcheck == 1:
                            if T.check_iptv(m3u8_link, 5):
                                speed = T.get_speed(m3u8_link, 3)
                                if iptvresolution == 1:
                                    video_info = T.get_ffprobe_info(m3u8_link)
                                    data_info = (m3u8_name, m3u8_link)
                                    if float(speed) > 0 and len(video_info) > 0 and not any(
                                            info[:2] == data_info[:2] for info in data_list):
                                        # 提取宽度和高度
                                        width = video_info[0]
                                        height = video_info[1]
                                        # 提取帧速率
                                        frame = video_info[2]
                                        # 将数据添加到列表
                                        print(f"{current_time} 第{number+1}条数据，频道名称：{m3u8_name}，分辨率：{width}*{height}，帧速率：{frame}, 播放速度：{speed} Kbps，有效地址: {m3u8_link}")
                                        number += 1
                                if 'CCTV' in m3u8_name.upper():
                                    ys.append((m3u8_name.upper(),m3u8_link))
                                elif '卫视' in m3u8_name.upper():
                                    ws.append((m3u8_name.upper(),m3u8_link))
                                else:
                                    df.append((m3u8_name.upper(),m3u8_link))
                        else:
                            if 'CCTV' in m3u8_name.upper():
                                ys.append((m3u8_name.upper(), m3u8_link))
                            elif '卫视' in m3u8_name.upper():
                                ws.append((m3u8_name.upper(), m3u8_link))
                            else:
                                df.append((m3u8_name.upper(), m3u8_link))
                    else:
                        continue
            except (requests.Timeout, requests.RequestException) as e:
                timeout_cnt += 1
                print(f"{current_time} 请求发生超时，异常次数：{timeout_cnt} 正在重试！")
                if timeout_cnt <= 10:
                    # 继续下一次循环迭代
                    continue
                else:
                    print(f"{current_time} 超时次数过多：{timeout_cnt} 次，请检查网络是否正常")
            page += 1
    return [ys,ws,df]

def make_txt(data):
    #制作输出zb文件
    f = open('%s%s%s.txt'%(os.getcwd(),os.sep,time.strftime("%Y%m%d", time.localtime(time.time()))),'a',encoding='utf-8')
    f.write('央视,#genre#\n')
    for line in data[0]:
        f.write(f'%s,%s\n'%(line[0],line[1]))
    f.write('卫视,#genre#\n')
    for line in data[1]:
        f.write(f'%s,%s\n'%(line[0],line[1]))
    f.write('地方,#genre#\n')
    for line in data[2]:
        f.write(f'%s,%s\n'%(line[0],line[1]))
    f.close()
    input('制作完成！ 文件输出在当前文件夹！ 回车结束！')


if __name__ == '__main__':
    engine_url = "http://tonkiang.us/"
    # 执行主程序函数
    groups = ["CCTV1","CCTV2","CCTV3","湖南卫视"]
    # 频道，执行多个频道搜索改成 groups = ["CCTV1","CCTV2","CCTV3","CCTV4","湖南卫视"]
    set_page = 2
    #设置爬取页面数,爬取的名称大写和搜索的大写不一致时停止爬取
    iptvcheck = 1
    #是否检测正常访问
    iptvresolution = 1
    #检测分辨率
    make_txt(spider_source())