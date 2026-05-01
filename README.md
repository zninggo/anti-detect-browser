# Anti-Detect Browser

一个给脚本和 AI Agent 用的反检测 Chrome 工具。它把真实 Chrome、undetected-chromedriver 和 Selenium 封装成简单命令，用来搜索网页、抓取页面内容，减少被搜索引擎和常见站点当成机器人拦下的概率。

适合这些场景：

- 你需要在命令行里做 Google、DuckDuckGo 或 Bing 搜索。
- 你的 Agent 需要稳定拿到搜索结果，而不是卡在 CAPTCHA 页面。
- 你想用 Python 控制一个更像真实浏览器的 Chrome 实例。
- 你只想快速抓取一个页面的 HTML，不想从头写 Selenium boilerplate。

不适合这些场景：

- 绕过登录、付费墙、权限控制或网站明确禁止的访问规则。
- 抓取高度依赖前端接口的复杂单页应用，然后期望 `get` 命令自动整理出正文。
- 长时间、大规模并发采集。这个工具更适合低频、明确目标的搜索和页面访问。

## 快速开始

```bash
git clone https://github.com/zninggo/anti-detect-browser.git
cd anti-detect-browser
bash scripts/install.sh
```

安装脚本会检查 Python 3.9+、Chrome/Chromium，并安装 `undetected-chromedriver` 和 `selenium`。

如果你在非交互式环境里运行，比如 Agent、CI 或管道脚本，可以直接用：

```bash
bash scripts/install.sh --auto
```

如果机器上已经有 Chrome，只想安装 Python 依赖：

```bash
bash scripts/install.sh --skip-chrome
```

## 先试一下

搜索：

```bash
python3 scripts/stealth_chrome.py search "Python 教程" --max-results 5
```

输出 JSON，方便脚本或 Agent 解析：

```bash
python3 scripts/stealth_chrome.py search "AI 新闻" --json --max-results 5
```

指定搜索引擎：

```bash
python3 scripts/stealth_chrome.py search "浏览器自动化" --engine google
python3 scripts/stealth_chrome.py search "浏览器自动化" --engine duckduckgo
python3 scripts/stealth_chrome.py search "浏览器自动化" --engine bing
```

抓取页面 HTML：

```bash
python3 scripts/stealth_chrome.py get https://example.com --length 1000
```

默认搜索顺序是 Google -> DuckDuckGo -> Bing。如果某个搜索引擎失败，工具会自动尝试下一个。搜索结果会过滤常见广告和付费点击跳转，尽量只返回自然结果。

## Python 用法

```python
from scripts.stealth_chrome import create_stealth_driver, search, get_page_content


driver = create_stealth_driver()
try:
    results = search(driver, 'Python 教程', max_results=5)
    for item in results:
        print(item['title'], item['url'])

    html = get_page_content(driver, 'https://example.com')
    print(html[:500])
finally:
    driver.quit()
```

一定要在最后调用 `driver.quit()`。Chrome 进程残留会导致后续 session 创建失败。

## 给 Agent 使用

任何能执行 shell 命令的 Agent 都可以直接调用这个仓库里的脚本。把下面这段放进项目的 `AGENTS.md`、`CLAUDE.md` 或类似说明文件即可：

```markdown
## Web Search

需要搜索或抓取网页时，优先使用 anti-detect-browser：

- 安装：bash /path/to/anti-detect-browser/scripts/install.sh --auto
- 搜索：python3 /path/to/anti-detect-browser/scripts/stealth_chrome.py search "关键词" --json
- 抓取：python3 /path/to/anti-detect-browser/scripts/stealth_chrome.py get <url>
- 注意：用完浏览器 driver 必须 quit；JS 重度渲染页面可能需要额外 Selenium 逻辑。
```

## 能做到什么

- 使用真实 Chrome，而不是普通 HTTP 请求。
- 隐藏常见自动化特征，包括 `navigator.webdriver`。
- 使用正常浏览器 User-Agent，避免默认 headless 标记暴露。
- 支持命令行和 Python 两种入口。
- 支持 Linux、macOS、Windows、WSL 和 Git Bash/MSYS2。

反检测不是“永远不会被拦”。搜索引擎、IP 信誉、访问频率、页面策略都会影响结果。这个工具的目标是让低频、正常用途的自动化访问更接近真实浏览器行为。

## 常见问题

### Chrome 未找到

先安装 Google Chrome 或 Chromium，然后重新运行安装脚本。

```bash
bash scripts/install.sh
```

如果你确认 Chrome 已经存在，只想跳过检测：

```bash
bash scripts/install.sh --skip-chrome
```

### Python 依赖安装失败

建议优先使用虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate
pip install undetected-chromedriver selenium
```

Debian/Ubuntu 的系统 Python 可能会报 `externally-managed-environment`。如果你确定要安装到系统环境，可以用：

```bash
pip3 install --break-system-packages undetected-chromedriver selenium
```

### 搜索没有结果

先指定另一个搜索引擎试试：

```bash
python3 scripts/stealth_chrome.py search "关键词" --engine duckduckgo --json
python3 scripts/stealth_chrome.py search "关键词" --engine bing --json
```

如果浏览器进程残留，清理后再试：

```bash
pkill -9 -f chrome
pkill -9 -f undetected_chromedriver
```

### `get` 抓不到正文

`get` 返回的是当前页面 HTML。很多网站正文由 JavaScript 后续加载，如果 HTML 里只有空容器或占位符，需要写更具体的 Selenium 逻辑等待页面元素出现。

## 项目结构

```text
anti-detect-browser/
├── SKILL.md
├── README.md
├── requirements.txt
└── scripts/
    ├── install.sh
    └── stealth_chrome.py
```

`README.md` 面向人类快速了解和上手；`SKILL.md` 面向 Agent，包含更细的使用规则、陷阱和站点专项经验。

## License

MIT License
