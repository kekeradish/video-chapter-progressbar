# 🎬 Video Chapter Progress Bar (视频自动分段动态进度条生成器)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Render Speed](https://img.shields.io/badge/Speed-160%2B%20FPS-brightgreen.svg)]()
[![Alpha Output](https://img.shields.io/badge/MOV-Alpha%20Transparent-ff69b4.svg)]()

> **专为短视频创作者、B站/YouTube UP 主、剪辑师打造的 AI 动态分段进度条引擎。**  
> 一键读入视频/字幕，AI 语义自适应分段，**毫秒级渲染输出带 Alpha 原生透明通道的 QuickTime MOV 素材**，剪映 / Premiere / Final Cut Pro 拖入即用！

---

## ✨ 核心特性

- ⚡ **零环境配置门槛（Zero-Config）**：内置自动探测与自包含 FFmpeg 引擎，其他 Agent 或开发者无需手动配置系统环境变量，`pip install` 即可直接运行！
- 🚀 **160+ FPS 极速条带渲染**：攻克 2K/4K 逐帧渲染缓慢痛点，采用局部条带内存加速算法，3 分钟 2K 视频仅需 30 秒导出！
- 💎 **原生 32-bit RGBA 透明通道**：输出 Apple QuickTime RLE (`qtrle`) 格式，直接拖入剪映即可完美透明叠加，零色差、零遮挡。
- 🤖 **AI 语义动态分段大脑**：双模输入支持——既能跑 Whisper 离线语音识别听出停顿转折，也能外挂 `.srt` 字幕；根据真实内容自适应切分，绝不写死模板。
- 🚶 **自定义 IP 角色随动领航**：支持任意上传透明 PNG 角色/宠物，角色脚踩轨道向前漫步，自带自然步态呼吸颠簸动效。
- ↕️ **短视频顶部防遮挡 (Top/Bottom 双布局)**：横屏视频放底部经典沉浸；抖音/短视频一键切换放顶部，完美避开双语字幕、文案、点赞侧边栏！
- 🎨 **12 大预设样式库**：涵盖纯底极简、纯文字无框、人声跳动波形、复古黑胶、手账便签、赛博朋克与 5 大 IP 专属跑道。

---

## 🖼️ 效果预览

### 1. 顶部防遮挡版（适合抖音 / 竖屏短视频场景）
![顶部防遮挡实景](assets/preview_top.jpg)

### 2. 底部经典版（适合 B站 / YouTube / 横屏大片场景）
![底部经典实景](assets/preview_bottom.jpg)

---

## 📦 安装与环境要求

### 1. 零配置极速安装（Zero-Config）
> 💡 **无需手动配置 FFmpeg 系统变量**：本项目内置自适应探测器，依赖库自动携带跨平台静态编译的独立 FFmpeg 二进制，所有 Agent 与普通用户均可无感开箱即用！

```bash
git clone https://github.com/kekeradish/video-chapter-progressbar.git
cd video-chapter-progressbar
pip install -r requirements.txt
```

---

## ⚡ 快速上手

### 1. 基础用法：输入视频，输出透明 MOV
```bash
python scripts/pipeline.py -i "input_video.mp4" -o "output_progress.mov"
```

### 2. 抖音/短视频模式：放在顶部防遮挡
```bash
python scripts/pipeline.py -i "input_video.mp4" -pos top
```

### 3. IP 专属模式：带上你的自定义角色向前漫步
```bash
python scripts/pipeline.py -i "input_video.mp4" -p "ip_minimal_horizon" -m "my_avatar.png"
```

### 4. 外挂字幕或显式手工指定章节
```bash
# 读取外挂字幕
python scripts/pipeline.py -i "input_video.mp4" -s "subtitle.srt"

# 手工快速指定章节
python scripts/pipeline.py -i "input_video.mp4" -c "00:00 简介 01:20 核心实测 02:40 总结"
```

---

## 🎨 样式预设库 (Presets)

| 预设 ID | 风格名称 | 特点与适用场景 |
| :--- | :--- | :--- |
| `minimal_bottom` | **纯底极简经典** | 暖金充能推进、沉浸无遮挡，全场景百搭 |
| `typography_underline` | **纯文字下划线** | 样式 E：Apple 级无框排版，发光下划线充能 |
| `audio_waveform` | **人声音频波形条** | 随说话起伏跳动的真实声波频谱，科技感十足 |
| `vinyl_deck` | **黑胶唱片微播放器** | 拟物自转黑胶唱片、金属唱针走秒，生活 Vlog 质感 |
| `paper_index_tab` | **纸质手账便签** | 彩色便签纸标签，当前段落弹起图钉标记 |
| `ip_minimal_horizon` | **IP 专属-地平线漫步** | 角色脚踩金色细线迈步前进，带自然颠簸步态 |
| `ip_audio_surfer` | **IP 专属-声波浪尖冲浪** | 角色踩在跳动的音频波形浪尖上向前冲浪 |
| `ip_cyber_runner` | **IP 专属-赛博霓虹跑道** | 青粉荧光双轨，角色脚底带发光喷气拖尾 |

---

## 🤖 作为 AI Agent Skill 使用

本项目完全遵循 **Antigravity / Claude / Cursor Agent Skill 规范**。  
直接将本目录放置在你的 Skills 路径下，AI Agent 会自动识别 `SKILL.md` 并自主调度该能力。

---

## 📄 开源许可证

本项目采用 [MIT License](LICENSE) 开源协议。
