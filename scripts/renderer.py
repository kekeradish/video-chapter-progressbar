# -*- coding: utf-8 -*-
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def safe_draw_rect(draw, bbox, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = bbox
    if (x1 - x0) >= (2 * radius + 2) and (y1 - y0) >= (2 * radius + 2):
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)
    elif x1 > x0 and y1 > y0:
        draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

def format_time(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

class StripRenderer:
    def __init__(self, geo, preset, font_path, mascot_path=None):
        self.geo = geo
        self.preset = preset
        self.width = geo["width"]
        self.height = geo["height"]
        self.strip_h = geo["strip_height"]
        self.strip_y_start = geo["strip_y_start"]
        self.position = geo.get("position", "bottom")
        self.font_path = font_path
        self.preset_id = preset.get("id", "minimal_bottom")

        # 吉祥物加载
        self.mascot_path = mascot_path
        if not self.mascot_path and "mascot_config" in preset:
            default_demo = "C:/Users/lm666/.gemini/antigravity/brain/929ac5e7-fa13-48ce-90b9-4f22697d7a5a/demo_user_mascot.png"
            if os.path.exists(default_demo):
                self.mascot_path = default_demo

        self.mascot_img = None
        if self.mascot_path and os.path.exists(self.mascot_path):
            try:
                raw_m = Image.open(self.mascot_path).convert("RGBA")
                cfg = preset.get("mascot_config", {})
                target_h = cfg.get("target_height_px", 68 if self.position == "bottom" else 58)
                asp = raw_m.width / raw_m.height
                self.mascot_img = raw_m.resize((int(target_h * asp), target_h), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"警告: 无法加载吉祥物图片 ({e})", flush=True)

        font_sizes = preset.get("font_sizes", {})
        self.font_normal = ImageFont.truetype(font_path, font_sizes.get("title_normal", 20))
        self.font_active = ImageFont.truetype(font_path, font_sizes.get("title_active", 22))

        # 预先绘制静态背景底图 (条带高度)
        self.base_strip = Image.new("RGBA", (self.width, self.strip_h), (0, 0, 0, 0))
        draw_base = ImageDraw.Draw(self.base_strip)

        # 柔和渐变暗影 (根据 position 决定渐变方向)
        sh_color = (5, 8, 14)
        if self.position == "top":
            # 顶部模式：从上往下由深变浅
            for i in range(self.strip_h):
                alpha = int(145 * ((self.strip_h - i) / float(self.strip_h))**1.6)
                draw_base.line([(0, i), (self.width, i)], fill=(*sh_color, alpha))
        else:
            # 底部模式：从下往上由浅变深
            for i in range(self.strip_h):
                alpha = int(145 * (i / float(self.strip_h))**1.6)
                draw_base.line([(0, i), (self.width, i)], fill=(*sh_color, alpha))

        self.layout_type = preset.get("layout", {}).get("type", "classic_track")
        self.colors = preset.get("colors", {})

        if self.layout_type in ["classic_track", "ip_runner"]:
            c_unplayed = tuple(self.colors.get("track_unplayed", [255, 255, 255, 65]))
            rad = self.geo.get("radius", 4)
            for tr in self.geo["tracks"]:
                safe_draw_rect(draw_base, [tr["x1"], tr["y1"], tr["x2"], tr["y2"]], rad, c_unplayed)

        self.full_buf = bytearray(self.width * self.height * 4)
        self.full_mv = memoryview(self.full_buf)
        self.strip_offset = self.strip_y_start * self.width * 4
        self.strip_nbytes = self.strip_h * self.width * 4

    def render_frame_bytes(self, cur_time, total_duration):
        strip_img = self.base_strip.copy()
        draw = ImageDraw.Draw(strip_img)

        current_tr = self.geo["tracks"][0]
        for tr in self.geo["tracks"]:
            ch = tr["chapter"]
            if ch["start"] <= cur_time <= ch["end"]:
                current_tr = tr
                break

        # 经典轨道 / IP漫步绘制
        rad = self.geo.get("radius", 4)
        c_played = tuple(self.colors.get("track_played", [255, 195, 0, 240]))
        c_active_fill = tuple(self.colors.get("track_active_fill", [255, 195, 0, 255]))
        c_active_bg = tuple(self.colors.get("track_active_bg", [255, 255, 255, 90]))

        c_txt_active = tuple(self.colors.get("text_active", [255, 255, 255, 255]))
        c_txt_played = tuple(self.colors.get("text_played", [220, 220, 220, 180]))
        c_txt_unplayed = tuple(self.colors.get("text_unplayed", [160, 170, 180, 120]))

        for tr in self.geo["tracks"]:
            ch = tr["chapter"]
            x1, y1, x2, y2 = tr["x1"], tr["y1"], tr["x2"], tr["y2"]
            is_active = (tr == current_tr)
            is_past = (cur_time >= ch["end"])

            if is_past:
                safe_draw_rect(draw, [x1, y1, x2, y2], rad, c_played)
            elif is_active:
                pct = max(0.0, min(1.0, (cur_time - ch["start"]) / tr["dur"]))
                fill_w = tr["w"] * pct
                fill_right = min(x2, x1 + fill_w)
                safe_draw_rect(draw, [x1, y1, x2, y2], rad, c_active_bg)
                if fill_right > x1:
                    safe_draw_rect(draw, [x1, y1, fill_right, y2], rad, c_active_fill)

            if tr["w"] > 50:
                title = tr["display_title"]
                f = self.font_active if is_active else self.font_normal
                col = c_txt_active if is_active else (c_txt_played if is_past else c_txt_unplayed)
                draw.text((tr["tx"], tr["ty"]), title, font=f, fill=col)

        # 吉祥物渲染
        if self.mascot_img is not None:
            mw, mh = self.mascot_img.size
            first_tr = self.geo["tracks"][0]
            last_tr = self.geo["tracks"][-1]
            total_track_w = last_tr["x2"] - first_tr["x1"]
            cur_prog_x = first_tr["x1"] + total_track_w * (cur_time / max(0.001, total_duration))
            
            rail_top_y = first_tr["y1"]
            bounce = int(math.sin(cur_time * 6.0) * 2.0)
            mx = int(cur_prog_x - mw // 2)
            my = int(rail_top_y - mh + 2 + bounce)

            draw.ellipse([cur_prog_x - mw//3, rail_top_y - 2, cur_prog_x + mw//3, rail_top_y + 4], fill=(0, 0, 0, 160))
            strip_img.alpha_composite(self.mascot_img, (mx, my))

        self.full_mv[self.strip_offset : self.strip_offset + self.strip_nbytes] = strip_img.tobytes()
        return self.full_buf
