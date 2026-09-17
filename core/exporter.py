"""图像导出。"""

from __future__ import annotations

import io

import numpy as np
from PIL import Image


def encode_png(rgb: np.ndarray) -> bytes:
    """将 RGB 图像编码为 PNG 字节流（供 Streamlit 下载）。"""
    if rgb.dtype != np.uint8:
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    if rgb.ndim == 2:
        img = Image.fromarray(rgb).convert("RGB")
    else:
        img = Image.fromarray(np.ascontiguousarray(rgb))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def save_png(rgb: np.ndarray, path: str) -> None:
    """将 RGB 图像保存为 PNG 文件。"""
    data = encode_png(rgb)
    with open(path, "wb") as f:
        f.write(data)
