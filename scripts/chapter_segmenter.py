# -*- coding: utf-8 -*-
import re

# 常见章节转折关键词权重库
TRANSITION_PATTERNS = [
    (r'(?:大家|欢迎|今天).*?(?:分享|介绍|带来|推荐|聊聊)', "开篇简介"),
    (r'(?:第一[个点款步]|首先|第1[个点款步])', None),
    (r'(?:第二[个点款步]|其次|第2[个点款步])', None),
    (r'(?:第三[个点款步]|接着|第3[个点款步])', None),
    (r'(?:第四[个点款步]|还有|第4[个点款步])', None),
    (r'(?:第五[个点款步]|第5[个点款步])', None),
    (r'(?:第六[个点款步]|第6[个点款步])', None),
    (r'(?:第七[个点款步]|第7[个点款步])', None),
    (r'(?:第八[个点款步]|第8[个点款步])', None),
    (r'(?:第九[个点款步]|第9[个点款步])', None),
    (r'(?:下一个|来看下|再来看|还有一个|另外)', None),
    (r'(?:最后|结尾|总结|概括)', "总结结尾"),
]

def clean_title(raw_text):
    """提取精炼的章节名称（控制在 4~8 个汉字）"""
    text = re.sub(r'[，。！？、～~\s]+', ' ', raw_text).strip()
    # 去除口语停顿词
    for w in ["大家", "今天", "给大家", "介绍一个", "介绍下", "带来一个", "推荐一个", "首先", "其次", "另外", "一个", "我们来看", "这个"]:
        text = text.replace(w, "")
    text = text.strip()
    # 截取适中长度
    if len(text) > 8:
        text = text[:8]
    return text or "内容精彩看点"

def segment_by_keywords(segments, total_duration, target_chapters=None):
    """根据转折关键词与停顿语义自动切分章节"""
    split_points = []
    
    # 始终包含开头
    split_points.append({"time": 0.0, "title": "开篇简介", "desc": ""})
    
    for i, seg in enumerate(segments):
        txt = seg["text"]
        start_t = seg["start"]
        
        # 避免在太近的时间内切分（最小间隔 8 秒）
        if split_points and (start_t - split_points[-1]["time"] < 8.0):
            continue
            
        matched = False
        for pat, default_name in TRANSITION_PATTERNS:
            if re.search(pat, txt):
                name = default_name or clean_title(txt)
                split_points.append({"time": start_t, "title": name, "desc": txt[:18]})
                matched = True
                break

    # 如果切出来的章节太少，且视频较长，采用时间均匀自适应切分
    if len(split_points) < 3 and total_duration > 60:
        step = total_duration / (target_chapters or 4)
        split_points = []
        for idx in range(target_chapters or 4):
            t = idx * step
            # 找到最接近该时间点的字幕
            closest_txt = "章节导览"
            for s in segments:
                if s["start"] >= t:
                    closest_txt = clean_title(s["text"])
                    break
            split_points.append({"time": t, "title": f"第{idx+1}部分" if idx > 0 else "开篇简介", "desc": closest_txt})

    # 如果指定了目标章节数，进行合并或拆分
    if target_chapters and len(split_points) != target_chapters:
        # 简单保留或插值到目标数量
        if len(split_points) > target_chapters:
            # 优先合并时长过短的段落
            while len(split_points) > target_chapters:
                shortest_idx = 1
                min_gap = 999999
                for j in range(1, len(split_points)):
                    next_t = split_points[j+1]["time"] if j+1 < len(split_points) else total_duration
                    gap = next_t - split_points[j]["time"]
                    if gap < min_gap:
                        min_gap = gap
                        shortest_idx = j
                split_points.pop(shortest_idx)

    # 组装为标准章节对象
    chapters = []
    for idx, sp in enumerate(split_points):
        st = sp["time"]
        et = split_points[idx+1]["time"] if idx+1 < len(split_points) else total_duration
        chapters.append({
            "tag": f"{idx+1:02d}",
            "title": sp["title"],
            "start": round(st, 2),
            "end": round(et, 2),
            "desc": sp.get("desc", "")
        })
        
    return chapters
