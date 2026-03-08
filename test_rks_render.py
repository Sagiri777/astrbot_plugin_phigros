#!/usr/bin/env python3
"""
测试 RKS 历史渲染功能
"""
import asyncio
import sys
from pathlib import Path

# 添加插件目录到路径
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

async def test_rks_history_rendering():
    """测试 RKS 历史渲染"""
    try:
        from phi_style_renderer import PhiStyleRenderer

        # 创建渲染器
        renderer = PhiStyleRenderer(
            plugin_dir=plugin_dir,
            cache_dir=plugin_dir / "cache",
            illustration_path=plugin_dir / "ILLUSTRATION"
        )

        await renderer.initialize()

        # 模拟测试数据（基于用户提供的测试数据）
        test_data = {
            "items": [
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-07T14:21:03.182949254+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-07T14:20:59.565017692+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-07T14:01:01.053852707+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-07T14:00:59.907945585+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-07T13:25:57.843174971+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-07T13:25:56.128084469+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-06T04:29:57.239122648+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-06T04:29:56.550483680+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-06T04:29:55.891798319+00:00"
                },
                {
                    "rks": 13.484260304021754,
                    "rksJump": -0.028458989798005874,
                    "createdAt": "2026-03-06T04:29:54.689534099+00:00"
                }
            ],
            "total": 194,
            "currentRks": 13.51271929381976,
            "peakRks": 13.51271929381976,
            "player_info": {
                "nickname": "TestPlayer",
                "player_id": "test123",
                "challenge_mode_rank": 5
            }
        }

        # 输出路径
        output_path = plugin_dir / "output" / "test_rks_history.png"

        print("🎨 开始测试 RKS 历史渲染...")
        print(f"📊 测试数据: {len(test_data['items'])} 条记录")
        print(f"👤 玩家信息: {test_data['player_info']}")
        print(f"💾 输出路径: {output_path}")

        # 调用渲染方法
        success = await renderer.render_rks_history(test_data, output_path)

        print(f"🎨 渲染结果: {'成功' if success else '失败'}")
        print(f"📁 文件存在: {output_path.exists()}")
        if output_path.exists():
            print(f"📏 文件大小: {output_path.stat().st_size} bytes")

        await renderer.terminate()

        return success

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_rks_history_rendering())
    sys.exit(0 if result else 1)