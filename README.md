# Anti-Detect Browser

反检测 Chrome 浏览器，使用 undetected-chromedriver 绕过 Google reCAPTCHA 等机器人检测。

适用于所有需要搜索或抓取网页内容的场景。

## 特性

- ✅ 绕过 Google reCAPTCHA 检测
- ✅ 伪装 User-Agent、Platform、Languages 等浏览器指纹
- ✅ 隐藏 navigator.webdriver 标志
- ✅ 支持命令行和 Python 模块两种使用方式
- ✅ 一键安装脚本，自动检测平台和 Chrome

## 快速开始

### 1. 安装依赖

```bash
bash scripts/install.sh
```

### 2. 使用

#### 命令行模式

```bash
# Google 搜索
python scripts/stealth_chrome.py search "Python 教程"

# 抓取网页
python scripts/stealth_chrome.py get https://example.com
```

#### Python 模块模式

```python
from scripts.stealth_chrome import create_stealth_driver, google_search

driver = create_stealth_driver()
results = google_search(driver, 'Python 教程', max_results=5)
driver.quit()
```

## 许可证

MIT License
