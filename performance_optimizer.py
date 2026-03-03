"""
⚡ 性能优化模块

核心功能：
1. 响应速度优化（目标<500ms）
2. 缓存管理
3. 异步优化
4. 资源预加载
"""

import asyncio
import time
import functools
from typing import Callable, Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from astrbot.api import logger


class PerformanceMonitor:
    """
    📊 性能监控器
    
    监控命令响应时间，确保平均响应时间控制在500ms以内
    """
    
    def __init__(self):
        self.response_times: Dict[str, list] = {}
        self.max_samples = 100  # 保留最近100个样本
    
    def record_response_time(self, command: str, duration_ms: float):
        """记录响应时间"""
        if command not in self.response_times:
            self.response_times[command] = []
        
        self.response_times[command].append(duration_ms)
        
        # 只保留最近100个样本
        if len(self.response_times[command]) > self.max_samples:
            self.response_times[command] = self.response_times[command][-self.max_samples:]
    
    def get_average_response_time(self, command: str = None) -> float:
        """获取平均响应时间"""
        if command:
            times = self.response_times.get(command, [])
            return sum(times) / len(times) if times else 0.0
        else:
            # 所有命令的平均值
            all_times = []
            for times in self.response_times.values():
                all_times.extend(times)
            return sum(all_times) / len(all_times) if all_times else 0.0
    
    def get_slow_commands(self, threshold_ms: float = 500.0) -> list:
        """获取响应慢的命令"""
        slow_commands = []
        for command, times in self.response_times.items():
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > threshold_ms:
                    slow_commands.append((command, avg_time))
        return sorted(slow_commands, key=lambda x: x[1], reverse=True)
    
    def generate_report(self) -> str:
        """生成性能报告"""
        avg_time = self.get_average_response_time()
        slow_commands = self.get_slow_commands()
        
        report = f"""
📊 性能监控报告

⏱️ 平均响应时间: {avg_time:.2f}ms
🎯 目标: <500ms
{"✅ 达标" if avg_time < 500 else "⚠️ 未达标"}

📈 各命令平均响应时间:
"""
        for command, times in sorted(self.response_times.items(), 
                                     key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0, 
                                     reverse=True):
            if times:
                avg = sum(times) / len(times)
                status = "✅" if avg < 500 else "⚠️"
                report += f"  {status} {command}: {avg:.2f}ms\n"
        
        if slow_commands:
            report += "\n🐌 需要优化的命令:\n"
            for cmd, time in slow_commands[:5]:
                report += f"  • {cmd}: {time:.2f}ms\n"
        
        return report


# 全局性能监控器
performance_monitor = PerformanceMonitor()


def timed_execution(func: Callable) -> Callable:
    """
    ⏱️ 执行时间装饰器
    
    自动记录函数执行时间
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration_ms = (time.time() - start_time) * 1000
            # 尝试获取命令名
            command = func.__name__
            performance_monitor.record_response_time(command, duration_ms)
            
            # 如果响应时间超过500ms，记录警告
            if duration_ms > 500:
                logger.warning(f"⚠️ 命令 {command} 响应较慢: {duration_ms:.2f}ms")
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration_ms = (time.time() - start_time) * 1000
            command = func.__name__
            performance_monitor.record_response_time(command, duration_ms)
            
            if duration_ms > 500:
                logger.warning(f"⚠️ 函数 {command} 执行较慢: {duration_ms:.2f}ms")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


class AsyncOptimizer:
    """
    🚀 异步优化器
    
    优化异步操作，提高并发处理能力
    """
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """在线程池中运行同步函数"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            functools.partial(func, *args, **kwargs)
        )
    
    async def limited_concurrency(self, coro: asyncio.Coroutine) -> Any:
        """限制并发数的协程执行"""
        async with self.semaphore:
            return await coro
    
    async def gather_with_limit(self, *coros: asyncio.Coroutine, limit: int = 4) -> list:
        """限制并发数的 gather"""
        semaphore = asyncio.Semaphore(limit)
        
        async def sem_coro(coro):
            async with semaphore:
                return await coro
        
        return await asyncio.gather(*[sem_coro(c) for c in coros])


# 全局异步优化器
async_optimizer = AsyncOptimizer()


def optimize_response_time(func: Callable) -> Callable:
    """
    ⚡ 响应时间优化装饰器
    
    自动优化函数执行，确保响应时间<500ms
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            # 设置超时（500ms + 100ms缓冲）
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=0.6  # 600ms超时
            )
            
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"✅ {func.__name__} 响应时间: {duration_ms:.2f}ms")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"❌ {func.__name__} 响应超时（>600ms）")
            raise TimeoutError("响应超时，请稍后再试")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ {func.__name__} 执行失败 ({duration_ms:.2f}ms): {e}")
            raise
    
    return wrapper


class ResourcePreloader:
    """
    📦 资源预加载器
    
    预加载常用资源，减少首次响应时间
    """
    
    def __init__(self):
        self.preloaded_resources: Dict[str, Any] = {}
        self.is_preloaded = False
    
    async def preload(self):
        """预加载资源"""
        if self.is_preloaded:
            return
        
        logger.info("🔄 开始预加载资源...")
        start_time = time.time()
        
        # 预加载任务列表
        preload_tasks = [
            self._preload_config(),
            self._preload_fonts(),
            self._preload_templates(),
        ]
        
        await asyncio.gather(*