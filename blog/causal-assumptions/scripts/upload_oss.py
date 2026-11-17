# -*- coding: utf-8 -*-
"""
把两图按工作流命名规则上传到阿里云 OSS（bucket fig-lianxh）。
凭证从 PicGo 配置 data.json 读取，脚本不打印、不展示密钥。
上传后通过 head_object 与下载内容校验 SHA-256。
"""
import hashlib
import json
import os

import oss2

PICGO_CONFIG = r"C:\Users\admin36\AppData\Roaming\picgo\data.json"
PROJECT = r"D:\doubao_project\blog-lianxh\因果推断三大识别假设"
STAMP = "202611171751"

with open(PICGO_CONFIG, "r", encoding="utf-8") as f:
    cfg = json.load(f)
ali = cfg["picBed"]["aliyun"]

endpoint = "https://" + ali["area"] + ".aliyuncs.com"
bucket = oss2.Bucket(oss2.Auth(ali["accessKeyId"], ali["accessKeySecret"]),
                     endpoint, ali["bucket"])

# (本地文件名, OSS 对象键)
files = [
    ("causal-assumptions-fig01-bias-20261116-213603.png",
     "lianxiaobai-causal-assumptions-fig1-" + STAMP + ".png"),
    ("causal-assumptions-fig02-overlap-20261116-213603.png",
     "lianxiaobai-causal-assumptions-fig2-" + STAMP + ".png"),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


for src_name, key in files:
    src = os.path.join(PROJECT, "images", src_name)
    local_hash = sha256_file(src)
    local_size = os.path.getsize(src)

    put = bucket.put_object_from_file(key, src)
    head = bucket.head_object(key)
    remote_bytes = bucket.get_object(key).read()
    remote_hash = hashlib.sha256(remote_bytes).hexdigest()

    url = "https://" + ali["bucket"] + "." + ali["area"] + ".aliyuncs.com/" + key
    print("对象键:", key)
    print("  上传 HTTP:", put.status)
    print("  远端大小:", head.content_length, "| 本地大小:", local_size,
          "| 一致:", head.content_length == local_size)
    print("  SHA-256 一致:", remote_hash == local_hash)
    print("  URL:", url)
    print()
