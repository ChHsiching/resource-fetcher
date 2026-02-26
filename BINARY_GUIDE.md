# Resource Fetcher - 二进制程序使用说明

## 📦 构建产物位置

所有二进制程序已构建完成，位置如下：

### 1. CLI 独立版（7.75 MB）
```
dist/resource-fetcher.exe
```
**用途**：命令行自动化、批处理脚本

**使用方法**：
```bash
# 查看帮助
.\dist\resource-fetcher.exe --help

# 下载专辑
.\dist\resource-fetcher.exe --url <URL>

# 带配置下载
.\dist\resource-fetcher.exe --url <URL> --output Downloads --limit 10 --renumber
```

---

### 2. NSIS 安装程序（2.4 MB）⭐ 推荐
```
tauri-gui/src-tauri/target/release/bundle/nsis/Resource Fetcher_0.2.0_x64-setup.exe
```
**用途**：普通用户日常使用

**安装后**：
- ✅ 桌面快捷方式：Resource Fetcher
- ✅ 开始菜单：Resource Fetcher
- ✅ 程序和功能：可卸载
- ✅ CLI 位置：`C:\Users\<用户>\AppData\Local\Programs\resource-fetcher-gui\Resources\cli\resource-fetcher.exe`

---

### 3. MSI 安装程序（3.6 MB）
```
tauri-gui/src-tauri/target/release/bundle/msi/Resource Fetcher_0.2.0_x64_en-US.msi
```
**用途**：企业部署、组策略

---

### 4. 便携包（10.95 MB）
```
release/Resource-Fetcher-Portable-win-x64.zip
```
**用途**：免安装、U盘携带

**使用方法**：
1. 解压 ZIP 文件到任意目录
2. 双击 `Resource-Fetcher.exe` 启动 GUI
3. CLI 位于 `runtime/cli/resource-fetcher.exe`

---

### 5. Tauri GUI 二进制（11 MB）
```
tauri-gui/src-tauri/target/release/resource-fetcher-gui.exe
```
**用途**：开发测试（需要确保 CLI 在正确位置）

---

## 🚀 快速开始

### 对于普通用户
**推荐方式**：运行 NSIS 安装程序
```
双击：tauri-gui/src-tauri/target/release/bundle/nsis/Resource Fetcher_0.2.0_x64-setup.exe
```

### 对于免安装使用
**推荐方式**：使用便携包
```
1. 解压：release/Resource-Fetcher-Portable-win-x64.zip
2. 运行：Resource-Fetcher.exe
```

### 对于命令行用户
**推荐方式**：使用 CLI 独立版
```bash
.\dist\resource-fetcher.exe --url <URL> --renumber
```

---

## 🔨 重新构建

如果需要重新构建所有产物：

```bash
# 一键构建所有产物
python build-all.py
```

这会自动创建：
- CLI 独立版
- NSIS 和 MSI 安装程序
- 便携包 ZIP

---

## 📝 版本信息

- **版本**：v0.2.0
- **构建日期**：2026-02-26
- **平台**：Windows x64
- **Python**：3.10.11（嵌入在 CLI 中）
- **Tauri**：2.10.2

---

## ✨ 特性

- ✅ CLI 和 GUI 完全解耦，各自独立可运行
- ✅ 多部署模式：便携包 + 安装程序
- ✅ 智能路径检测：自动识别便携/安装场景
- ✅ 现代 GUI：Tauri + React + TypeScript
- ✅ 无需安装 Python：所有依赖已打包

---

*最后更新：2026-02-26*
