# GitHub Actions 使用指南

## 快速开始

### 第一步：初始化Git仓库（如果还没有）

```bash
# 在项目目录下执行
git init
git add .
git commit -m "Initial commit: Add brand checker app"
```

### 第二步：创建GitHub仓库并推送代码

1. **在GitHub上创建新仓库**
   - 登录 GitHub
   - 点击右上角 "+" → "New repository"
   - 输入仓库名称（如：`brand-check`）
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

2. **推送代码到GitHub**
   ```bash
   # 添加远程仓库（替换 <your-username> 和 <repo-name>）
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   
   # 推送代码
   git branch -M main
   git push -u origin main
   ```

### 第三步：触发构建

有两种方式触发构建：

#### 方式一：创建Tag触发（推荐，会自动创建Release）

```bash
# 创建tag
git tag v1.0.0

# 推送tag到GitHub
git push origin v1.0.0
```

**优点：**
- 自动创建GitHub Release
- 可以添加版本说明
- 适合正式发布

#### 方式二：手动触发（最简单）

1. 打开GitHub仓库页面
2. 点击 "Actions" 标签
3. 在左侧找到 "Build and Release" 工作流
4. 点击右侧的 "Run workflow" 按钮
5. 点击绿色的 "Run workflow" 按钮确认

**优点：**
- 不需要创建tag
- 可以随时触发
- 适合测试

### 第四步：查看构建进度

1. 点击 "Actions" 标签
2. 选择 "Build and Release" 工作流
3. 点击最新的运行记录（会显示 "in progress" 或 "completed"）
4. 可以查看每个步骤的详细日志

### 第五步：下载构建好的exe文件

#### 如果使用Tag触发（方式一）：

1. 在仓库页面，点击右侧 "Releases"
2. 找到最新发布的版本
3. 下载 `图片品牌检查工具.exe`

#### 如果使用手动触发（方式二）：

1. 在Actions页面，点击最新的运行记录
2. 滚动到页面底部
3. 在 "Artifacts" 部分，点击 `windows-app`
4. 下载zip文件并解压，里面就是 `图片品牌检查工具.exe`

## 详细步骤说明

### 完整操作流程

```bash
# 1. 确保所有文件都已提交
git status

# 2. 如果还有未提交的文件，先提交
git add .
git commit -m "Add all files"

# 3. 如果还没有远程仓库，添加它
git remote add origin https://github.com/<your-username>/<repo-name>.git

# 4. 推送代码
git push -u origin main

# 5. 创建tag触发构建（或使用手动触发）
git tag v1.0.0
git push origin v1.0.0

# 6. 等待几分钟，然后在GitHub上查看结果
```

### 查看构建日志

构建过程中，你可以：

1. **实时查看进度**
   - 进入Actions页面
   - 点击正在运行的工作流
   - 可以看到每个步骤的执行状态

2. **查看详细日志**
   - 点击任意步骤
   - 可以看到该步骤的完整输出
   - 如果出错，可以在这里查看错误信息

### 常见问题

#### Q1: 构建失败怎么办？

**检查清单：**
- ✅ 确保 `.github/workflows/build-windows.yml` 文件存在
- ✅ 确保 `brand_checker.spec` 文件存在
- ✅ 确保 `brand_checker.py` 文件存在
- ✅ 确保 `requirements.txt` 文件存在
- ✅ 查看构建日志中的错误信息

**常见错误：**
- 缺少文件：检查所有必需文件是否都已提交
- 依赖安装失败：检查 `requirements.txt` 是否正确
- 图标生成失败：这是警告，不影响构建，会继续使用默认图标

#### Q2: 如何修改构建配置？

编辑 `.github/workflows/build-windows.yml` 文件：

```yaml
# 修改Python版本
python-version: '3.10'  # 改为 '3.9' 或其他版本

# 修改构建命令
pyinstaller brand_checker.spec --clean  # 可以添加其他参数
```

#### Q3: 如何只构建不创建Release？

使用手动触发（方式二），而不是创建tag。

或者修改工作流文件，注释掉创建Release的步骤。

#### Q4: 构建需要多长时间？

通常需要 2-5 分钟：
- 环境准备：30秒
- 安装依赖：1-2分钟
- 生成图标：10秒
- 打包应用：1-2分钟
- 上传产物：30秒

#### Q5: 可以同时构建多个版本吗？

可以！每次触发都会创建一个新的构建。GitHub Actions支持并行构建。

## 工作流配置说明

当前的工作流配置（`.github/workflows/build-windows.yml`）包含：

1. **触发条件**
   - 推送tag（格式：`v*`，如 `v1.0.0`）
   - 推送到main分支
   - 手动触发

2. **构建环境**
   - Windows最新版本
   - Python 3.10

3. **构建步骤**
   - 检出代码
   - 安装Python依赖
   - 生成应用图标
   - 使用PyInstaller打包
   - 上传构建产物

4. **自动发布**
   - 如果使用tag触发，会自动创建GitHub Release
   - exe文件会附加到Release中

## 最佳实践

1. **版本管理**
   - 使用语义化版本号：`v1.0.0`, `v1.1.0`, `v2.0.0`
   - 在Release中添加更新说明

2. **测试构建**
   - 先使用手动触发测试
   - 确认构建成功后再创建tag发布

3. **代码管理**
   - 确保所有必需文件都已提交
   - 使用 `.gitignore` 排除不必要的文件

4. **监控构建**
   - 关注构建状态
   - 及时处理构建失败

## 下一步

构建成功后，你可以：

1. **测试exe文件**
   - 在Windows系统上运行
   - 测试所有功能

2. **分发应用**
   - 通过GitHub Release分享
   - 或直接下载exe文件分发

3. **持续更新**
   - 修改代码后，再次触发构建
   - 创建新tag发布新版本

