# 图片品牌检查工具

一个基于 Python 和 tkinter 的桌面应用程序，用于根据图片文件名中的品牌名清理图片文件。

**核心功能**：删除品牌存在的图片，只保留品牌不存在的图片。

## 功能特性

- 📁 选择品牌根目录和图片根目录
- 🔍 自动扫描品牌目录，识别所有品牌
- 🖼️ 从图片文件名中提取品牌名（格式：`品牌_Brador_日期_编号.jpg`）
- ✅ 智能匹配品牌（不区分大小写，不区分重音符号）
- 🗑️ 自动删除品牌存在的图片文件（只保留品牌不存在的图片）
- 🧹 自动清理空目录

## 安装要求

- Python 3.6 或更高版本
- tkinter（通常随 Python 一起安装）

## 使用方法

1. 运行程序：
```bash
python brand_checker.py
```

2. 选择品牌根目录：
   - 点击"选择目录"按钮
   - 选择包含品牌子目录的根目录
   - 每个子目录名称代表一个品牌

3. 选择图片根目录：
   - 点击"选择目录"按钮
   - 选择包含图片文件的根目录
   - 可以包含子目录

4. 扫描品牌：
   - 点击"扫描品牌"按钮
   - 程序会扫描品牌目录下的所有子目录
   - 在日志中查看发现的品牌列表

5. 开始清理：
   - 点击"开始清理"按钮
   - 程序会处理所有图片文件
   - 删除品牌存在的图片（只保留品牌不存在的图片）
   - 清理空目录

## 文件名格式

程序支持以下格式的图片文件名：
```
品牌_Brador_2025年03月16日_03_1.jpg
```

品牌名位于第一个下划线和第二个下划线之间（示例中为 `Brador`）。

## 品牌匹配规则

- 不区分大小写：`Brador`、`BRADOR`、`brador` 都会被匹配
- 不区分重音符号：`Café` 和 `Cafe` 会被视为相同品牌
- 支持法文等带声调字母的匹配

## 注意事项

⚠️ **警告**：此程序会永久删除文件，请在使用前备份重要数据！

- 程序会删除品牌存在的图片文件（只保留品牌不存在的图片）
- 程序会保留无法提取品牌名的图片文件
- 程序会删除空的子目录
- 操作不可撤销，请谨慎使用

## 示例

假设：
- 品牌目录包含：`Brador`、`Nike`、`Adidas` 等子目录
- 图片目录包含文件：`品牌_Brador_2025年03月16日_03_1.jpg`、`品牌_Nike_2025年03月16日_03_2.jpg`、`品牌_Unknown_2025年03月16日_03_3.jpg`

处理结果：
- `品牌_Brador_2025年03月16日_03_1.jpg` → 删除（品牌存在）
- `品牌_Nike_2025年03月16日_03_2.jpg` → 删除（品牌存在）
- `品牌_Unknown_2025年03月16日_03_3.jpg` → 保留（品牌不存在）

## 构建 Windows 安装包

项目已配置 GitHub Actions 自动构建 Windows 可执行文件。

### 快速开始

1. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```

2. **触发构建**
   - **方式一（推荐）**：创建 tag 自动构建并发布
     ```bash
     git tag v1.0.0
     git push origin v1.0.0
     ```
   - **方式二**：在 GitHub Actions 页面手动触发

3. **下载构建结果**
   - 如果使用 tag 触发：在 Releases 页面下载 `图片品牌检查工具.exe`
   - 如果手动触发：在 Actions 页面的 Artifacts 中下载

详细说明请查看 [GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)

### 本地构建

如果需要本地构建：

```bash
# 安装依赖
pip install -r requirements.txt

# 生成图标（可选）
python generate_icon.py

# 构建可执行文件
pyinstaller brand_checker.spec --clean
```

构建完成后，可执行文件在 `dist/图片品牌检查工具.exe`

## 开发

项目结构：
```
brand-check/
├── brand_checker.py              # 主程序文件
├── brand_checker.spec            # PyInstaller 配置文件
├── generate_icon.py              # 图标生成脚本
├── requirements.txt              # 依赖文件
├── .github/
│   └── workflows/
│       └── build-windows.yml     # GitHub Actions 工作流
├── GITHUB_ACTIONS_GUIDE.md      # GitHub Actions 使用指南
└── README.md                     # 说明文档
```

## 许可证

MIT License
