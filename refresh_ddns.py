# 刷新电脑的ddns
# Version 1.0.0.20250317


import os
import json
import subprocess
from datetime import datetime
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

# 从环境变量中读取secret_id和secret_key
secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
if not secret_id or not secret_key:
    print("请设置环境变量TENCENTCLOUD_SECRET_ID和TENCENTCLOUD_SECRET_KEY")
    exit(1)

def get_dns_ip():
    try:
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dnspod_client.DnspodClient(cred, "", clientProfile)
        req = models.DescribeRecordListRequest()
        params = {
            "Domain": "littleking.site",
            "Subdomain": "xx.rdp"
        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeRecordList(req)
        dns_ip = resp.RecordList[0].Value
        return dns_ip

    except TencentCloudSDKException as err:
        print(err)
        return None

def set_dns_ip(ip):
    # 检查ip格式
    if not ip or not ip.startswith("10."):
        return
    try:
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dnspod_client.DnspodClient(cred, "", clientProfile)
        req = models.ModifyRecordRequest()
        params = {
            "Domain": "littleking.site",
            "RecordType": "A",
            "RecordLine": "默认",
            "Value": ip,
            "RecordId": 1986143276,
            "SubDomain": "xx.rdp",
            "Remark": f"update by my ddns, {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        req.from_json_string(json.dumps(params))
        resp = client.ModifyRecord(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)

def get_eth_ip():
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if '以太网适配器 以太网' in line:
                for j in range(i + 1, len(lines)):
                    if 'IPv4 地址' in lines[j]:
                        ip_address = lines[j].split(': ')[1]
                        return ip_address
    except Exception as e:
        print(f"获取IP地址时发生错误: {e}")
    return None

    

if __name__ == '__main__':
    eth_ip = get_eth_ip()
    dns_ip = get_dns_ip()
    print(f"当前IP地址: {eth_ip}", f"DNS记录IP地址: {dns_ip}")
    if eth_ip != dns_ip:
        print(f"IP地址已更改，更新DNS记录。")
        set_dns_ip(eth_ip)
    else:
        print(f"IP地址未更改，无需更新DNS记录。")