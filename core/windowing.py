"""窗宽窗位调整。

窗宽（Window Width, WW）决定显示的 HU 值范围，窗位（Window Level/Center, WL）
决定该范围的中间值。将 [WL - WW/2, WL + WW/2] 线性映射到 [0, 255] 灰度。
"""

from __future__ import annotations

import numpy as np


def apply_window(hu: np.ndarray, ww: float, wl: float, invert: bool = False) -> np.ndarray:
    """将 HU 图像按窗宽窗位映射为 8 位灰度图。

    Args:
        hu: HU 值矩阵。
        ww: 窗宽，必须为正（内部会钳制到 >= 1）。
        wl: 窗位。
        invert: 是否反色（黑白翻转）。

    Returns:
        uint8 灰度图像。
    """
    ww = max(float(ww), 1.0)  # 防止除零
    low = wl - ww / 2.0
    high = wl + ww / 2.0

    normalized = (hu - low) / (high - low)
    normalized = np.clip(normalized, 0.0, 1.0)

    gray = (normalized * 255.0).astype(np.uint8)
    if invert:
        gray = 255 - gray
    return gray
