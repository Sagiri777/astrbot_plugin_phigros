#!/usr/bin/env python3
"""
测试插件初始化
"""
import asyncio
import sys
from pathlib import Path

# 模拟 AstrBot 环境
class MockContext:
    pass

class MockConfig:
    def get(self, key, default=None):
        configs = {
            'enable_renderer': True,
            'illustration_path': './ILLUSTRATION',
            'image_quality': 95,
            'default_search_limit': 5,
            'default_history_limit': 10
        }
        return configs.get(key, default)

async def test_plugin_initialization():
    try:
        print('🚀 测试插件初始化...')

        # 导入插件
        sys.path.insert(0, str(Path(__file__).parent))
        from main import PhigrosPlugin

        # 创建插件实例
        context = MockContext()
        config = MockConfig()

        plugin = PhigrosPlugin(context, config)

        print('🔧 enable_renderer:', plugin.enable_renderer)
        print('🔧 renderer 初始状态:', plugin.renderer)

        # 初始化插件
        await plugin.initialize()

        print('🔧 renderer 初始化后:', plugin.renderer)
        if plugin.renderer:
            print('🔧 renderer 类型:', type(plugin.renderer))
            print('🔧 有 render_rks_history 方法:', hasattr(plugin.renderer, 'render_rks_history'))
        else:
            print('🔧 renderer 为 None')

        # 终止插件
        await plugin.terminate()

        return plugin.renderer is not None

    except Exception as e:
        print('❌ 初始化失败:', e)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_plugin_initialization())
    print('🎯 测试结果:', '成功' if result else '失败')