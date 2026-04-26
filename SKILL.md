---
name: anti-detect-browser
description: 反检测 Chrome 浏览器 — 使用 undetected-chromedriver 绕过机器人检查
triggers:
  - 需要搜索引擎查询时
  - 需要抓取网页内容时
  - 需要访问可能有反爬检测的网站时
---

# Anti-Detect Browser

反检测 Chrome 浏览器，使用 undetected-chromedriver 绕过 Google reCAPTCHA 等机器人检测。
适用于所有需要搜索或抓取网页内容的场景。

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
# Google 搜索
python scripts/stealth_chrome.py search "Python 教程"

# 抓取网页
python scripts/stealth_chrome.py get https://example.com

# 指定结果数量
python scripts/stealth_chrome.py search "AI 新闻" --max-results 5
```

#### 方式 B：作为 Python 模块导入

```python
from scripts.stealth_chrome import create_stealth_driver, google_search, get_page_content

driver = create_stealth_driver()
results = google_search(driver, 'Python 教程', max_results=5)
driver.quit()
```

#### 方式 C：Shell 调用（适用于 Claude Code / Codex 等）

```bash
python3 ~/.hermes/skills/anti-detect-browser/scripts/stealth_chrome.py search "关键词"
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

### google_search(driver, query, max_results=10)
Google 搜索
- `driver`: Chrome 实例
- `query`: 搜索关键词
- `max_results`: 最大结果数（默认 10）
- 返回: list of dict，每个包含 'title' 和 'url'

## 使用示例

### 示例 1：Google 搜索
```python
from scripts.stealth_chrome import create_stealth_driver, google_search

driver = create_stealth_driver()
results = google_search(driver, 'Python 教程', max_results=5)
for i, r in enumerate(results, 1):
    print(f"{i}. {r['title']}")
    print(f"   {r['url']}")
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

本 skill 不限于 Hermes，任何支持 shell 调用的 Agent 都能用。

### Claude Code / Codex / Cursor

1. **找到 skill 目录**：本 skill 位于 `~/.hermes/skills/anti-detect-browser/`
2. **安装依赖**：`bash ~/.hermes/skills/anti-detect-browser/scripts/install.sh`
3. **调用**：`python3 ~/.hermes/skills/anti-detect-browser/scripts/stealth_chrome.py search "关键词"`

或者在项目的 CLAUDE.md / AGENTS.md 中添加引用：

```markdown
## 搜索工具
需要搜索或抓取网页时，使用反检测浏览器：
- 安装：bash ~/.hermes/skills/anti-detect-browser/scripts/install.sh
- 搜索：python3 ~/.hermes/skills/anti-detect-browser/scripts/stealth_chrome.py search "关键词"
- 抓取：python3 ~/.hermes/skills/anti-detect-browser/scripts/stealth_chrome.py get <url>
```

### 任意 Python 脚本

```python
import sys
sys.path.insert(0, '/root/.hermes/skills/anti-detect-browser/scripts')
from stealth_chrome import create_stealth_driver, google_search

driver = create_stealth_driver()
results = google_search(driver, '查询内容')
driver.quit()
```

## 反检测效果
- navigator.webdriver: None（正常浏览器也是这个值）
- User-Agent: 伪装为 Windows Chrome 147
- Platform: 伪装为 Win32
- Languages: zh-CN, zh, en-US, en
- 已通过 Google 搜索测试，不会触发 reCAPTCHA

## 关键点
1. **必须在最后调用 driver.quit()** 释放资源
2. 搜索结果返回 list of dict，每个包含 'title' 和 'url'
3. 如果需要点击页面元素、填表等操作，用 selenium 的 By 定位
4. 每次只创建一个 driver 实例，用完立即 quit
5. 建议用 try-finally 包裹确保资源释放

## 已知陷阱

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
- **解决方案**：先用 `search` 命令找到目标 URL，然后改用 Hermes 内置的 `browser_navigate` + `browser_snapshot` 工具渲染页面获取内容
- 典型失败案例：中国天气网 (weather.com.cn)、深圳市气象局 (weather.sz.gov.cn) 等政府/门户站点
- **判断依据**：如果 `get` 返回的 HTML 中关键内容区域为空或只有占位符，说明是 JS 渲染页面
