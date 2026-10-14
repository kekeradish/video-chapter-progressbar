---
name: video-chapter-progressbar
description: 视频自动分段动态进度条生成器。自动根据视频语音或字幕智能划分章节，进行时间轴空间几何建模，并渲染导出带有原生 Alpha 透明通道的 QuickTime MOV 视频素材，可无缝直接拖入剪映、Premiere、Final Cut Pro 使用。
---

# 视频自动分段动态进度条生成器 (Video Chapter Progress Bar)

本技能用于为自媒体视频、教学课程、游戏推荐、数码评测等视频，自动生成**按实际内容比例分段、实时平滑推进高亮、且带各章节标题指示**的专业级底部动态进度条。

## 核心特性
1. **多模态输入自适应**：
   - **纯视频/音频**：自动调用轻量 Whisper 毫秒级语音识别，智能提取转折词与内容亮点；
   - **外挂字幕 (.srt / .vtt)**：秒级免推理直接读取字幕时间戳与文案；
   - **手工/半自动指定**：支持用户直接提供章节时间点文本（如 `00:00 开篇, 01:20 火箭筒`）。
2. **章节数量与粒度自适应**：
   - 彻底告别死板的固定分段，根据视频时长与语义自然转折动态划分（短视频 2~3 段，长视频 5~10 段）；
   - 支持通过 `-n / --num_chapters` 手动指定目标章节数。
3. **空间几何防挤占算法**：
   - 支持任意分辨率（横屏 1080P/2K/4K，竖屏 9:16 抖音小红书）；
   - 针对超短段落（如 3 秒问候）内置文字自适应折叠机制，确保文字 100% 永不挤占重叠。
4. **剪映原生即用（零门槛对齐）**：
   - 输出原生带 32-bit RGBA Alpha 透明通道的 QuickTime `.mov` 素材；
   - 拖入剪映主视频上层轨道自动 1:1 吸附对齐，无需抠像、无需手动调位置。

---

## 触发场景与意图识别
当用户提到以下需求时自动激活本技能：
- “给这个视频下面加个动态进度条”
- “做个分段进度条，标出每个时间段讲了什么”
- “视频底部加个章节指示条”
- “生成剪映可用的透明进度条素材”
- “根据字幕自动做个视频进度条”

---

## 执行流水线工作流 (Workflow)

```mermaid
flowchart LR
    A[输入: MP4视频 / 字幕] --> B[scripts/transcribe.py<br/>音轨提取与多模态解析]
    B --> C[scripts/chapter_segmenter.py<br/>语义章节聚类与标题提炼]
    C --> D[scripts/geometry.py<br/>时间轴空间几何映射]
    D --> E[scripts/renderer.py + encoder.py<br/>局部条带加速与透明编码]
    E --> F[输出: 原生透明MOV素材 / 合成MP4]
```

### 快速调用命令示例

#### 1. 默认极简纯净版（全自动提取 + 导出透明素材）
```bash
python .agents/skills/video-chapter-progressbar/scripts/pipeline.py -i "D:/视频/评测.mp4"
```

#### 2. 外挂字幕文件加速模式（免语音识别耗时）
```bash
python .agents/skills/video-chapter-progressbar/scripts/pipeline.py -i "D:/视频/评测.mp4" -s "D:/视频/评测.srt"
```

#### 3. 指定样式预设与章节数量
```bash
python .agents/skills/video-chapter-progressbar/scripts/pipeline.py -i "D:/视频/评测.mp4" -p capsule_details -n 5
```

#### 4. 一键直接合成原画成片
```bash
python .agents/skills/video-chapter-progressbar/scripts/pipeline.py -i "D:/视频/评测.mp4" --composite
```

---

## 预设主题库 (Presets)
- `minimal_bottom`（默认）：纯底部极简分段进度条，紧贴底边，无大遮挡，当前段暖金色平滑推进，文字高亮金色。
- `capsule_details`：左侧带磨砂悬浮胶囊卡片，显示章节大标题、功能特性、动态走秒时间戳。
- `cyberpunk`：赛博朋克霓虹荧光风格，粉青撞色，适合电竞与潮酷风格。
