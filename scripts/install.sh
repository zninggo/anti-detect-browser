#!/bin/bash
# Anti-Detect Browser - 一键安装脚本
# 适用于 Linux / macOS / Windows (Git Bash / WSL / MSYS2)
# 支持 Hermes / Claude Code / Codex 等任意 agent
#
# 用法：
#   bash install.sh                  # 交互式安装（人工执行时）
#   bash install.sh --auto           # 强制全自动，跳过所有确认
#   bash install.sh --skip-chrome    # 只装 Python 依赖，跳过 Chrome 检测
#   bash install.sh --help           # 显示帮助
#
# 自动检测：非交互式终端（Agent / 管道）自动跳过确认提示

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色（非终端时禁用）
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    CYAN='\033[0;36m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' CYAN='' NC=''
fi

# 参数解析
AUTO=false
SKIP_CHROME=false
for arg in "$@"; do
    case "$arg" in
        --auto) AUTO=true ;;
        --skip-chrome) SKIP_CHROME=true ;;
        --help|-h)
            echo "用法: bash install.sh [选项]"
            echo ""
            echo "选项:"
            echo "  --auto          全自动安装，跳过所有确认"
            echo "  --skip-chrome   只装 Python 依赖，跳过 Chrome 检测"
            echo "  --help, -h      显示此帮助"
            echo ""
            echo "自动行为：非交互式终端（Agent / 管道）自动等同 --auto"
            exit 0
            ;;
    esac
done

# 自动检测：非交互式终端 → 强制全自动模式
# [ -t 0 ] 检查 stdin 是否为终端，[ -t 1 ] 检查 stdout 是否为终端
# Agent / 管道 / 子进程调用时通常都不是终端
if [ -t 0 ] && [ -t 1 ]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
    AUTO=true
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Anti-Detect Browser - 依赖安装${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
if [ "$INTERACTIVE" = false ]; then
    echo -e "🤖 检测到非交互式环境，自动进入全自动模式"
    echo ""
fi

# ============================================================
# 检测操作系统
# ============================================================
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="linux" ;;
    Darwin*)    OS="macos" ;;
    CYGWIN*|MINGW*|MSYS*) OS="windows" ;;
esac

echo -e "🖥️  操作系统: ${GREEN}${OS}${NC}"

# ============================================================
# 检测 Python
# ============================================================
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' || true)
        if [ -n "$version" ]; then
            major=$(echo "$version" | cut -d. -f1)
            minor=$(echo "$version" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
                PYTHON="$cmd"
                break
            fi
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${RED}❌ 未找到 Python 3.9+，请先安装 Python${NC}"
    echo ""
    echo "  Linux:  sudo apt install python3 / sudo yum install python3"
    echo "  macOS:  brew install python3"
    echo "  Windows: https://www.python.org/downloads/"
    exit 1
fi

echo -e "✅ Python: ${GREEN}$($PYTHON --version)${NC}"

# ============================================================
# 检测 Chrome（除非 --skip-chrome）
# ============================================================
CHROME_FOUND=false
CHROME_PATH=""

if [ "$SKIP_CHROME" = false ]; then
    # 按平台检测 Chrome 路径
    case "$OS" in
        linux)
            for p in \
                /usr/bin/google-chrome \
                /usr/bin/google-chrome-stable \
                /usr/bin/chromium-browser \
                /usr/bin/chromium \
                /snap/bin/google-chrome \
                /opt/google/chrome/google-chrome; do
                if [ -x "$p" ]; then
                    CHROME_PATH="$p"
                    CHROME_FOUND=true
                    break
                fi
            done
            ;;
        macos)
            for p in \
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
                "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
                if [ -x "$p" ]; then
                    CHROME_PATH="$p"
                    CHROME_FOUND=true
                    break
                fi
            done
            ;;
        windows)
            # Windows 常见 Chrome 安装路径
            for p in \
                "/c/Program Files/Google/Chrome/Application/chrome.exe" \
                "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
                "$LOCALAPPDATA/Google/Chrome/Application/chrome.exe" \
                "$PROGRAMFILES/Google/Chrome/Application/chrome.exe" \
                "${PROGRAMFILES(X86)}/Google/Chrome/Application/chrome.exe" \
                "/d/Program Files/Google/Chrome/Application/chrome.exe" \
                "/d/Program Files (x86)/Google/Chrome/Application/chrome.exe"; do
                if [ -n "$p" ] && [ -f "$p" ]; then
                    CHROME_PATH="$p"
                    CHROME_FOUND=true
                    break
                fi
            done
            # 也检查 where 命令 (Windows)
            if [ "$CHROME_FOUND" = false ] && command -v where &>/dev/null; then
                found=$(where chrome 2>/dev/null || where google-chrome 2>/dev/null || true)
                if [ -n "$found" ]; then
                    CHROME_PATH=$(echo "$found" | head -1)
                    CHROME_FOUND=true
                fi
            fi
            ;;
    esac

    if [ "$CHROME_FOUND" = true ]; then
        echo -e "✅ Chrome: ${GREEN}${CHROME_PATH}${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠️  未检测到 Google Chrome${NC}"
        echo ""

        if [ "$AUTO" = true ]; then
            if [ "$INTERACTIVE" = false ]; then
                echo -e "${YELLOW}  非交互式环境，跳过 Chrome 安装，继续安装 Python 依赖${NC}"
            else
                echo -e "${YELLOW}  跳过 Chrome 安装（--auto 模式），继续安装 Python 依赖${NC}"
            fi
        else
            case "$OS" in
                linux)
                    echo "  可选操作：自动安装 Chrome"
                    echo ""
                    if command -v apt &>/dev/null; then
                        echo "    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -"
                        echo "    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list"
                        echo "    sudo apt update && sudo apt install -y google-chrome-stable"
                    elif command -v yum &>/dev/null; then
                        echo "    sudo yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm"
                    elif command -v pacman &>/dev/null; then
                        echo "    sudo pacman -S google-chrome"
                    fi
                    ;;
                macos)
                    echo "  可选操作：brew install --cask google-chrome"
                    ;;
                windows)
                    echo "  请手动下载安装："
                    echo "    https://www.google.com/chrome/"
                    echo ""
                    echo "  或使用 winget（如果有）："
                    echo "    winget install Google.Chrome"
                    ;;
            esac
            echo ""
            read -p "  是否继续安装 Python 依赖？(Y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Nn]$ ]]; then
                exit 1
            fi
        fi
    fi
else
    echo -e "⏭️  跳过 Chrome 检测 (--skip-chrome)"
fi

# ============================================================
# 安装 Python 依赖
# ============================================================
echo ""
echo -e "📦 安装 Python 依赖..."

# 检测是否在 venv 中
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "   检测到虚拟环境: ${GREEN}${VIRTUAL_ENV}${NC}"
    PIP_CMD="$PYTHON -m pip"
else
    PIP_CMD="$PYTHON -m pip"
    # 如果有 --user 支持且不是 root，用 --user 避免权限问题
    if [ "$(id -u)" -ne 0 ] && [ "$OS" != "windows" ]; then
        PIP_CMD="$PYTHON -m pip install --user"
    fi
fi

$PIP_CMD install --quiet undetected-chromedriver selenium 2>/dev/null || \
$PYTHON -m pip install --quiet undetected-chromedriver selenium

# ============================================================
# 验证安装
# ============================================================
echo ""
echo -e "🔍 验证安装..."
$PYTHON -c "
import undetected_chromedriver
import selenium
print(f'  undetected-chromedriver: {undetected_chromedriver.__version__}')
print(f'  selenium: {selenium.__version__}')
" 2>/dev/null || {
    echo -e "${RED}❌ Python 依赖安装失败，请手动执行：${NC}"
    echo "  pip install undetected-chromedriver selenium"
    exit 1
}

# ============================================================
# 完成
# ============================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "使用方式："
echo ""
echo "  命令行搜索:"
echo "    $PYTHON $SCRIPT_DIR/stealth_chrome.py search \"关键词\""
echo ""
echo "  命令行抓取:"
echo "    $PYTHON $SCRIPT_DIR/stealth_chrome.py get https://example.com"
echo ""
echo "  Python 导入:"
echo "    from stealth_chrome import create_stealth_driver, google_search"
echo ""
echo "  Python 测试:"
echo "    $PYTHON $SCRIPT_DIR/stealth_chrome.py"
echo ""
