# -*- coding: utf-8 -*-
"""StellarCanvas —— 星绘，生图执行器 v1.0.0

星缀的生图挂载点，接口兼容 Amo_Image 的 draw_for() 和 quota()。
支持 NAI / OpenAI / 任意 t2i 后端。
"""
from __future__ import annotations
from typing import Any, Dict, Optional
try:
    from astrbot.api import logger
    from astrbot.api.event import AstrMessageEvent
    from astrbot.api.star import Context, Star
except ImportError:
    raise

PLUGIN_VERSION = "1.0.1"


class StellarCanvas(Star):
    def __init__(self, context: Context, config: Dict[str, Any] | None = None) -> None:
        super().__init__(context)
        cfg = config or {}
        self._enabled: bool = bool(cfg.get("enable", True))
        self._backend: str = str(cfg.get("backend", "nai"))   # nai / openai / sd
        self._api_key: str = str(cfg.get("api_key") or "")
        self._api_base: str = str(cfg.get("api_base") or "")
        self._daily_limit: int = int(cfg.get("daily_limit") or 0)   # 0=不限
        self._daily_used: Dict[str, int] = {}   # uid -> count
        logger.info(f"[StellarCanvas] v{PLUGIN_VERSION} 初始化，后端={self._backend}")

    async def draw_for(
        self,
        umo: str,
        uid: str = "",
        prompt: str = "",
        selfie: bool | None = None,
        place: str = "",
        activity: str = "",
        zone: str = "",
        **kwargs,
    ) -> bytes | None:
        """公开接口：供星缀大脑调用的出图接口。

        失败一律返回 None，不抛异常。
        """
        if not self._enabled:
            return None
        if not prompt:
            return None

        # 配额检查
        if self._daily_limit > 0:
            used = self._daily_used.get(str(uid or umo), 0)
            if used >= self._daily_limit:
                logger.info(f"[StellarCanvas] {uid} 今日配额已用完（{used}/{self._daily_limit}）")
                return None

        try:
            img_bytes = await self._do_draw(prompt)
            if img_bytes:
                self._daily_used[str(uid or umo)] = (
                    self._daily_used.get(str(uid or umo), 0) + 1
                )
            return img_bytes
        except Exception as e:
            logger.warning(f"[StellarCanvas] 出图失败: {e}")
            return None

    def quota(self, uid: str = "", umo: str = "", group: bool = False) -> Dict:
        """配额查询接口（兼容 Amo_Image）。"""
        limit = self._daily_limit
        used = self._daily_used.get(str(uid or umo), 0)
        return {
            "allowed": limit == 0 or used < limit,
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used) if limit > 0 else -1,
        }

    async def _do_draw(self, prompt: str) -> bytes | None:
        """实际绘图（根据 backend 路由）。"""
        if self._backend == "nai":
            return await self._nai_draw(prompt)
        elif self._backend == "openai":
            return await self._openai_draw(prompt)
        else:
            logger.warning(f"[StellarCanvas] 不支持的后端：{self._backend}")
            return None

    async def _nai_draw(self, prompt: str) -> bytes | None:
        """NAI v3 生图。"""
        import aiohttp
        base = self._api_base or "https://image.novelai.net"
        payload = {
            "input": prompt,
            "model": "nai-diffusion-3",
            "action": "generate",
            "parameters": {
                "width": 832, "height": 1216,
                "scale": 5.0, "sampler": "k_euler",
                "steps": 28, "n_samples": 1,
                "strength": 0.7, "noise": 0.0,
            }
        }
        headers = {"Authorization": f"Bearer {self._api_key}",
                   "Content-Type": "application/json"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base}/ai/generate-image",
                    json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.warning(f"[StellarCanvas] NAI 返回 {resp.status}: {body[:100]}")
                        return None
                    data = await resp.json()
                    import base64
                    for img_data in data.get("images") or []:
                        return base64.b64decode(img_data)
        except Exception as e:
            logger.warning(f"[StellarCanvas] NAI 请求失败: {e}")
        return None

    async def _openai_draw(self, prompt: str) -> bytes | None:
        """OpenAI images.generate。"""
        import aiohttp
        base = self._api_base or "https://api.openai.com/v1"
        payload = {"model": "dall-e-3", "prompt": prompt[:4000],
                   "n": 1, "size": "1024x1024", "response_format": "b64_json"}
        headers = {"Authorization": f"Bearer {self._api_key}",
                   "Content-Type": "application/json"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base}/images/generations",
                    json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=90),
                ) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    import base64
                    for item in (data.get("data") or []):
                        b64 = item.get("b64_json") or ""
                        if b64:
                            return base64.b64decode(b64)
        except Exception as e:
            logger.warning(f"[StellarCanvas] OpenAI draw 请求失败: {e}")
        return None
