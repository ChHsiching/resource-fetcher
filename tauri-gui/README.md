# Resource Fetcher GUI (Tauri + React)

现代化的桌面应用程序，使用 Tauri + React + TypeScript + TailwindCSS 构建。

## 技术栈

### 前端
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **TailwindCSS 3.x** - 样式框架
- **Vite** - 构建工具

### 后端
- **Tauri 2.0** - 桌面应用框架
- **Rust** - 后端逻辑
- **Python CLI** - 核心下载引擎（已存在）

## 设计风格

专业商务风格，特点：
- 扁平化设计，极简阴影
- 适度圆角 (4-8px)
- 高对比度配色
- Inter 字体
- Light/Dark 主题切换

## 开发环境要求

1. **Node.js** 18+ 和 npm/pnpm/yarn
2. **Rust** 1.70+ (包括 cargo)
3. **Python** 3.10+ (用于 CLI)
4. **WebView2** (Windows，通常已预装)

## 安装步骤

### 1. 安装前端依赖

```bash
cd tauri-gui
npm install
# 或
pnpm install
# 或
yarn install
```

### 2. 构建 Python CLI

```bash
# 从项目根目录
python build.py --cli
```

CLI 可执行文件将位于 `dist/` 目录。

### 3. 启动开发服务器

```bash
npm run tauri dev
```

这将：
- 启动 Vite 开发服务器 (http://localhost:1420)
- 编译 Rust 后端代码
- 打开 Tauri 应用程序窗口

## 构建生产版本

```bash
npm run tauri build
```

构建产物将位于 `src-tauri/target/release/bundle/` 目录。

## 项目结构

```
tauri-gui/
├── src/                    # 前端源代码
│   ├── App.tsx            # 主应用组件
│   ├── main.tsx           # 入口文件
│   └── index.css          # 全局样式
├── src-tauri/             # Rust 后端
│   ├── src/main.rs        # Rust 主程序
│   ├── Cargo.toml         # Rust 依赖配置
│   └── tauri.conf.json    # Tauri 配置
├── index.html             # HTML 模板
├── package.json           # 前端依赖配置
├── tsconfig.json          # TypeScript 配置
├── vite.config.ts         # Vite 配置
└── tailwind.config.js     # TailwindCSS 配置
```

## 功能特性

- ✅ 现代化的界面设计
- ✅ Light/Dark 主题切换
- ✅ 响应式布局
- ✅ 跨平台支持 (Windows, macOS, Linux)
- ✅ 小体积安装包 (<50MB)
- ✅ 高性能启动

## 与 Python CLI 的集成

Python CLI 通过 subprocess 调用：

```rust
// Rust 代码示例
let cli_path = get_cli_path()?;
let output = Command::new(&cli_path)
    .arg("album")
    .arg(&url)
    .arg("--output").arg(&output_dir)
    .output()?;
```

## 自动化测试

### 测试框架

- **Vitest** - 单元测试和集成测试
- **@testing-library/react** - React 组件测试
- **Playwright** - 端到端测试

### 运行测试

#### 单元测试
```bash
# 运行所有单元测试
npm run test

# 监听模式（开发时使用）
npm run test:watch

# 生成覆盖率报告
npm run test:coverage

# 在 UI 中运行测试
npm run test:ui
```

#### 集成测试
```bash
# 测试 Tauri 命令调用
npm run test tests/integration
```

#### E2E 测试
```bash
# 首次运行需要安装浏览器
npx playwright install

# 运行 E2E 测试
npm run test:e2e

# 在 UI 中运行 E2E 测试
npm run test:e2e -- --ui
```

### 测试结构

```
tests/
├── setup.ts              # 测试环境配置（mocks）
├── unit/                 # 单元测试
│   └── App.test.tsx     # App 组件测试
├── integration/          # 集成测试
│   └── downloadCommands.test.ts  # Tauri 命令测试
└── e2e/                  # E2E 测试
    └── app.spec.ts      # 完整应用流程测试
```

### 测试覆盖率

覆盖率报告生成在 `coverage/` 目录：
- `index.html` - 交互式 HTML 报告
- `coverage-final.json` - JSON 格式报告
- `lcov.info` - LCOV 格式报告

## 构建脚本

### 快速设置（开发环境）

#### Windows
```powershell
.\scripts\setup-dev.ps1
```

#### Unix/Linux/macOS
```bash
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh
```

这将自动：
- 检查 Node.js、Rust、Python 安装
- 使用 nvm 切换到 Node 20
- 创建 Python venv
- 安装所有依赖
- 运行测试验证环境

### 构建生产版本

#### Windows
```powershell
# 开发构建
.\scripts\build.ps1

# 生产构建（优化）
.\scripts\build.ps1 -Release

# 详细输出
.\scripts\build.ps1 -Release -Verbose
```

#### Unix/Linux/macOS
```bash
# 开发构建
./scripts/build.sh

# 生产构建（优化）
./scripts/build.sh --release

# 详细输出
./scripts/build.sh --release --verbose
```

构建产物位于 `src-tauri/target/release/bundle/` 目录。

## 开发路线图

### Phase 1: 基础界面 ✅
- [x] 项目结构搭建
- [x] 基础 UI 组件
- [x] Light/Dark 主题
- [x] Rust 后端集成
- [x] venv Python 支持
- [x] 自动化测试框架

### Phase 2: 核心功能 (进行中)
- [x] URL 输入与验证
- [x] 配置选项
- [ ] 进度显示
- [ ] 日志输出

### Phase 3: 高级功能
- [ ] 下载历史记录
- [ ] 批量下载
- [ ] 配置持久化
- [ ] 错误处理

### Phase 4: 打包与分发
- [ ] 代码签名
- [ ] 安装程序制作
- [ ] 自动更新

## 许可证

MIT License - 详见项目根目录 LICENSE 文件
