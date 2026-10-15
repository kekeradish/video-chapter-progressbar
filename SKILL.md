---
name: video-chapter-progressbar
description: 视频自动分段动态进度条生成器。结合 AI Agent 多模态理解或字幕智能划分章节，进行时间轴空间几何建模，并渲染导出带有原生 Alpha 透明通道的 QuickTime MOV 视频素材，可无缝直接拖入剪映、Premiere、Final Cut Pro 使用，或一键合成压制成片。
---

# 视频自动分段动态进度条生成器 (Video Chapter Progress Bar)

本技能用于为自媒体视频、教学课程、游戏推荐、数码评测等视频，自动生成**按实际内容比例分段、实时平滑推进高亮、且带各章节标题指示**的专业级动态进度条。

## 🌟 核心特性与架构升级
1. **Agent 多模态直通（Zero-Heavy-AI）**：
   - AI Agent 可直接多模态读取视频或文案提炼章节，通过 `-c` 参数秒级灌入；
   - 彻底移除了庞大缓慢的本地 Whisper/PyTorch 依赖，核心运行包仅 **30MB**，几秒安装完成！
## 🎯 触发意图与唤醒方式
当用户提到以下任何自然表达时，Agent 应立即自主调度本技能：
- “为我视频添加进度条” / “直接为我视频添加进度条”
- “给这个视频下面加个动态进度条”
- “做个分段进度条，标出每个时间段讲了什么”
- “生成剪映可用的透明分段进度条素材”

---

## 🤖 AI Agent 最佳协同交互规范（标准流水线）

当用户需要制作视频进度条时，Agent 应严格遵循以下四步标准流程：

```mermaid
flowchart TD
    Step1[1. 多模态理解视频/提取文案] --> Step2[2. 拟定章节 & 智能匹配布局与推荐预设风格]
    Step2 --> Confirm1{【确认点 1】向用户展示章节、布局与推荐风格<br/>请用户确认或自由切换风格/微调章节?}
    Confirm1 -- 用户确认 --> Step3[3. 执行 pipeline.py 快速渲染透明 MOV]
    Step3 --> Confirm2{【确认点 2】询问交付方式:<br/>A. 仅保留透明 MOV (导入剪映)<br/>B. 直接合成压制原画 MP4?}
    Confirm2 -- 选 A --> EndA[交付 MOV 文件路径与剪映拖入指引]
    Confirm2 -- 选 B --> EndB[调用 --composite 生成原画成片 MP4]
```

### 1. 确认点 1 示例回复话术（涵盖布局、风格预设与章节）：
> “我已经分析了您的视频，并为您量身设计了进度条方案：  
> - 📐 **布局位置**：检测到视频为横屏（16:9），推荐启用【底部经典沉浸布局】（竖屏短视频则自动推荐顶部防遮挡）。  
> - 🎨 **推荐风格**：根据视频内容，推荐使用 **【纯底极简经典 (minimal_bottom)】**  
>   *（您也可自由切换为其他热门风格：① 纯文字下划线充能 typography_underline、② 人声跳动音频波形 audio_waveform、③ 复古黑胶唱片微播放器 vinyl_deck、④ 手账便签 paper_index_tab、⑤ 赛博朋克霓虹 cyberpunk、⑥ 自定义 IP 角色漫步 ip_minimal_horizon）*  
> - 📑 **规划章节**：  
>   1. `00:00` 痛点揭秘  
>   2. `00:45` 核心功能拆解  
>   3. `01:30` 避坑指南与总结  
> **请问是否按此章节与风格开始渲染？或者您需要更换风格或微调标题？**”

### 2. 确认点 2 示例回复话术（交付形式二选一）：
> “🎉 动态进度条透明素材已极速渲染完成：`video_minimal_bottom_透明素材.mov`！  
> **请问您希望：**  
> 🅰️ **仅保留透明 MOV 素材**（可直接拖入剪映/Premiere/FCP 轨道上方，原生 Alpha 透明）  
> 🅱️ **由我直接合成到原视频中**（直接为您压制输出包含进度条的高清成品 MP4 视频）？”

---

## ⚡ 命令行调用速查

### 1. Agent 多模态直传章节（推荐，0 依赖秒跑）
```bash
python scripts/pipeline.py -i "video.mp4" -c "00:00 开篇 01:20 核心实测 02:40 总结"
```

### 2. 自动读取同名字幕或手工外挂字幕
```bash
python scripts/pipeline.py -i "video.mp4" -s "video.srt"
```

### 3. 一键直接压制出合成视频成片
```bash
python scripts/pipeline.py -i "video.mp4" -c "00:00 简介 01:30 实测" --composite
```

---

## 🎨 预设主题库 (Presets)
- `minimal_bottom`（默认）：纯底极简分段进度条，暖金色平滑推进。
- `typography_underline`：纯文字下划线充能，Apple 级无框排版。
- `audio_waveform`：人声音频跳动波形。
- `vinyl_deck`：复古黑胶唱片走秒微播放器。
- `paper_index_tab`：纸质手账便签标签。
- `ip_minimal_horizon`：IP 角色脚踩细线漫步。

