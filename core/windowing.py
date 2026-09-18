"""窗宽窗位调整。

窗宽（Window Width, WW）决定显示的 HU 值范围，窗位（Window Level/Center, WL）
决定该范围的中间值。将 [WL - WW/2, WL + WW/2] 线性映射到 [0, 255] 灰度。
"""

from __future__ import annotations

import numpy as np


def apply_window(hu: np.ndarray, ww: float, wl: float, invert: bool = False) -> np.ndarray:
    """将 DICOM 原始 HU 值按窗宽窗位线性映射为 8 位灰度图。

    功能：
        CT 的 HU 值动态范围可达 [-1024, 3071]，远超显示器 256 级灰度。
        窗宽窗位（Windowing）从中截取医生关心的 HU 子区间，线性拉伸到
        [0, 255]，从而突出特定组织的对比度。

    数学公式：
        low  = WL - WW / 2                             # 窗口下限
        high = WL + WW / 2                             # 窗口上限
        gray = clip((HU - low) / (high - low), 0, 1) * 255   # 灰度输出

        即：HU 先平移使窗下限归零，再除以窗宽归一化到 [0, 1]，
        乘以 255 得到灰度；越界值被裁剪到边界（饱和）。

    参数定义：
        ww (Window Width, 窗宽)：显示窗口覆盖的 HU 值范围（窗口宽度）。
            ww 越大 → 更多 HU 值被压缩进同一灰度级，对比度越低，但可同时
            看清密度差异大的组织；ww 越小 → 对比度越高，细节越锐利。
        wl (Window Level / Center, 窗位)：窗口中心的 HU 值，决定被映射为
            中间灰度的 HU 段落，效果类似亮度调节。wl 越高 → 整体图像越暗
            （只有更高 HU 才显亮）。

    临床意义（肺窗为例）：
        肺窗常取 WW=1500、WL=-600（覆盖 HU 约 [-1350, +150]），使含气肺组织
        （约 -800 HU）落在暗灰区、纵隔软组织（约 +30~+50 HU）落在亮区，
        从而在低密度背景下清晰显示肺纹理、磨玻璃结节等病变。
        与之相对的纵隔窗（WW=400、WL=40）则用于观察心脏、大血管与纵隔结构。

    边界处理：
        低于窗下限（HU < low）的像素 → 裁剪为 0（纯黑）。
        高于窗上限（HU > high）的像素 → 裁剪为 1（纯白）。
        即越界像素"饱和"到灰度两端，保证输出不产生负值或 >255 的溢出。

    Args:
        hu: HU 值矩阵（float32 或可广播的数值数组）。
        ww: 窗宽，必须为正（内部钳制到 >= 1，避免除零与反向窗口）。
        wl: 窗位（窗口中心 HU 值）。
        invert: 是否反色（黑白翻转），默认 False。

    Returns:
        uint8 灰度图像，取值 [0, 255]，形状与输入一致。
    """
    # 窗宽钳制到 >= 1：ww=0 或负数会导致除零 / 窗口反向，先兜底
    ww = max(float(ww), 1.0)
    # 窗口上下限：以窗位为中心，向两侧各扩展半个窗宽
    low = wl - ww / 2.0
    high = wl + ww / 2.0

    # 核心映射：平移 + 归一化
    # (hu - low)     —— 平移，使窗下限对应 0
    # / (high - low) —— 除以窗宽，把窗口区间归一化到 [0, 1]
    normalized = (hu - low) / (high - low)
    # 边界裁剪：低于下限(<0)钳到 0，高于上限(>1)钳到 1，实现越界饱和
    normalized = np.clip(normalized, 0.0, 1.0)

    # 归一化值 ×255 转 uint8（截断取整），得到 0~255 灰度
    gray = (normalized * 255.0).astype(np.uint8)
    # 反色：255 减灰度，黑白互换
    if invert:
        gray = 255 - gray
    return gray
