---
name: anti-detect-browser
description: 反检测 Chrome 浏览器 — 使用 undetected-chromedriver 绕过机器人检查
triggers:
  - 需要搜索引擎查询时（百度、Google、Bing 等）
  - 需要抓取网页内容时
  - 需要访问可能有反爬检测的网站时
  - browser_navigate 遇到 CAPTCHA 或机器人检测时
  - 任何搜索/抓取任务的首选工具
---

# Anti-Detect Browser

## ⚠️ 使用时机（必须遵守）

**搜索/抓取任务时，本 skill 是首选工具，不是备选方案。**

| 场景 | 正确做法 | 错误做法 |
|------|----------|----------|
| 需要搜索信息 | 用本 skill 的 search 命令 | 用 browser_navigate 访问搜索引擎 |
| 遇到 CAPTCHA | 立即切换到本 skill | 换另一个网站绕过 |
| 需要抓取网页 | 用本 skill 的 get 命令 | 直接用 curl 或 browser_navigate |

**触发条件（任一满足即应使用）：**
- 任何需要搜索引擎查询的任务（百度、Google、Bing 等）
- browser_navigate 遇到 CAPTCHA 或机器人检测页面
- 需要抓取可能有反爬检测的网站
- 需要绕过机器人检查的任何场景

反检测 Chrome 浏览器，使用 undetected-chromedriver 绕过机器人检查。
支持多搜索引擎自动回退（DuckDuckGo → Bing → Google），适用于所有需要搜索或抓取网页内容的场景。

## 首次使用检查清单

在使用本 skill 之前，按顺序执行以下步骤：

### Step 1：安装依赖

运行一键安装脚本（自动检测平台和已有 Chrome，不会重复安装）：

```bash
bash scripts/install.sh
```

安装脚本特性：
- **自动检测终端类型**：人工执行时交互式询问；Agent / 管道调用时自动跳过确认
- **自动检测 Chrome**：找到则跳过，找不到则提示对应平台的安装方式
- **支持平台**：Linux (apt/yum/pacman)、macOS (brew)、Windows (手动/winget)
- **可用参数**：`--auto`（强制全自动）、`--skip-chrome`（只装 Python 依赖）

### Step 2：验证依赖是否就绪

```bash
# 检查 Chrome
google-chrome --version || chromium-browser --version

# 检查 Python 依赖
python3 -c "import undetected_chromedriver; import selenium; print('OK')"
```

如果输出 OK，说明依赖已就绪，可以开始使用。如果报错，回到 Step 1。

### Step 3：使用

依赖就绪后，按以下任一方式使用。

## 使用方式

#### 方式 A：命令行直接调用

```bash
# 搜索（默认使用 DuckDuckGo，失败自动回退 Bing → Google）
python scripts/stealth_chrome.py search "Python 教程"

# 指定搜索引擎
python scripts/stealth_chrome.py search "AI 新闻" --engine bing
python scripts/stealth_chrome.py search "关键词" --engine duckduckgo
python scripts/stealth_chrome.py search "关键词" --engine google

# 指定结果数量
python scripts/stealth_chrome.py search "AI 新闻" --max-results 5

# JSON 格式输出
python scripts/stealth_chrome.py search "Python" --json

# 抓取网页
python scripts/stealth_chrome.py get https://example.com
```

#### 方式 B：作为 Python 模块导入

```python
from scripts.stealth_chrome import create_stealth_driver, search, google_search, get_page_content

driver = create_stealth_driver()

# 新的 search 函数（推荐，支持多引擎回退）
results = search(driver, 'Python 教程', max_results=5)

# 指定引擎
results = search(driver, 'Python 教程', engine='bing')

# google_search 仍然可用（向后兼容，等同于 search）
results = google_search(driver, 'Python 教程', max_results=5)

driver.quit()
```

#### 方式 C：Shell 调用（适用于 Claude Code / Codex 等）

```bash
# 将 /path/to/anti-detect-browser 替换为实际的项目路径
python3 /path/to/anti-detect-browser/scripts/stealth_chrome.py search "关键词"
```

## API 参考

### create_stealth_driver(headless=True, window_size='1920,1080', lang='zh-CN')
创建反检测 Chrome 实例
- `headless`: 是否无头模式（默认 True）
- `window_size`: 窗口大小（默认 1920x1080）
- `lang`: 语言设置（默认 zh-CN）
- 返回: undetected_chromedriver.Chrome 实例

### safe_get(driver, url, timeout=10)
安全访问 URL，等待页面加载完成
- `driver`: Chrome 实例
- `url`: 目标 URL
- `timeout`: 超时时间（默认 10 秒）
- 返回: 页面标题

### get_page_content(driver, url=None)
获取页面完整 HTML 内容
- `driver`: Chrome 实例
- `url`: 可选 URL，不提供则获取当前页面
- 返回: HTML 字符串

### search(driver, query, max_results=10, engine=None, fallback=True)
搜索并返回结果（推荐使用）
- `driver`: Chrome 实例
- `query`: 搜索关键词
- `max_results`: 最大结果数（默认 10）
- `engine`: 指定搜索引擎 (`duckduckgo`/`ddg`/`bing`/`google`)，None=自动回退
- `fallback`: 失败时是否自动回退到下一个引擎（默认 True）
- 返回: list of dict，每个包含 'title' 和 'url'
- 回退顺序: DuckDuckGo → Bing → Google

### google_search(driver, query, max_results=10)
向后兼容函数，等同于 `search(driver, query, max_results)`

## 使用示例

### 示例 1：搜索（自动回退）
```python
from scripts.stealth_chrome import create_stealth_driver, search

driver = create_stealth_driver()
results = search(driver, 'Python 教程', max_results=5)
for i, r in enumerate(results, 1):
    print(f"{i}. {r['title']}")
    print(f"   {r['url']}")
driver.quit()
```

### 示例 1b：指定搜索引擎
```python
from scripts.stealth_chrome import create_stealth_driver, search

driver = create_stealth_driver()
# 使用 Bing 搜索
results = search(driver, 'Python 教程', engine='bing', max_results=5)
driver.quit()
```

### 示例 2：抓取网页内容
```python
from scripts.stealth_chrome import create_stealth_driver, get_page_content

driver = create_stealth_driver()
html = get_page_content(driver, 'https://example.com')
print(html[:500])
driver.quit()
```

### 示例 3：提取页面特定元素
```python
from scripts.stealth_chrome import create_stealth_driver, safe_get
from selenium.webdriver.common.by import By

driver = create_stealth_driver()
safe_get(driver, 'https://news.ycombinator.com')
titles = driver.find_elements(By.CSS_SELECTOR, '.titleline > a')
for t in titles[:10]:
    print(f"- {t.text}: {t.get_attribute('href')}")
driver.quit()
```

### 示例 4：搜索后访问结果页面
```python
from scripts.stealth_chrome import create_stealth_driver, google_search, safe_get

driver = create_stealth_driver()
results = google_search(driver, 'undetected chromedriver 教程')
if results:
    safe_get(driver, results[0]['url'])
    print(f"页面标题: {driver.title}")
driver.quit()
```

## 其他 Agent 使用指南

本工具不限于特定 Agent，任何支持 shell 调用的 Agent 都能用。

### Claude Code / Codex / Cursor

1. **克隆仓库**：`git clone https://github.com/zninggo/anti-detect-browser.git`
2. **安装依赖**：`bash anti-detect-browser/scripts/install.sh`
3. **调用**：`python3 anti-detect-browser/scripts/stealth_chrome.py search "关键词"`

或者在项目的 CLAUDE.md / AGENTS.md 中添加引用：

```markdown
## 搜索工具
需要搜索或抓取网页时，使用反检测浏览器：
- 安装：bash /path/to/anti-detect-browser/scripts/install.sh
- 搜索：python3 /path/to/anti-detect-browser/scripts/stealth_chrome.py search "关键词"
- 抓取：python3 /path/to/anti-detect-browser/scripts/stealth_chrome.py get <url>
```

### 任意 Python 脚本

```python
import sys
sys.path.insert(0, '/path/to/anti-detect-browser/scripts')
from stealth_chrome import create_stealth_driver, google_search

driver = create_stealth_driver()
results = google_search(driver, '查询内容')
driver.quit()
```

## 反检测效果

以下由 undetected-chromedriver 自动处理，无需手动注入 CDP 脚本：
- navigator.webdriver: None（正常浏览器也是这个值）
- User-Agent: 伪装为 Windows Chrome 147
- Languages: zh-CN, zh, en-US, en
- 已通过 Google 搜索测试，不会触发 reCAPTCHA

> **注意**：不要通过 `execute_cdp_cmd` 手动注入反检测脚本！undetected-chromedriver 已经内置了完善的反检测机制，额外注入反而会与之冲突导致被检测到（详见"已知陷阱"）。

## 关键点
1. **必须在最后调用 driver.quit()** 释放资源
2. 搜索结果返回 list of dict，每个包含 'title' 和 'url'
3. 如果需要点击页面元素、填表等操作，用 selenium 的 By 定位
4. 每次只创建一个 driver 实例，用完立即 quit
5. 建议用 try-finally 包裹确保资源释放
6. **不要手动注入 CDP 反检测脚本**，让 undetected-chromedriver 全权处理

## 与其他 Skill 的配合

### 与 web-access 的关系

| Skill | 定位 | 适用场景 |
|-------|------|----------|
| anti-detect-browser | **执行工具** | 搜索、抓取、绕过反爬 |
| web-access | **方法论 + 知识库** | 联网工具选择策略、信息核实、站点经验 |

**配合原则**：
- 搜索/抓取任务 → 用 anti-detect-browser（本 skill）
- 需要方法论参考 → 加载 web-access
- 站点经验 → 从 web-access 的 site-patterns/ 读取

### 与 browser_navigate 的关系

| 工具 | 反检测能力 | 适用环境 |
|------|-----------|----------|
| anti-detect-browser | ✅ 强（绕过 CAPTCHA） | 任何环境 |
| browser_navigate (Hermes 内置) | ❌ 弱（必定触发 CAPTCHA） | 仅 Hermes |

**重要**：browser_navigate 是 Hermes 特有的无头浏览器工具，没有反检测功能，对百度、Google 等搜索引擎几乎必定触发 CAPTCHA。

## 站点专项方案

### B站 (bilibili.com) — Wbi 签名绕过反爬

B站有严格的反爬机制，直接请求 API 会返回 `-412 request was banned` 或 `-352` 错误。
必须使用 **wbi 签名** 才能访问 B站 API。

#### 前置条件：确保 Chrome 状态正常

B站搜索经常遇到 Chrome 进程残留导致 `session not created` 错误，**每次使用前必须检查**：

```bash
# 检查 Chrome 是否在运行
ps aux | grep -i chrome | grep -v grep
ss -tlnp | grep 9222

# 如果有残留进程，先清理
pkill -9 -f chrome
sleep 2

# 验证端口已释放
ss -tlnp | grep 9222 || echo "Port 9222 is free"
```

#### Wbi 签名工具函数

```python
import requests
import hashlib
import time
import urllib.parse
from functools import reduce

MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52
]

def get_mixin_key(orig):
    return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, '')[:32]

def enc_wbi(params, img_key, sub_key):
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time
    params = dict(sorted(params.items()))
    params = {
        k: ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v in params.items()
    }
    query = urllib.parse.urlencode(params)
    wbi_sign = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = wbi_sign
    return params

def get_wbi_keys():
    resp = requests.get('https://api.bilibili.com/x/web-interface/nav',
                       headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    data = resp.json()['data']
    img_url = data['wbi_img']['img_url']
    sub_url = data['wbi_img']['sub_url']
    img_key = img_url.rsplit('/', 1)[1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
    return img_key, sub_key
```

#### B站搜索示例

```python
import requests

# 获取 wbi 签名
img_key, sub_key = get_wbi_keys()

# 搜索参数
params = enc_wbi({
    'search_type': 'video',
    'keyword': 'ASMR',
    'order': 'click',  # 按播放量排序
    'page': 1,
    'page_size': 50
}, img_key, sub_key)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://search.bilibili.com',
}

resp = requests.get('https://api.bilibili.com/x/web-interface/search/type',
                   params=params, headers=headers)
data = resp.json()

if data.get('code') == 0:
    results = data.get('data', {}).get('result', [])
    for v in results:
        title = v.get('title', '').replace('<em class="keyword">', '').replace('</em>', '')
        play = v.get('play', 0)
        bvid = v.get('bvid', '')
        print(f'{title} - {play}播放 - https://www.bilibili.com/video/{bvid}')
```

#### B站 API 常用参数

| 参数 | 说明 | 值 |
|------|------|-----|
| `search_type` | 搜索类型 | `video`, `bangumi`, `pgc`, `live`, `article` |
| `order` | 排序方式 | `click`(播放量), `pubdate`(最新), `dm`(弹幕), `stow`(收藏) |
| `page` | 页码 | 1, 2, 3... |
| `page_size` | 每页数量 | 最大 50 |
| `keyword` | 搜索关键词 | 任意字符串 |
| `tid` | 分区 ID | 0=全部, 1=动画, 3=音乐, 119=鬼畜... |

#### B站视频数据字段

| 字段 | 说明 |
|------|------|
| `title` | 视频标题（含 HTML 高亮标签） |
| `play` | 播放量 |
| `video_review` | 弹幕数 |
| `favorites` | 收藏数 |
| `duration` | 时长 (MM:SS) |
| `author` | UP主名称 |
| `bvid` | 视频 BV 号 |
| `tag` | 标签 |

---

## 已知陷阱

### ⚠️ 不要手动注入 CDP 反检测脚本（最重要）

**症状：** Google 搜索触发 CAPTCHA，但不注入 CDP 脚本时一切正常

**原因：** undetected-chromedriver 内部已有完善的反检测机制（隐藏 webdriver 标志、修补指纹等）。手动通过 `execute_cdp_cmd` 注入的反检测脚本会与其冲突，反而暴露自动化特征。特别危险的注入：
- `plugins: [1, 2, 3, 4, 5]` — 返回数字数组而非 Plugin 对象，Google 一检测就露馅
- `navigator.webdriver = undefined` — 与 uc 内部补丁冲突
- `window.chrome = {...}` — 不完整的 chrome 对象暴露破绽

**正确做法：** 不注入任何 CDP 脚本，让 undetected-chromedriver 全权处理：
```python
driver = uc.Chrome(options=options, version_main=147)
# 不要调用 driver.execute_cdp_cmd()！
```

**实测结论：**
| 场景 | 结果 |
|------|------|
| headless + CDP 脚本注入 | ❌ Google CAPTCHA |
| headless + 不注入（让 uc 自己处理） | ✅ 搜索正常 |

### Chrome 进程残留导致 Session 创建失败

**症状：** `session not created: cannot connect to chrome at 127.0.0.1:XXXXX`

**原因：** 之前的 Chrome 实例未正确退出，端口被占用

**解决方案：**
```bash
# 强制清理所有 Chrome 进程
pkill -9 -f chrome
pkill -9 -f undetected_chromedriver
sleep 2

# 验证清理成功
ps aux | grep -i chrome | grep -v grep || echo "Chrome cleaned"
ss -tlnp | grep 9222 || echo "Port free"
```

**预防措施：**
- 使用 try-finally 包裹 driver 操作，确保 `driver.quit()` 被调用
- 每次创建 driver 前先检查端口状态

### Chrome 远程调试方案不可靠
曾尝试通过 Windows VM 的 Chrome 远程调试端口来绕过检测，但遇到多个问题：
- Chrome 147 的 `--remote-debugging-address=0.0.0.0` 参数**无效**，只监听 127.0.0.1
- 需要用 `netsh interface portproxy` 做端口转发才能远程访问
- 使用原用户数据目录 (`--user-data-dir`) 启动时，调试端口不稳定，会自行关闭
- 最终结论：**服务器端 undetected-chromedriver 是更可靠的方案**

### User-Agent 伪装
- 默认 headless Chrome 的 User-Agent 包含 `HeadlessChrome` 标记，容易被检测
- 必须手动设置正常的 User-Agent 字符串
- 当前伪装为 Windows Chrome 147

### 资源泄漏
- 忘记调用 driver.quit() 会导致 Chrome 进程残留
- 多次创建 driver 不 quit 会耗尽系统资源
- 建议用 try-finally 包裹确保释放

### Externally-Managed Python 环境
- Debian/Ubuntu 系统可能报 `externally-managed-environment` 错误
- 解决方案：`pip install --break-system-packages undetected-chromedriver selenium`
- 或使用 `pip3 install --break-system-packages` 确保安装到系统 Python

### 元素定位失败
- 页面未完全加载时查找元素会失败
- 使用 safe_get() 而非 driver.get() 可确保页面加载完成
- 动态内容可能需要 time.sleep() 等待

### JS 渲染页面抓取失败
- `stealth_chrome.py get` 命令返回的是原始 HTML，不执行 JavaScript
- 对于 JS 动态加载内容的网站（如 weather.com.cn、大部分天气/新闻门户），`get` 只能拿到空壳 HTML 框架
- **解决方案**：对于 JS 渲染页面，需要使用支持 JavaScript 渲染的工具（如 Playwright、Puppeteer 等）
- 典型失败案例：中国天气网 (weather.com.cn)、深圳市气象局 (weather.sz.gov.cn) 等政府/门户站点
- **判断依据**：如果 `get` 返回的 HTML 中关键内容区域为空或只有占位符，说明是 JS 渲染页面
