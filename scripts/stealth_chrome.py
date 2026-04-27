#!/usr/bin/env python3
"""
反检测 Chrome 浏览器 - 用于绕过机器人检查

用法 (Python 模块):
    from stealth_chrome import create_stealth_driver, search, get_page_content
    driver = create_stealth_driver()
    results = search(driver, 'Python 教程')
    driver.quit()

用法 (命令行):
    python stealth_chrome.py search "Python 教程"
    python stealth_chrome.py search "AI 新闻" --engine bing --max-results 5
    python stealth_chrome.py get https://example.com
"""

import sys
import os
import json
import argparse
import time

# 确保能找到依赖包
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# 添加常见 site-packages 路径（支持 venv 和系统安装）
for path in [
    os.path.join(SKILL_DIR, 'venv', 'lib'),
    os.path.join(os.path.expanduser('~'), '.local', 'lib'),
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
    # 注意：不要手动注入 CDP 反检测脚本！
    # undetected-chromedriver 自己已经做了完整的反检测处理
    # 额外注入的 CDP 脚本（尤其是 plugins: [1,2,3,4,5]）反而暴露自动化特征
    # 测试证明：有 CDP 注入 → Google CAPTCHA，无 CDP 注入 → 正常搜索

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


def _search_duckduckgo(driver, query, max_results=10):
    """DuckDuckGo 搜索引擎 — 最可靠，不易被 CAPTCHA"""
    from selenium.webdriver.common.keys import Keys

    driver.get('https://duckduckgo.com')
    time.sleep(2)

    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # DuckDuckGo 结果选择器
    result_links = driver.find_elements(By.CSS_SELECTOR, 'article h2 a, [data-testid="result-title-a"]')
    results = []

    for link in result_links[:max_results]:
        try:
            title = link.text.strip()
            url = link.get_attribute('href')
            if title and url:
                results.append({'title': title, 'url': url})
        except:
            pass

    return results


def _search_bing(driver, query, max_results=10):
    """Bing 搜索引擎"""
    from selenium.webdriver.common.keys import Keys

    driver.get('https://www.bing.com')
    time.sleep(2)

    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # Bing 结果：h2 > a，链接在 a 标签上
    result_h2s = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo h2, .b_algo h2')
    results = []

    for h2 in result_h2s[:max_results]:
        try:
            # 尝试在 h2 内找 a 标签
            a_tag = h2.find_element(By.TAG_NAME, 'a')
            title = a_tag.text.strip()
            url = a_tag.get_attribute('href')
            if title and url:
                results.append({'title': title, 'url': url})
        except:
            # 回退：尝试父元素的 href
            try:
                title = h2.text.strip()
                parent = h2.find_element(By.XPATH, '..')
                url = parent.get_attribute('href')
                if title and url:
                    results.append({'title': title, 'url': url})
            except:
                pass

    return results


def _search_google(driver, query, max_results=10):
    """Google 搜索引擎 — 可能被 CAPTCHA 拦截"""
    from selenium.webdriver.common.keys import Keys

    driver.get('https://www.google.com')
    time.sleep(2)

    # 检查是否被 CAPTCHA 拦截
    if '/sorry/' in driver.current_url:
        raise RuntimeError('Google CAPTCHA 检测，请使用 --engine duckduckgo 或 --engine bing')

    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # 再次检查是否被 CAPTCHA 拦截
    if '/sorry/' in driver.current_url:
        raise RuntimeError('Google CAPTCHA 检测，请使用 --engine duckduckgo 或 --engine bing')

    # Google 结果选择器
    h3_elements = driver.find_elements(By.CSS_SELECTOR, '#search a h3, #rso a h3, div.g a h3')
    results = []

    for h3 in h3_elements[:max_results]:
        try:
            title = h3.text.strip()
            link = h3.find_element(By.XPATH, '..').get_attribute('href')
            if title and link:
                results.append({'title': title, 'url': link})
        except:
            pass

    return results


# 搜索引擎注册表
ENGINES = {
    'duckduckgo': _search_duckduckgo,
    'ddg': _search_duckduckgo,
    'bing': _search_bing,
    'google': _search_google,
}

# 默认引擎回退顺序（Google 优先，CAPTCHA 时自动回退）
FALLBACK_ORDER = ['google', 'duckduckgo', 'bing']


def search(driver, query, max_results=10, engine=None, fallback=True):
    """
    搜索并返回结果

    Args:
        driver: Chrome 实例
        query: 搜索关键词
        max_results: 最大返回结果数
        engine: 指定搜索引擎 (duckduckgo/ddg/bing/google)，None=自动回退
        fallback: 失败时是否自动回退到下一个引擎

    Returns:
        list of dict, 每个 dict 包含 'title' 和 'url'
    """
    if engine:
        engine_key = engine.lower()
        if engine_key not in ENGINES:
            raise ValueError(f'不支持的搜索引擎: {engine}，可用: {list(ENGINES.keys())}')
        engines_to_try = [engine_key]
    else:
        engines_to_try = FALLBACK_ORDER

    last_error = None
    for eng in engines_to_try:
        try:
            results = ENGINES[eng](driver, query, max_results)
            if results:
                return results
            # 如果没结果但没报错，尝试下一个引擎
            last_error = RuntimeError(f'{eng}: 未找到搜索结果')
        except Exception as e:
            last_error = e
            if not fallback:
                raise
            continue

    # 所有引擎都失败
    if last_error:
        raise last_error
    return []


# 保持旧的 google_search 函数向后兼容
def google_search(driver, query, max_results=10):
    """向后兼容 - 使用自动回退搜索"""
    return search(driver, query, max_results)


def cli_main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='反检测 Chrome 浏览器 - 绕过机器人检查进行搜索和抓取'
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # search 子命令
    search_parser = subparsers.add_parser('search', help='搜索')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--engine', choices=list(ENGINES.keys()),
                               default=None, help='搜索引擎 (默认自动回退: google -> ddg -> bing)')
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
            results = search(driver, args.query, max_results=args.max_results, engine=args.engine)
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

        print("Testing with DuckDuckGo...")
        title = safe_get(driver, 'https://duckduckgo.com')
        print(f"Page title: {title}")

        webdriver_val = driver.execute_script("return navigator.webdriver")
        ua = driver.execute_script("return navigator.userAgent")
        platform = driver.execute_script("return navigator.platform")

        print(f"navigator.webdriver: {webdriver_val}")
        print(f"User-Agent: {ua}")
        print(f"Platform: {platform}")

        driver.quit()
        print("\nAll tests passed! Stealth Chrome is ready.")
