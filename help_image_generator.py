"""
🎨 帮助图片生成器

将帮助文本渲染到背景图片上，生成美观的帮助图片
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from astrbot.api import logger


class HelpImageGenerator:
    """
    📱 帮助图片生成器
    
    把枯燥的文字帮助变成漂亮的图片！
    """
    
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.bg_image_path = plugin_dir / "resources" / "img" / "img" / "1dacb975f586e6614f37575d80903292.jpg"
        self.output_path = plugin_dir / "output" / "help_image.png"
        
        # 字体路径
        self.font_path = plugin_dir / "resources" / "font" / "NotoSansCJK-Bold.ttc"
        if not self.font_path.exists():
            # 备用字体
            self.font_path = plugin_dir / "resources" / "font" / "SourceHanSansCN-Bold.otf"
    
    def generate_help_image(self, help_text: str) -> Path:
        """
        生成帮助图片
        
        Args:
            help_text: 帮助文本内容
            
        Returns:
            生成的图片路径
        """
        try:
            # 加载背景图片
            bg_image = Image.open(self.bg_image_path)
            
            # 调整图片大小（保持比例，最大宽度 1200）
            max_width = 1200
            ratio = max_width / bg_image.width
            new_height = int(bg_image.height * ratio)
            bg_image = bg_image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # 创建可绘制对象
            draw = ImageDraw.Draw(bg_image)
            
            # 加载字体
            try:
                title_font = ImageFont.truetype(str(self.font_path), 36)
                subtitle_font = ImageFont.truetype(str(self.font_path), 24)
                text_font = ImageFont.truetype(str(self.font_path), 18)
                small_font = ImageFont.truetype(str(self.font_path), 14)
            except Exception as e:
                logger.warning(f"加载字体失败，使用默认字体: {e}")
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # 在图片上添加半透明遮罩（提高文字可读性）
            overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, 160))
            bg_image = Image.alpha_composite(bg_image.convert('RGBA'), overlay)
            draw = ImageDraw.Draw(bg_image)
            
            # 解析帮助文本
            lines = help_text.split('\n')
            
            # 绘制参数
            x = 50
            y = 50
            line_height = 30
            
            for line in lines:
                if not line.strip():
                    y += line_height // 2
                    continue
                
                # 根据行内容选择字体和颜色
                if line.startswith('🎮'):
                    # 标题
                    draw.text((x, y), line, font=title_font, fill=(255, 255, 255, 255))
                    y += line_height + 10
                elif line.startswith('【') and line.endswith('】'):
                    # 分类标题
                    draw.text((x, y), line, font=subtitle_font, fill=(100, 200, 255, 255))
                    y += line_height + 5
                elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.')):
                    # 命令行
                    draw.text((x, y), line, font=text_font, fill=(255, 255, 150, 255))
                    y += line_height
                elif line.strip().startswith('💡') or line.strip().startswith('⚙️'):
                    # 提示信息
                    draw.text((x, y), line, font=small_font, fill=(200, 200, 200, 255))
                    y += line_height - 5
                elif line.strip().startswith('•'):
                    # 列表项
                    draw.text((x + 20, y), line, font=small_font, fill=(220, 220, 220, 255))
                    y += line_height - 5
                else:
                    # 普通文本
                    draw.text((x, y), line, font=small_font, fill=(240, 240, 240, 255))
                    y += line_height - 5
                
                # 如果超出图片高度，扩展图片
                if y > bg_image.height - 100:
                    # 扩展图片
                    new_image = Image.new('RGBA', (bg_image.width, bg_image.height + 500), (30, 30, 30, 255))
                    new_image.paste(bg_image, (0, 0))
                    bg_image = new_image
                    draw = ImageDraw.Draw(bg_image)
            
            # 裁剪空白区域
            bg_image = bg_image.crop((0, 0, bg_image.width, y + 50))
            
            # 保存图片
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            bg_image.convert('RGB').save(self.output_path, 'PNG', quality=95)
            
            logger.info(f"✅ 帮助图片已生成: {self.output_path}")
            return self.output_path
            
        except Exception as e:
            logger.error(f"❌ 生成帮助图片失败: {e}")
            raise


# 便捷函数
def generate_help_image(plugin_dir: Path, help_text: str) -> Path:
    """生成帮助图片的便捷函数"""
    generator = HelpImageGenerator(plugin_dir)
    return generator.generate_help_image(help_text)
