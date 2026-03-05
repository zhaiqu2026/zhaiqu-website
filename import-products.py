#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品数据导入工具
用于手动导入 1688/淘宝商品信息
"""

import json
import os
from pathlib import Path

WEBSITE_DIR = Path("/home/admin/.openclaw/workspace/zhaiqu-website")
PRODUCTS_FILE = WEBSITE_DIR / "products.json"

def import_from_json(json_file):
    """从 JSON 文件导入产品数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # 合并到现有产品列表
    existing = []
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    
    # 去重（根据 URL）
    existing_urls = {p.get('url') for p in existing}
    for p in products:
        if p.get('url') not in existing_urls:
            existing.append(p)
    
    # 保存
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功导入 {len(products)} 个产品")
    return len(products)

def create_template():
    """创建产品数据模板"""
    template = [
        {
            "url": "https://detail.1688.com/offer/609060377631.html",
            "title": "产品名称",
            "price": "价格区间（如：¥10.50-15.00）",
            "images": [
                "https://example.com/image1.jpg"
            ],
            "description": "产品描述",
            "company": "公司名称"
        }
    ]
    
    template_file = WEBSITE_DIR / "products-template.json"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 模板已创建：{template_file}")
    print("📝 请编辑此文件，填入真实产品数据，然后运行：python3 import-products.py")

def generate_website():
    """生成网站 HTML"""
    products = []
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            products = json.load(f)
    
    # 调用主脚本的生成函数
    import sys
    sys.path.append(str(WEBSITE_DIR))
    from auto_fetch_1688 import generate_website_html
    
    html = generate_website_html(products)
    html_file = WEBSITE_DIR / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 网站已更新：{html_file}")
    
    # 自动提交
    print("\n🔄 提交到 GitHub...")
    os.system(f"cd {WEBSITE_DIR} && git add . && git commit -m '更新产品数据：{len(products)} 个商品' && git push origin main")
    print("✅ 已推送到 GitHub！")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "template":
            create_template()
        elif sys.argv[1].endswith(".json"):
            import_from_json(sys.argv[1])
            generate_website()
    else:
        print("📦 产品数据导入工具")
        print("\n用法:")
        print("  python3 import-products.py template     - 创建数据模板")
        print("  python3 import-products.py data.json    - 从 JSON 文件导入")
        print("\n步骤:")
        print("  1. 运行：python3 import-products.py template")
        print("  2. 编辑 products-template.json，填入产品信息")
        print("  3. 运行：python3 import-products.py products-template.json")
