#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成应用图标
创建一个体现"品牌检查"概念的图标
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("需要安装Pillow库: pip install Pillow")
    exit(1)


def create_icon():
    """创建应用图标 - 品牌检查主题"""
    # 创建不同尺寸的图标（Windows需要多种尺寸）
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # 创建图像（RGBA模式支持透明）
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 计算缩放比例
        scale = size / 256.0
        
        # 绘制背景圆形（现代紫色渐变）
        margin = int(8 * scale)
        bg_rect = [margin, margin, size - margin, size - margin]
        # 主背景色：现代紫色（品牌/检查主题）
        draw.ellipse(bg_rect, fill=(155, 89, 182, 255))
        
        # 添加内圈高光效果
        highlight_margin = int(20 * scale)
        highlight_rect = [highlight_margin, highlight_margin, 
                          size - highlight_margin, size - highlight_margin]
        draw.ellipse(highlight_rect, fill=(209, 196, 233, 100))
        
        # 绘制图片图标（左侧，白色相框）
        image_width = int(90 * scale)
        image_height = int(110 * scale)
        image_x = int(size * 0.2)
        image_y = int(size * 0.25)
        
        # 图片外框
        image_rect = [image_x, image_y, image_x + image_width, image_y + image_height]
        draw.rectangle(image_rect, fill=(255, 255, 255, 255), outline=(200, 200, 200, 255), width=int(3 * scale))
        
        # 图片内部内容（模拟图片）
        inner_margin = int(8 * scale)
        inner_rect = [image_x + inner_margin, image_y + inner_margin,
                     image_x + image_width - inner_margin, image_y + image_height - inner_margin]
        draw.rectangle(inner_rect, fill=(240, 240, 240, 255))
        
        # 图片内部装饰线条（模拟图片内容）
        for i in range(2):
            line_y = image_y + inner_margin + int((i + 1) * 25 * scale)
            line_width = int(50 * scale)
            draw.rectangle(
                [image_x + int(20 * scale), line_y,
                 image_x + int(20 * scale) + line_width, line_y + int(5 * scale)],
                fill=(220, 220, 220, 255)
            )
        
        # 绘制品牌标签/徽章（右侧上方，表示品牌检查）
        badge_x = int(size * 0.55)
        badge_y = int(size * 0.2)
        badge_size = int(70 * scale)
        
        # 品牌徽章背景（圆形）
        badge_rect = [badge_x, badge_y, badge_x + badge_size, badge_y + badge_size]
        draw.ellipse(badge_rect, fill=(255, 255, 255, 255))
        
        # 品牌徽章内部（字母B表示Brand）
        font_size = int(40 * scale)
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
            except:
                # 使用默认字体
                font = ImageFont.load_default()
        
        # 绘制字母B
        text = "B"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = badge_x + (badge_size - text_width) // 2
        text_y = badge_y + (badge_size - text_height) // 2
        draw.text((text_x, text_y), text, fill=(155, 89, 182, 255), font=font)
        
        # 绘制检查标记（对勾，表示验证通过）
        check_x = int(size * 0.7)
        check_y = int(size * 0.55)
        check_size = int(50 * scale)
        
        # 对勾线条（绿色）
        check_thickness = int(8 * scale)
        # 对勾的第一段（左下到中间）
        check_start_x = check_x
        check_start_y = check_y + check_size // 2
        check_mid_x = check_x + check_size // 3
        check_mid_y = check_y + check_size // 3
        # 对勾的第二段（中间到右上）
        check_end_x = check_x + check_size
        check_end_y = check_y
        
        draw.line(
            [check_start_x, check_start_y, check_mid_x, check_mid_y],
            fill=(46, 204, 113, 255), width=check_thickness
        )
        draw.line(
            [check_mid_x, check_mid_y, check_end_x, check_end_y],
            fill=(46, 204, 113, 255), width=check_thickness
        )
        
        # 绘制连接线（从图片到检查标记，表示处理流程）
        arrow_start_x = image_x + image_width + int(5 * scale)
        arrow_start_y = image_y + image_height // 2
        arrow_end_x = check_x - int(5 * scale)
        arrow_end_y = check_y + check_size // 2
        
        # 箭头线
        arrow_thickness = int(5 * scale)
        draw.line(
            [arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y],
            fill=(255, 255, 255, 200), width=arrow_thickness
        )
        
        # 箭头头部
        arrow_head_size = int(10 * scale)
        arrow_points = [
            (arrow_end_x, arrow_end_y),
            (arrow_end_x - arrow_head_size, arrow_end_y - arrow_head_size // 2),
            (arrow_end_x - arrow_head_size, arrow_end_y + arrow_head_size // 2),
        ]
        draw.polygon(arrow_points, fill=(255, 255, 255, 200))
        
        images.append(img)
    
    # 保存为ICO格式（包含所有尺寸）
    images[0].save(
        'icon.ico',
        format='ICO',
        sizes=[(img.size[0], img.size[1]) for img in images]
    )
    
    # 同时保存为PNG格式（用于预览）
    images[-1].save('icon.png', format='PNG')
    
    print("图标生成成功！")
    print("- icon.ico (Windows图标，包含多种尺寸)")
    print("- icon.png (预览图，256x256)")


if __name__ == "__main__":
    create_icon()

