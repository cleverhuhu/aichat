# 🤖 AI聊天助手 (AI Chat Assistant)

<div align="center">

![Version](https://img.shields.io/badge/版本-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Vue.js](https://img.shields.io/badge/Vue.js-2.x-brightgreen)
![License](https://img.shields.io/badge/许可证-MIT-orange)

</div>

<p align="center">
一个功能强大的AI聊天应用，支持多种AI模型，角色扮演，语音交互和丰富的用户界面体验。
<br>
基于Vue.js + Flask构建，提供类似Discord的现代化用户界面。
</p>

![分隔线](https://i.imgur.com/waxVImv.png)

## 📋 目录

- [功能特点](#-功能特点)
- [系统架构](#-系统架构)
- [安装要求](#-安装要求)
- [安装步骤](#-安装步骤)
- [使用方法](#-使用方法)
- [配置说明](#-配置说明)
- [常见问题](#-常见问题)
- [开发计划](#-开发计划)
- [许可证](#-许可证)

## ✨ 功能特点

<table>
<tr>
<td width="50%">

### 🧠 多AI模型支持
- **Gemini** - Google的最新大语言模型
- **GPT** - OpenAI的GPT-4系列模型
- **Claude** - Anthropic的Claude系列模型
- 可自定义温度、Top-P等参数

</td>
<td width="50%">

### 🎭 角色扮演系统
- 创建、编辑、管理无限角色
- 自定义角色头像和设定
- 角色记忆与对话历史保存
- 按角色分类查看历史记录

</td>
</tr>

<tr>
<td width="50%">

### 🔊 语音交互功能
- 语音输入（语音识别）
- AI语音输出（TTS）
- 可调节语音速度
- 参考音频自定义

</td>
<td width="50%">

### 🖼️ 多模态交互
- 图片上传与识别功能
- 支持视觉模型分析图像
- 图像与文本结合问答
- 图片预览与放大功能

</td>
</tr>

<tr>
<td width="50%">

### 📝 预设管理系统
- 创建和管理提示词模板
- 导入/导出预设
- 自定义标签分类
- 调整模型参数配置

</td>
<td width="50%">

### 🎨 现代化UI
- Discord风格界面设计
- 深色/浅色主题切换
- 可自定义聊天背景
- 响应式设计，适配移动设备

</td>
</tr>
</table>

## 🏗 系统架构

```
AI聊天助手
├── 前端 (Vue.js)
│   ├── 主界面组件
│   ├── 设置面板
│   ├── 历史记录管理
│   └── 角色管理界面
│
├── 后端 (Flask)
│   ├── AI模型集成
│   ├── 角色/历史数据管理
│   ├── 预设管理 
│   └── API路由
│
└── 外部服务
    ├── AI模型API (Gemini/OpenAI/Claude)
    └── GPT-SoVITS (语音合成)
```

## 📦 安装要求

### 后端要求
- Python 3.8+
- Flask + 其他依赖包 (见`requirements.txt`)
- 支持的操作系统：Windows, macOS, Linux

### 前端要求
- Node.js 14+
- npm 或 yarn

### 可选：TTS语音服务
- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) (用于语音合成)
  - 默认运行于本地端口7865

## 🚀 安装步骤

### 1. 克隆项目
```bash
git clone [项目仓库地址]
cd [项目文件夹]
```

### 2. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 3. 安装前端依赖
```bash
cd frontend
npm install
# 或者使用yarn
# yarn install
```

### 4. 配置API密钥
在应用的设置界面中配置以下API密钥:
- Google Gemini API
- OpenAI API
- Anthropic Claude API

### 5. (可选) 设置TTS服务
如需使用AI语音功能，请安装并启动[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)服务，确保它运行在默认端口7865上。

## 🎮 使用方法

### 启动应用

**Windows用户**:
```
双击运行 run.bat
```

**Linux/MacOS用户**:
```bash
chmod +x run.sh
./run.sh
```

### 手动启动
如需分别启动前后端:

**后端**:
```bash
python backend/app.py
```

**前端**:
```bash
cd frontend
npm run serve
```

### 访问应用
启动后在浏览器中访问：`http://localhost:8080`

### 使用流程

1. **设置**: 点击底部设置图标进入设置界面
2. **配置API**: 输入AI服务API密钥
3. **创建角色**: 添加新角色或使用系统默认角色
4. **选择预设**: 选择预设模板或创建自定义预设
5. **开始聊天**: 选择角色，输入消息或使用语音输入
6. **查看历史**: 通过历史面板查看和管理聊天记录

## ⚙️ 配置说明

### API密钥获取
- [Google Gemini API](https://ai.google.dev/) - AI Studio平台注册获取
- [OpenAI API](https://platform.openai.com/) - OpenAI平台注册获取
- [Anthropic Claude API](https://console.anthropic.com/) - Anthropic控制台注册获取

### 模型选择指南

| 使用场景 | 推荐模型 | 特点 |
|---------|---------|------|
| 日常对话 | Gemini Flash / GPT-3.5 | 响应速度快，成本低 |
| 复杂问答 | GPT-4 / Claude 3 Opus | 推理能力强，回答更全面 |
| 创意写作 | Claude 3 Sonnet / GPT-4 | 创意性强，叙事能力好 |
| 图像识别 | Gemini Pro Vision / GPT-4 Vision | 支持图像理解和分析 |

### TTS服务配置
默认TTS服务地址为`http://localhost:7865`，可在设置界面修改连接地址和参数。

## ❓ 常见问题

<details>
<summary><b>为什么无法连接到后端服务？</b></summary>
<p>
请确保后端服务已启动，默认端口为5000。检查是否有其他应用占用该端口，或者检查防火墙设置。
</p>
</details>

<details>
<summary><b>语音功能无法使用？</b></summary>
<p>
请确保已安装并启动GPT-SoVITS服务，并且端口设置正确。检查浏览器是否授予了麦克风权限。
</p>
</details>

<details>
<summary><b>如何使用预设系统？</b></summary>
<p>
预设系统允许您保存不同的AI行为配置。在设置页面的"AI预设"选项卡中可以创建、编辑和管理预设。每个预设可以包含不同的指令、参数和角色设定。
</p>
</details>

<details>
<summary><b>支持哪些图片格式？</b></summary>
<p>
支持常见的图片格式，包括JPG、PNG、GIF等。上传图片大小限制为5MB。
</p>
</details>

## 📝 开发计划

- [ ] 移动端应用支持
- [ ] 本地模型集成
- [ ] 多用户支持
- [ ] 更多语音模型集成
- [ ] 插件系统

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">
<p>如有问题或建议，欢迎提交Issue或Pull Request</p>
<p>祝您使用愉快！👋</p>
</div>
