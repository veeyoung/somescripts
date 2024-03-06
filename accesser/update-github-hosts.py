#!/usr/bin/env python3
from requests_html import HTMLSession
import toml
from fetch_ips import get_json, GITHUB_URLS

def add_to_config_toml(json_content):
    config_toml_path = "./config.toml"

    if json_content is None:
        return
    # 读取config.toml文件内容
    with open(config_toml_path, 'r') as file:
        config_data = toml.load(file)

    # 获取host部分
    hosts_section = config_data.get('hosts', {})

    # 更新hosts部分或添加新的键值对
    for entry in json_content:
        ip, domain = entry
        ip = ip.strip()
        domain = domain.strip()
        hosts_section[domain] = ip

    # 将更新后的内容写回config.toml文件
    config_data['hosts'] = hosts_section
    with open(config_toml_path, 'w') as file:
        toml.dump(config_data, file)

if __name__ == '__main__':
    session = HTMLSession()
    content_list = get_json(session)
    add_to_config_toml(content_list)
