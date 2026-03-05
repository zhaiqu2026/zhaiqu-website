#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 商品自动抓取脚本 - 移动端版本
使用移动端页面绕过反爬
"""

import json
import os
import sys
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置
WEBSITE_DIR = Path("/home/admin/.openclaw/workspace/zhaiqu-website")
DATA_FILE = WEBSITE_DIR / "products.json"
COOKIES_FILE = WEBSITE_DIR / "cookies.json"

def extract_offer_id(url):
    """从 URL 提取商品 ID"""
    # https://detail.1688.com/offer/609060377631.html
    match = re.search(r'/offer/(\d+)', url)
    if match:
        return match.group(1)
    return None

def fetch_product_info(url, context):
    """抓取单个商品信息 - 使用移动端页面"""
    print(f"\n🔍 正在抓取：{url}")
    
    offer_id = extract_offer_id(url)
    if not offer_id:
        print(f"  ❌ 无法提取商品 ID")
        return None
    
    # 使用移动端 API（防护较弱）
    mobile_api = f"https://m.1688.com/offer/{offer_id}.html"
    
    page = context.new_page()
    
    try:
        # 设置移动端 User-Agent
        context.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        })
        
        # 访问移动端页面
        page.goto(mobile_api, wait_until="domcontentloaded", timeout=30000)
        
        # 等待页面加载
        page.wait_for_timeout(5000)
        
        # 检查是否被拦截
        page_content = page.content()
        if "Access denied" in page_content or "访问被拒绝" in page_content or "安全验证" in page_content:
            print(f"  ⚠️  页面被拦截")
            return None
        
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
            title = page.query_selector("h1, .title, [data-title]")
            if title:
                text = title.inner_text().strip()
                if text and len(text) > 5:
                    product_info["title"] = text[:100]
        except:
            pass
        
        # 提取价格
        try:
            price = page.query_selector(".price, .r-price, .dt-price")
            if price:
                text = price.inner_text().strip()
                if text:
                    product_info["price"] = text
        except:
            pass
        
        # 提取图片
        try:
            images = page.query_selector_all("img")
            for img in images[:30]:
                src = img.get_attribute("src")
                if src and src.startswith("http") and ("alicdn" in src or "1688" in src):
                    if not any(x in src for x in ["favicon", "icon", "avatar"]):
                        # 清理图片 URL
                        if "?" in src:
                            src = src.split("?")[0]
                        if src not in product_info["images"]:
                            product_info["images"].append(src)
                            if len(product_info["images"]) >= 5:
                                break
        except:
            pass
        
        # 如果没抓到，尝试从页面 URL 获取图片
        if not product_info["images"]:
            # 1688 图片通常在页面中有特定格式
            try:
                all_imgs = page.query_selector_all("img[src*='alicdn']")
                for img in all_imgs[:10]:
                    src = img.get_attribute("src")
                    if src and src not in product_info["images"]:
                        product_info["images"].append(src)
                        if len(product_info["images"]) >= 3:
                            break
            except:
                pass
        
        # 获取页面标题作为备选
        if not product_info["title"]:
            try:
                page_title = page.title()
                if page_title:
                    product_info["title"] = page_title[:100]
            except:
                pass
        
        if product_info["title"] or product_info["images"]:
            print(f"  ✅ 抓取成功：{product_info['title'][:50] if product_info['title'] else '有图片'}")
            return product_info
        else:
            print(f"  ⚠️  未抓取到有效信息")
            return None
        
    except Exception as e:
        print(f"  ❌ 抓取失败：{str(e)[:100]}")
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
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 宅趣网站</h1>
        <p>专业代工 · 品质保证</p>
    </div>
    
    <div class="container">
        <div class="products">
"""
    
    if not products:
        html += """
            <div style="grid-column: 1/-1; text-align: center; padding: 60px;">
                <h2>📦 产品数据加载中...</h2>
            </div>
"""
    else:
        for p in products:
            image = p.get('images', [''])[0] if p.get('images') else ''
            html += f"""
            <div class="product-card">
                <img src="{image}" alt="产品" class="product-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22250%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22300%22 height=%22250%22/%3E%3Ctext fill=%22%23999%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22%3E暂无图片%3C/text%3E%3C/svg%3E'">
                <div class="product-info">
                    <h3 class="product-title">{p.get('title', '未命名产品')}</h3>
                    <div class="product-price">{p.get('price', '面议')}</div>
                    <p class="product-desc">{p.get('company', '')}</p>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <div class="footer">
        <p>© 2026 宅趣网站 · 专业代工服务</p>
    </div>
</body>
</html>
"""
    return html

def main(urls=None):
    """主函数"""
    print("🚀 开始抓取 1688 商品信息（移动端版）...")
    
    if urls is None:
        urls = []
    
    products = []
    
    # 加载已有产品
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            products = existing
            print(f"📋 已加载 {len(existing)} 个已有产品")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = browser.new_context(
            viewport={"width": 375, "height": 812},  # iPhone 尺寸
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        )
        
        for url in urls:
            if url in {p.get('url') for p in products}:
                print(f"\n⏭️  跳过已抓取：{url}")
                continue
            
            info = fetch_product_info(url, context)
            if info:
                products.append(info)
            
            time.sleep(3)
        
        browser.close()
    
    if products:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 产品数据已保存到 {DATA_FILE}")
    
    html = generate_website_html(products)
    html_file = WEBSITE_DIR / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 网站 HTML 已更新到 {html_file}")
    
    print(f"\n📊 共有 {len(products)} 个商品")
    
    if len(products) > 0:
        print("\n🔄 提交到 GitHub...")
        os.system(f"cd {WEBSITE_DIR} && git add . && git commit -m '自动更新：{len(products)} 个商品' && git push origin main")
        print("✅ 已推送！")

if __name__ == "__main__":
    urls = sys.argv[1:] if len(sys.argv) > 1 else []
    main(urls)
