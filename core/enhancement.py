"""图像增强：CLAHE、伽马校正、锐化与伪彩色映射。"""

from __future__ import annotations

import cv2
import numpy as np


# 颜色映射名称 -> OpenCV colormap 常量
_COLORMAP_MAP: dict[str, int] = {
    "jet": cv2.COLORMAP_JET,
    "hot": cv2.COLORMAP_HOT,
    "bone": cv2.COLORMAP_BONE,
    "inferno": cv2.COLORMAP_INFERNO,
    "viridis": cv2.COLORMAP_VIRIDIS,
}


def clahe(gray: np.ndarray, clip_limit: float = 2.0, tile_grid_size: int = 8) -> np.ndarray:
    """CLAHE 对比度受限自适应直方图均衡。

    相比全局直方图均衡，CLAHE 对局部对比度的提升更温和，
    更适合医学影像中细节的增强。
    """
    clip_limit = max(float(clip_limit), 0.0)
    tile_grid_size = max(int(tile_grid_size), 1)
    clahe_obj = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
    return clahe_obj.apply(gray)


def gamma_correct(gray: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """伽马校正。

    gamma > 1 图像变暗，gamma < 1 图像变亮。使用查找表（LUT）加速。
    """
    gamma = max(float(gamma), 1e-3)
    lut = np.clip((np.arange(256) / 255.0) ** (1.0 / gamma) * 255.0, 0, 255).astype(np.uint8)
    return cv2.LUT(gray, lut)


def sharpen(gray: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """基于高斯模糊的反锐化掩模（Unsharp Masking）锐化。

    result = gray * (1 + strength) - blur * strength
    """
    strength = max(float(strength), 0.0)
    if strength == 0.0:
        return gray
    blur = cv2.GaussianBlur(gray, (0, 0), sigmaX=3.0)
    result = cv2.addWeighted(gray, 1.0 + strength, blur, -strength, 0)
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_colormap(gray: np.ndarray, name: str) -> np.ndarray:
    """应用伪彩色映射。

    Args:
        gray: uint8 灰度图。
        name: 颜色映射名称（"gray" 表示保持灰度）。

    Returns:
        RGB 图像（H, W, 3）。
    """
    if name == "gray":
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cmap = _COLORMAP_MAP.get(name, cv2.COLORMAP_JET)
    return cv2.applyColorMap(gray, cmap)
