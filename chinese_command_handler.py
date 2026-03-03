"""
🇨🇳 中文命令处理器

核心功能：
1. 中文命令识别与映射
2. 自然语言理解
3. 命令智能纠错
4. 中文友好的错误提示
"""

import re
import difflib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from astrbot.api import logger


@dataclass
class CommandMapping:
    """命令映射数据类"""
    chinese_names: List[str]  # 中文命令名列表
    english_name: str         # 英文命令名
    description: str          # 命令描述
    examples: List[str]       # 使用示例
    aliases: List[str]        # 别名


class ChineseCommandHandler:
    """
    🎯 中文命令处理器
    
    让你的指令更接地气，支持中文自然语言输入！
    """
    
    # 命令映射表
    COMMAND_MAPPINGS: Dict[str, CommandMapping] = {
        "phi_bind": CommandMapping(
            chinese_names=["绑定", "绑定账号", "账号绑定", "登录", "登陆"],
            english_name="phi_bind",
            description="绑定 Phigros 账号",
            examples=["绑定 xxxxxx", "绑定账号 xxxxxx cn"],
            aliases=["bind", "login"]
        ),
        "phi_qrlogin": CommandMapping(
            chinese_names=["扫码登录", "二维码登录", "扫码", "qr登录"],
            english_name="phi_qrlogin",
            description="使用二维码扫码登录",
            examples=["扫码登录", "扫码登录 cn"],
            aliases=["qrlogin", "qr"]
        ),
        "phi_unbind": CommandMapping(
            chinese_names=["解绑", "解绑账号", "取消绑定", "退出登录", "注销"],
            english_name="phi_unbind",
            description="解绑当前账号",
            examples=["解绑", "取消绑定"],
            aliases=["unbind", "logout"]
        ),
        "phi_save": CommandMapping(
            chinese_names=["存档", "查询存档", "我的存档", "个人信息", "资料"],
            english_name="phi_save",
            description="查询个人游戏存档",
            examples=["存档", "查询存档"],
            aliases=["save", "profile"]
        ),
        "phi_b30": CommandMapping(
            chinese_names=["b30", "best30", "成绩图", "best30成绩", "b30图"],
            english_name="phi_b30",
            description="生成 Best30 成绩图",
            examples=["b30", "b30 cn", "best30 black"],
            aliases=["best30", "b30图"]
        ),
        "phi_bn": CommandMapping(
            chinese_names=["bn", "bestn", "自定义成绩", "bn图"],
            english_name="phi_bn",
            description="生成 BestN 成绩图",
            examples=["bn 27", "bn 50 black"],
            aliases=["bestn"]
        ),
        "phi_rks_history": CommandMapping(
            chinese_names=["rks历史", "历史记录", "rks变化", "rks趋势"],
            english_name="phi_rks_history",
            description="查询 RKS 历史变化",
            examples=["rks历史", "rks历史 10"],
            aliases=["rkshistory", "history"]
        ),
        "phi_leaderboard": CommandMapping(
            chinese_names=["排行榜", "榜单", "排名", "大神榜"],
            english_name="phi_leaderboard",
            description="查看全服排行榜",
            examples=["排行榜", "榜单"],
            aliases=["leaderboard", "ranking"]
        ),
        "phi_rank": CommandMapping(
            chinese_names=["查排名", "排名查询", "名次"],
            english_name="phi_rank",
            description="按排名区间查询",
            examples=["查排名 1 10", "排名 100"],
            aliases=["rank"]
        ),
        "phi_search": CommandMapping(
            chinese_names=["搜索", "搜歌", "找歌", "查歌"],
            english_name="phi_search",
            description="搜索歌曲",
            examples=["搜索 Glaciaxion", "搜歌 冬雪"],
            aliases=["search", "find"]
        ),
        "phi_song": CommandMapping(
            chinese_names=["单曲", "歌曲成绩", "查单曲", "歌曲信息"],
            english_name="phi_song",
            description="查询单曲成绩",
            examples=["单曲 曲名", "歌曲成绩 曲名.曲师"],
            aliases=["song", "track"]
        ),
        "phi_updates": CommandMapping(
            chinese_names=["新曲", "更新", "新曲速递", "最新歌曲"],
            english_name="phi_updates",
            description="获取最新更新歌曲",
            examples=["新曲", "新曲 5"],
            aliases=["updates", "new"]
        ),
        "phi_help": CommandMapping(
            chinese_names=["帮助", "指令", "命令", "怎么用", "教程"],
            english_name="phi_help",
            description="显示帮助信息",
            examples=["帮助", "指令"],
            aliases=["help", "?"]
        ),
    }
    
    # 自然语言模式匹配
    NATURAL_LANGUAGE_PATTERNS = [
        # 绑定相关
        (r"(?:帮我?)?(?:绑定|登录|登陆)(?:一下)?(?:账号)?[:：]?\s*(\S+)", "phi_bind"),
        (r"(?:我想)?(?:绑定|登录)(?:我的)?(?:账号)?[:：]?\s*(\S+)", "phi_bind"),
        
        # 扫码登录
        (r"(?:我要)?扫码(?:登录)?(?:一下)?", "phi_qrlogin"),
        (r"(?:用)?二维码(?:登录)?", "phi_qrlogin"),
        
        # 查询存档
        (r"(?:查看?|查询)?(?:我的)?(?:存档|资料|信息)(?:呢)?", "phi_save"),
        (r"(?:我)?(?:的)?(?:存档|资料)(?:在哪里|在哪|呢)?", "phi_save"),
        
        # B30
        (r"(?:查看?)?(?:我的)?b30(?:成绩)?(?:图)?(?:呢)?", "phi_b30"),
        (r"(?:我的)?best30(?:呢)?", "phi_b30"),
        (r"(?:查看?)?(?:我的)?成绩图", "phi_b30"),
        
        # 排行榜
        (r"(?:查看?)?排行榜(?:呢)?", "phi_leaderboard"),
        (r"(?:看看)?大神榜", "phi_leaderboard"),
        
        # 搜索
        (r"(?:帮我?)?搜索(?:一下)?[:：]?\s*(.+)", "phi_search"),
        (r"(?:帮我?)?找(?:一下)?(?:这首歌)?[:：]?\s*(.+)", "phi_search"),
        
        # 帮助
        (r"(?:这个)?(?:怎么|如何)(?:使用)?(?:啊|呀|呢)?", "phi_help"),
        (r"(?:有)?什么(?:指令|命令)(?:啊|呀|呢)?", "phi_help"),
        (r"(?:我)?不会用(?:啊|呀)", "phi_help"),
    ]
    
    def __init__(self):
        """初始化处理器"""
        # 构建反向映射（中文名 -> 英文名）
        self.chinese_to_english: Dict[str, str] = {}
        self.all_chinese_names: List[str] = []
        
        for cmd_name, mapping in self.COMMAND_MAPPINGS.items():
            # 添加中文名映射
            for cn_name in mapping.chinese_names:
                self.chinese_to_english[cn_name] = cmd_name
                self.all_chinese_names.append(cn_name)
            # 添加别名映射
            for alias in mapping.aliases:
                self.chinese_to_english[alias] = cmd_name
    
    def recognize_command(self, user_input: str) -> Tuple[Optional[str], float, str]:
        """
        🎯 识别用户输入的命令
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            (命令名, 置信度, 识别方式)
            命令名为 None 表示未识别
        """
        user_input = user_input.strip()
        
        # 1. 精确匹配英文命令
        if user_input.startswith("phi_"):
            cmd = user_input.split()[0]
            if cmd in self.COMMAND_MAPPINGS:
                return cmd, 1.0, "exact_english"
        
        # 2. 精确匹配中文命令
        if user_input in self.chinese_to_english:
            return self.chinese_to_english[user_input], 1.0, "exact_chinese"
        
        # 3. 自然语言匹配
        for pattern, cmd in self.NATURAL_LANGUAGE_PATTERNS:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return cmd, 0.95, "natural_language"
        
        # 4. 模糊匹配（容错）
        best_match = self._fuzzy_match(user_input)
        if best_match and best_match[1] >= 0.8:
            return best_match[0], best_match[1], "fuzzy_match"
        
        # 5. 提取可能的命令关键词
        keyword_match = self._extract_command_keyword(user_input)
        if keyword_match:
            return keyword_match[0], keyword_match[1], "keyword_extract"
        
        return None, 0.0, "not_recognized"
    
    def _fuzzy_match(self, user_input: str) -> Optional[Tuple[str, float]]:
        """
        🔍 模糊匹配命令
        """
        # 与所有中文命令名进行模糊匹配
        matches = difflib.get_close_matches(
            user_input, 
            self.all_chinese_names, 
            n=1, 
            cutoff=0.6
        )
        
        if matches:
            matched_name = matches[0]
            similarity = difflib.SequenceMatcher(None, user_input, matched_name).ratio()
            english_cmd = self.chinese_to_english.get(matched_name)
            if english_cmd:
                return (english_cmd, similarity)
        
        return None
    
    def _extract_command_keyword(self, user_input: str) -> Optional[Tuple[str, float]]:
        """
        🔎 从输入中提取命令关键词
        """
        # 常见关键词映射
        keywords = {
            "绑定": "phi_bind",
            "扫码": "phi_qrlogin",
            "解绑": "phi_unbind",
            "存档": "phi_save",
            "b30": "phi_b30",
            "best30": "phi_b30",
            "bn": "phi_bn",
            "rks": "phi_rks_history",
            "排行": "phi_leaderboard",
            "排名": "phi_rank",
            "搜索": "phi_search",
            "搜": "phi_search",
            "单曲": "phi_song",
            "新曲": "phi_updates",
            "帮助": "phi_help",
        }
        
        for keyword, cmd in keywords.items():
            if keyword in user_input.lower():
                return (cmd, 0.7)
        
        return None
    
    def get_suggestion(self, user_input: str) -> Optional[str]:
        """
        💡 获取命令建议（当识别失败时）
        """
        # 找到最相似的命令
        matches = difflib.get_close_matches(
            user_input,
            self.all_chinese_names,
            n=3,
            cutoff=0.4
        )
        
        if matches:
            suggestions = []
            for match in matches:
                cmd = self.chinese_to_english.get(match)
                if cmd:
                    mapping = self.COMMAND_MAPPINGS.get(cmd)
                    if mapping:
                        suggestions.append(f"「{match}」({mapping.description})")
            
            if suggestions:
                return "、".join(suggestions)
        
        return None
    
    def parse_parameters(self, user_input: str, command: str) -> Dict[str, Any]:
        """
        📦 解析命令参数
        
        支持自然语言参数提取
        """
        params = {}
        
        # 提取 token（绑定命令）
        if command == "phi_bind":
            # 匹配各种格式的 token
            token_patterns = [
                r"(?:token|令牌)[:：]?\s*(\S+)",
                r"(?:绑定|登录)[:：]?\s*(\S+)",
                r"\b([a-zA-Z0-9_-]{20,})\b",  # 长字符串可能是 token
            ]
            for pattern in token_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    params["session_token"] = match.group(1)
                    break
            
            # 提取版本
            if "国际" in user_input or "global" in user_input.lower():
                params["taptap_version"] = "global"
            elif "国服" in user_input or "cn" in user_input.lower():
                params["taptap_version"] = "cn"
        
        # 提取数量（BN 命令）
        elif command == "phi_bn":
            number_match = re.search(r"(\d+)", user_input)
            if number_match:
                params["n"] = int(number_match.group(1))
            
            # 提取主题
            if "白" in user_input or "white" in user_input.lower():
                params["theme"] = "white"
            elif "黑" in user_input or "black" in user_input.lower():
                params["theme"] = "black"
        
        # 提取搜索关键词
        elif command == "phi_search":
            # 去除命令词，保留搜索内容
            for cmd_word in ["搜索", "搜歌", "找歌", "查歌", "search"]:
                if cmd_word in user_input:
                    keyword = user_input.split(cmd_word, 1)[-1].strip()
                    if keyword:
                        params["keyword"] = keyword
                        break
        
        # 提取歌曲名
        elif command == "phi_song":
            for cmd_word in ["单曲", "歌曲", "song"]:
                if cmd_word in user_input:
                    song_name = user_input.split(cmd_word, 1)[-1].strip()
                    if song_name:
                        params["song_id"] = song_name
                        break
        
        return params
    
    def get_error_message(self, error_type: str, details: str = "") -> str:
        """
        ❌ 获取中文友好的错误提示
        """
        error_messages = {
            "command_not_found": f"❌ 我没听懂你在说什么...\n\n💡 试试输入「帮助」查看所有指令吧！",
            "token_invalid": f"❌ 你的登录凭证好像不对哦~\n\n💡 解决方法：\n1. 重新扫码登录：发送「扫码登录」\n2. 或者访问 https://lilith.xtower.site/ 获取新的 token",
            "network_error": f"❌ 网络开小差了，连接不上服务器...\n\n💡 请检查：\n1. 网络连接是否正常\n2. 稍后再试\n\n错误详情：{details}",
            "api_error": f"❌ 服务器好像出了点问题...\n\n💡 可能原因：\n1. API 服务暂时不可用\n2. 请求太频繁了，请稍后再试\n\n错误详情：{details}",
            "not_bound": f"❌ 你还没有绑定账号呢！\n\n💡 解决方法：\n1. 扫码登录（推荐）：发送「扫码登录」\n2. 手动绑定：发送「绑定 你的token」",
            "song_not_found": f"❌ 找不到这首歌呢...\n\n💡 试试：\n1. 检查歌曲名是否拼写正确\n2. 使用「搜索」功能查找歌曲\n3. 查看曲绘文件夹中是否有这首歌的图片",
            "render_failed": f"❌ 图片生成失败了...\n\n💡 可能原因：\n1. 缺少必要的字体文件\n2. 内存不足\n3. 图片资源缺失\n\n错误详情：{details}",
            "timeout": f"⏱️ 操作超时了，请稍后再试~\n\n💡 建议：\n1. 检查网络连接\n2. 如果是查询大量数据，可以分批查询",
            "unknown": f"❌ 哎呀，出错了！\n\n错误详情：{details}\n\n💡 如果问题持续存在，请联系插件开发者~",
        }
        
        return error_messages.get(error_type, error_messages["unknown"])
    
    def get_command_help(self, command: str) -> Optional[str]:
        """
        📖 获取命令的详细帮助
        """
        mapping = self.COMMAND_MAPPINGS.get(command)
        if not mapping:
            return None
        
        help_text = f"""
📋 「{mapping.chinese_names[0]}」使用帮助

📝 功能：{mapping.description}

🔤 可用指令：
{chr(10).join([f"  • {name}" for name in mapping.chinese_names[:3]])}

💡 使用示例：
{chr(10).join([f"  {i+1}. {example}" for i, example in enumerate(mapping.examples)])}

🎯 快捷方式：
{chr(10).join([f"  • {alias}" for alias in mapping.aliases])}
"""
        return help_text.strip()


# 创建全局处理器实例
chinese_handler = ChineseCommandHandler()


def recognize_chinese_command(user_input: str) -> Tuple[Optional[str], float, str, Optional[Dict[str, Any]]]:
    """
    🎯 识别中文命令的便捷函数
    
    Returns:
        (命令名, 置信度, 识别方式, 解析的参数)
    """
    command, confidence, method = chinese_handler.recognize_command(user_input)
    
    # 解析参数
    params = {}
    if command:
        params = chinese_handler.parse_parameters(user_input, command)
    
    return command, confidence, method, params


def get_chinese_error_message(error_type: str, details: str = "") -> str:
    """
    ❌ 获取中文错误消息的便捷函数
    """
    return chinese_handler.get_error_message(error_type, details)


def get_command_suggestion(user_input: str) -> Optional[str]:
    """
    💡 获取命令建议的便捷函数
    """
    return chinese_handler.get_suggestion(user_input)
