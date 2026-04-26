# Anti-Detect Browser

反检测 Chrome 浏览器，使用 undetected-chromedriver 绕过 Google reCAPTCHA 等机器人检测。

适用于所有需要搜索或抓取网页内容的场景，支持 Claude Code、Codex、Cursor 等 AI Agent 调用。

## 特性

- ✅ 绕过 Google reCAPTCHA 检测
- ✅ 伪装 User-Agent、Platform、Languages 等浏览器指纹
- ✅ 隐藏 navigator.webdriver 标志
- ✅ 支持命令行和 Python 模块两种使用方式
- ✅ 一键安装脚本，自动检测平台和 Chrome
- ✅ 支持 Linux / macOS / Windows

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/zninggo/anti-detect-browser.git
cd anti-detect-browser
```

### 2. 安装依赖

```bash
bash scripts/install.sh
```

安装脚本会自动：
- 检测操作系统（Linux/macOS/Windows）
- 检测 Python 3.9+
- 检测 Google Chrome 或 Chromium
- 安装 Python 依赖（undetected-chromedriver、selenium）

**安装选项：**
```bash
bash scripts/install.sh              # 交互式安装
bash scripts/install.sh --auto       # 全自动，跳过所有确认
bash scripts/install.sh --skip-chrome  # 只装 Python 依赖
```

### 3. 验证安装

```bash
# 检查 Chrome
google-chrome --version || chromium-browser --version

# 检查 Python 依赖
python3 -c "import undetected_chromedriver; import selenium; print('OK')"
```

### 4. 使用

#### 命令行模式

```bash
# Google 搜索
python3 scripts/stealth_chrome.py search "Python 教程"

# 抓取网页
python3 scripts/stealth_chrome.py get https://example.com

# 指定结果数量
python3 scripts/stealth_chrome.py search "AI 新闻" --max-results 5

# JSON 格式输出
python3 scripts/stealth_chrome.py search "Python" --json
```

#### Python 模块模式

```python
from scripts.stealth_chrome import create_stealth_driver, google_search, get_page_content

# 创建驱动
driver = create_stealth_driver()

# Google 搜索
results = google_search(driver, 'Python 教程', max_results=5)
for r in results:
    print(f"{r['title']}: {r['url']}")

# 抓取网页
html = get_page_content(driver, 'https://example.com')
print(html[:500])

# 记得释放资源
driver.quit()
```

## AI Agent 使用指南

本工具可以被任何支持 shell 调用的 AI Agent 使用。以下是各 Agent 的使用方法：

### Claude Code / Cursor / Codex

**方式 1：直接在对话中告诉 Agent**

```
请使用 anti-detect-browser 工具搜索 "Python 教程"，它位于 ~/anti-detect-browser/
安装命令：bash ~/anti-detect-browser/scripts/install.sh
搜索命令：python3 ~/anti-detect-browser/scripts/stealth_chrome.py search "关键词"
抓取命令：python3 ~/anti-detect-browser/scripts/stealth_chrome.py get <url>
```

**方式 2：在项目配置文件中添加**

在项目的 `CLAUDE.md`、`.cursorrules` 或 `AGENTS.md` 中添加：

```markdown
## 搜索工具

需要搜索或抓取网页时，使用反检测浏览器（anti-detect-browser）：

- 仓库位置：~/anti-detect-browser
- 安装依赖：bash ~/anti-detect-browser/scripts/install.sh
- 搜索：python3 ~/anti-detect-browser/scripts/stealth_chrome.py search "关键词"
- 抓取：python3 ~/anti-detect-browser/scripts/stealth_chrome.py get <url>
- JSON 输出：python3 ~/anti-detect-browser/scripts/stealth_chrome.py search "关键词" --json

注意事项：
- 每次使用前确保已安装依赖
- 搜索结果包含 title 和 url 字段
- 对于 JS 渲染的页面，get 命令可能无法获取完整内容
```

### Hermes Agent

在 Hermes 的 skill 目录中创建符号链接：

```bash
ln -s ~/anti-detect-browser ~/.hermes/skills/anti-detect-browser
```

### 任意 Python 脚本

```python
import sys
sys.path.insert(0, '/path/to/anti-detect-browser/scripts')
from stealth_chrome import create_stealth_driver, google_search

driver = create_stealth_driver()
results = google_search(driver, '查询内容')
for r in results:
    print(f"{r['title']}: {r['url']}")
driver.quit()
```

## API 参考

### `create_stealth_driver(headless=True, window_size='1920,1080', lang='zh-CN')`

创建反检测 Chrome 实例。

- `headless`: 是否无头模式（默认 True）
- `window_size`: 窗口大小（默认 1920x1080）
- `lang`: 语言设置（默认 zh-CN）
- 返回: undetected_chromedriver.Chrome 实例

### `safe_get(driver, url, timeout=10)`

安全访问 URL，等待页面加载完成。

- `driver`: Chrome 实例
- `url`: 目标 URL
- `timeout`: 超时时间（默认 10 秒）
- 返回: 页面标题

### `get_page_content(driver, url=None)`

获取页面完整 HTML 内容。

- `driver`: Chrome 实例
- `url`: 可选 URL，不提供则获取当前页面
- 返回: HTML 字符串

### `google_search(driver, query, max_results=10)`

Google 搜索。

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

### 示例 4：JSON 格式输出（适合 Agent 解析）

```bash
python3 scripts/stealth_chrome.py search "Python 教程" --json --max-results 3
```

输出：
```json
[
  {
    "title": "Python 教程 | 菜鸟教程",
    "url": "https://www.runoob.com/python/python-tutorial.html"
  },
  ...
]
```

## 反检测效果

- `navigator.webdriver`: None（正常浏览器也是这个值）
- User-Agent: 伪装为 Windows Chrome 147
- Platform: 伪装为 Win32
- Languages: zh-CN, zh, en-US, en
- 已通过 Google 搜索测试，不会触发 reCAPTCHA

## 注意事项

1. **必须在最后调用 `driver.quit()`** 释放资源
2. 搜索结果返回 list of dict，每个包含 'title' 和 'url'
3. 如果需要点击页面元素、填表等操作，用 selenium 的 By 定位
4. 每次只创建一个 driver 实例，用完立即 quit
5. 建议用 try-finally 包裹确保资源释放

## 依赖

- Python 3.9+
- Google Chrome 或 Chromium
- undetected-chromedriver
- selenium

## 故障排除

### Chrome 未找到

```
❌ 未检测到 Google Chrome
```

**解决方案：**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y google-chrome-stable

# macOS
brew install --cask google-chrome

# 或跳过 Chrome 检测，只装 Python 依赖
bash scripts/install.sh --skip-chrome
```

### Python 依赖安装失败

```
❌ Python 依赖安装失败
```

**解决方案：**
```bash
# 方式 1：使用 --break-system-packages
pip3 install --break-system-packages undetected-chromedriver selenium

# 方式 2：使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install undetected-chromedriver selenium
```

### externally-managed-environment 错误

Debian/Ubuntu 系统可能出现此错误。

**解决方案：**
```bash
pip3 install --break-system-packages undetected-chromedriver selenium
```

### JS 渲染页面抓取失败

`get` 命令返回的是原始 HTML，不执行 JavaScript。

**解决方案：**
- 对于 JS 渲染的页面，需要使用支持 JavaScript 渲染的工具（如 Playwright、Puppeteer）
- 判断依据：如果返回的 HTML 中关键内容区域为空，说明是 JS 渲染页面

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
