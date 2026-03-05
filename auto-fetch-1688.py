#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 商品自动抓取脚本
用于从 1688 店铺获取商品信息并更新网站
"""

import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 配置
WEBSITE_DIR = Path("/home/admin/.openclaw/workspace/zhaiqu-website")
DATA_FILE = WEBSITE_DIR / "products.json"
COOKIES_FILE = WEBSITE_DIR / "cookies.json"

# 要抓取的商品链接列表
PRODUCT_URLS = [
    "https://detail.1688.com/offer/609060377631.html",
    # 可以添加更多商品链接
]

def save_cookies(page, filepath):
    """保存 Cookies"""
    cookies = page.context.cookies()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    print(f"✅ Cookies 已保存到 {filepath}")

def load_cookies(filepath):
    """加载 Cookies"""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def fetch_product_info(url, context):
    """抓取单个商品信息"""
    print(f"\n🔍 正在抓取：{url}")
    
    page = context.new_page()
    
    try:
        # 设置超时
        page.set_default_timeout(30000)
        
        # 访问页面
        page.goto(url, wait_until="domcontentloaded")
        
        # 等待页面加载
        page.wait_for_timeout(5000)
        
        # 尝试提取商品信息
        product_info = {
            "url": url,
            "title": "",
            "price": "",
            "images": [],
            "description": "",
            "company": ""
        }
        
        # 提取标题
        try:
            title = page.query_selector("h.d-title")
            if title:
                product_info["title"] = title.inner_text().strip()
            else:
                # 备用选择器
                title = page.query_selector("h1")
                if title:
                    product_info["title"] = title.inner_text().strip()[:100]
        except Exception as e:
            print(f"  ⚠️  标题提取失败：{e}")
        
        # 提取价格
        try:
            price = page.query_selector(".price-content")
            if price:
                product_info["price"] = price.inner_text().strip()
        except Exception as e:
            print(f"  ⚠️  价格提取失败：{e}")
        
        # 提取图片
        try:
            images = page.query_selector_all(".img-container img")
            for img in images[:5]:  # 最多取 5 张
                src = img.get_attribute("src")
                if src and src.startswith("http"):
                    product_info["images"].append(src)
        except Exception as e:
            print(f"  ⚠️  图片提取失败：{e}")
        
        # 提取公司名
        try:
            company = page.query_selector(".company-name")
            if company:
                product_info["company"] = company.inner_text().strip()
        except Exception as e:
            print(f"  ⚠️  公司名提取失败：{e}")
        
        print(f"  ✅ 抓取成功：{product_info['title'][:50] if product_info['title'] else '无标题'}")
        return product_info
        
    except PlaywrightTimeout:
        print(f"  ⏱️  页面加载超时")
        return None
    except Exception as e:
        print(f"  ❌ 抓取失败：{e}")
        return None
    finally:
        page.close()

def generate_website_html(products):
    """生成网站 HTML"""
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>宅趣网站 - 产品展示</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; padding: 40px 0; }
        .product-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-5px); }
        .product-image { width: 100%; height: 250px; object-fit: cover; background: #f0f0f0; }
        .product-info { padding: 20px; }
        .product-title { font-size: 1.2em; margin-bottom: 10px; color: #333; }
        .product-price { color: #e74c3c; font-size: 1.3em; font-weight: bold; margin-bottom: 10px; }
        .product-desc { color: #666; font-size: 0.9em; line-height: 1.6; }
        .footer { text-align: center; padding: 30px; color: #666; }
        .loading { text-align: center; padding: 60px 20px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 宅趣网站</h1>
        <p>专业代工 · 品质保证</p>
    </div>
    
    <div class="container">
"""
    
    if not products:
        html += """
        <div class="loading">
            <h2>📦 产品数据加载中...</h2>
            <p>请稍后再来查看</p>
        </div>
"""
    else:
        html += '        <div class="products">\n'
        for p in products:
            image = p.get('images', [''])[0] if p.get('images') else ''
            html += f"""
            <div class="product-card">
                <img src="{image}" alt="{p.get('title', '产品')}" class="product-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22250%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22300%22 height=%22250%22/%3E%3Ctext fill=%22%23999%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22%3E暂无图片%3C/text%3E%3C/svg%3E'">
                <div class="product-info">
                    <h3 class="product-title">{p.get('title', '未命名产品')}</h3>
                    <div class="product-price">{p.get('price', '面议')}</div>
                    <p class="product-desc">{p.get('company', '')}</p>
                </div>
            </div>
"""
        html += '        </div>\n'
    
    html += """
    </div>
    
    <div class="footer">
        <p>© 2026 宅趣网站 · 专业代工服务</p>
    </div>
</body>
</html>
"""
    return html

def main():
    """主函数"""
    print("🚀 开始抓取 1688 商品信息...")
    
    products = []
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 检查是否有保存的 Cookies
        cookies = load_cookies(COOKIES_FILE)
        if cookies:
            print("📋 加载已保存的 Cookies...")
            context.add_cookies(cookies)
        
        # 抓取每个商品
        for url in PRODUCT_URLS:
            info = fetch_product_info(url, context)
            if info:
                products.append(info)
        
        browser.close()
    
    # 保存产品数据
    if products:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 产品数据已保存到 {DATA_FILE}")
    
    # 生成网站 HTML
    html = generate_website_html(products)
    html_file = WEBSITE_DIR / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 网站 HTML 已更新到 {html_file}")
    
    print(f"\n📊 本次抓取完成：{len(products)} 个商品")
    
    # 如果有新商品，自动提交到 GitHub
    if products:
        print("\n🔄 准备自动提交到 GitHub...")
        os.system(f"cd {WEBSITE_DIR} && git add . && git commit -m '自动更新：抓取 {len(products)} 个商品' && git push origin main")
        print("✅ 已推送到 GitHub，网站将自动更新！")

if __name__ == "__main__":
    main()
