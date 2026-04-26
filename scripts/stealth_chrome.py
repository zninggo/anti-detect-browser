#!/usr/bin/env python3
"""
反检测 Chrome 浏览器 - 用于绕过机器人检查

用法 (Python 模块):
    from stealth_chrome import create_stealth_driver, google_search, get_page_content
    driver = create_stealth_driver()
    results = google_search(driver, 'Python 教程')
    driver.quit()

用法 (命令行):
    python stealth_chrome.py search "Python 教程"
    python stealth_chrome.py get https://example.com
    python stealth_chrome.py search "AI 新闻" --max-results 5
"""

import sys
import os
import json
import argparse
import time

# 确保能找到依赖包
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# 添加常见 site-packages 路径
for path in [
    os.path.join(SKILL_DIR, 'venv', 'lib'),
    '/data/repo/hermes-agent/venv/lib/python3.13/site-packages',
]:
    if os.path.exists(path):
        for sub in os.listdir(path):
            sp = os.path.join(path, sub, 'site-packages')
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError as e:
    print(f"错误: 缺少依赖包 - {e}", file=sys.stderr)
    print("请运行: pip install undetected-chromedriver selenium", file=sys.stderr)
    sys.exit(1)


def create_stealth_driver(headless=True, window_size='1920,1080', lang='zh-CN'):
    """
    创建一个反检测的 Chrome 浏览器实例

    Args:
        headless: 是否无头模式
        window_size: 窗口大小
        lang: 语言设置

    Returns:
        undetected_chromedriver.Chrome 实例
    """
    options = uc.ChromeOptions()

    if headless:
        options.add_argument('--headless=new')

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--window-size={window_size}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f'--lang={lang}')

    # 伪装 User-Agent (Windows Chrome)
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/147.0.7727.117 Safari/537.36'
    )

    driver = uc.Chrome(options=options, version_main=147)

    # 注入额外的反检测脚本
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            // 隐藏 webdriver 标志
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

            // 伪装平台
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});

            // 伪装语言
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en']
            });

            // 伪装 plugins 数量
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // 隐藏 Chrome 自动化特征
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };

            // 伪装 permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        '''
    })

    return driver


def safe_get(driver, url, timeout=10):
    """
    安全地访问 URL，等待页面加载完成

    Args:
        driver: Chrome 实例
        url: 目标 URL
        timeout: 超时时间

    Returns:
        页面标题
    """
    driver.get(url)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    return driver.title


def get_page_content(driver, url=None):
    """
    获取页面的完整 HTML 内容

    Args:
        driver: Chrome 实例
        url: 可选的 URL，如果不提供则获取当前页面

    Returns:
        HTML 内容字符串
    """
    if url:
        safe_get(driver, url)
    return driver.page_source


def google_search(driver, query, max_results=10):
    """
    使用 Google 搜索并返回结果

    Args:
        driver: Chrome 实例
        query: 搜索关键词
        max_results: 最大返回结果数

    Returns:
        list of dict, 每个 dict 包含 'title' 和 'url'
    """
    from selenium.webdriver.common.keys import Keys

    driver.get('https://www.google.com')
    time.sleep(2)

    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # 提取搜索结果
    h3_elements = driver.find_elements(By.CSS_SELECTOR, '#search a h3')
    results = []

    for h3 in h3_elements[:max_results]:
        try:
            title = h3.text
            link = h3.find_element(By.XPATH, '..').get_attribute('href')
            results.append({'title': title, 'url': link})
        except:
            pass

    return results


def cli_main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='反检测 Chrome 浏览器 - 绕过机器人检查进行搜索和抓取'
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # search 子命令
    search_parser = subparsers.add_parser('search', help='Google 搜索')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--max-results', type=int, default=10, help='最大结果数 (默认 10)')
    search_parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')

    # get 子命令
    get_parser = subparsers.add_parser('get', help='抓取网页内容')
    get_parser.add_argument('url', help='目标 URL')
    get_parser.add_argument('--length', type=int, default=0, help='输出长度限制 (0=全部)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    driver = None
    try:
        driver = create_stealth_driver()

        if args.command == 'search':
            results = google_search(driver, args.query, max_results=args.max_results)
            if args.json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                if not results:
                    print('未找到搜索结果')
                else:
                    for i, r in enumerate(results, 1):
                        print(f'{i}. {r["title"]}')
                        print(f'   {r["url"]}')

        elif args.command == 'get':
            html = get_page_content(driver, args.url)
            if args.length > 0:
                print(html[:args.length])
            else:
                print(html)

    except Exception as e:
        print(f'错误: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        if driver:
            driver.quit()


# 测试用
if __name__ == '__main__':
    if len(sys.argv) > 1:
        # CLI 模式
        cli_main()
    else:
        # 测试模式
        print("Creating stealth Chrome driver...")
        driver = create_stealth_driver()

        print("Testing with Google...")
        title = safe_get(driver, 'https://www.google.com')
        print(f"Page title: {title}")

        webdriver_val = driver.execute_script("return navigator.webdriver")
        ua = driver.execute_script("return navigator.userAgent")
        platform = driver.execute_script("return navigator.platform")

        print(f"navigator.webdriver: {webdriver_val}")
        print(f"User-Agent: {ua}")
        print(f"Platform: {platform}")

        driver.quit()
        print("\nAll tests passed! Stealth Chrome is ready.")
