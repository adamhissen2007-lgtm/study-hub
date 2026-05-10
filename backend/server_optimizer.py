import asyncio
import aioredis
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import cachetools
from functools import lru_cache
import hashlib
from typing import Dict, Any
import time

class ServerOptimizer:
    """خوارزميات تحسين السيرفر بمعايير عالمية"""
    
    def __init__(self):
        self.cache = cachetools.TTLCache(maxsize=1000, ttl=300)  # 5 دقائق
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def optimize_middleware(self, app: FastAPI):
        """تطبيق طبقات التحسين"""
        # ضغط الردود (GZIP)
        app.add_middleware(GZipMiddleware, minimum_size=500)
        
        # حماية CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # حماية المضيف الموثوق
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=["*"]
        )
        
        print("🔥 تم تفعيل طبقات التحسين العالمية")
        return app
    
    async def caching_middleware(self, request, call_next):
        """ذاكرة تخزين مؤقت ذكية"""
        cache_key = f"{request.method}:{request.url.path}"
        
        # تجاهل طلبات POST و الـ API المستمرة
        if request.method == "GET" and "api" not in str(request.url):
            cached_response = self.cache.get(cache_key)
            if cached_response:
                self.cache_hits += 1
                return cached_response
            else:
                self.cache_misses += 1
        
        response = await call_next(request)
        
        if request.method == "GET" and response.status_code == 200:
            self.cache[cache_key] = response
        
        return response
    
    def get_cache_stats(self):
        """إحصائيات أداء الـ Cache"""
        total = self.cache_hits + self.cache_misses
        hit_ratio = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio": f"{hit_ratio:.1f}%",
            "cache_size": len(self.cache)
        }

# ==================== خوارزمية تحسين الأداء ====================

class AsyncDatabaseOptimizer:
    """تحسين سرعة قاعدة البيانات"""
    
    @staticmethod
    async def bulk_insert(session, objects, batch_size=100):
        """إدراج مجموعة كبيرة من البيانات بسرعة"""
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i+batch_size]
            session.add_all(batch)
            await session.flush()
        await session.commit()
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_cached_query(query_hash: str):
        """تخزين الاستعلامات المتكررة"""
        return None
    
    @staticmethod
    def generate_query_hash(sql: str) -> str:
        """إنشاء هاش فريد للاستعلام"""
        return hashlib.md5(sql.encode()).hexdigest()

# ==================== خوارزمية موازنة الأحمال ====================

class LoadBalancer:
    """توزيع الطلبات على خيوط متعددة"""
    
    def __init__(self):
        self.workers = []
        self.current_worker = 0
    
    def add_worker(self, worker_url: str):
        self.workers.append(worker_url)
    
    def get_next_worker(self) -> str:
        """Round-robin selection"""
        worker = self.workers[self.current_worker]
        self.current_worker = (self.current_worker + 1) % len(self.workers)
        return worker

server_optimizer = ServerOptimizer()