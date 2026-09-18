"""core/windowing.py 窗宽窗位转换函数的单元测试。"""

import numpy as np
import pytest

from core.windowing import apply_window


# ---------------------------------------------------------------
# 1. 标准肺窗验证（WW=1500, WL=-600）
# ---------------------------------------------------------------
def test_standard_lung_window():
    """标准肺窗：已知 HU 值映射到 8 位灰度的结果与理论值一致。"""
    hu = np.array([-1000.0, -800.0, -600.0, 0.0, 100.0, 150.0], dtype=np.float32)
    gray = apply_window(hu, ww=1500.0, wl=-600.0)

    # 理论值：窗区间 [-1350, 150]，gray = (HU + 1350) / 1500 * 255
    expected = np.array([59.5, 93.5, 127.5, 229.5, 246.5, 255.0], dtype=np.float32)

    assert gray.dtype == np.uint8
    assert gray.shape == hu.shape
    # uint8 截断取整，允许 ±1 灰度精度误差
    np.testing.assert_allclose(gray.astype(np.float32), expected, atol=1.0)


# ---------------------------------------------------------------
# 2. 边界裁剪验证
# ---------------------------------------------------------------
def test_boundary_clipping():
    """低于窗下限裁剪为 0，高于窗上限裁剪为 255，越界不溢出。"""
    # WW=1500/WL=-600 -> 窗区间 [-1350, 150]
    hu = np.array([-2000.0, -1350.0, 150.0, 500.0], dtype=np.float32)
    gray = apply_window(hu, ww=1500.0, wl=-600.0)

    # 低于下限 -> 0；等于下限 -> 0；等于上限 -> 255；高于上限 -> 255
    np.testing.assert_array_equal(gray, np.array([0, 0, 255, 255], dtype=np.uint8))


# ---------------------------------------------------------------
# 3. 多窗位兼容：纵隔窗（WW=400, WL=40）
# ---------------------------------------------------------------
def test_mediastinal_window():
    """纵隔窗参数下的转换结果符合预期，验证函数对多组窗位的通用性。"""
    # WW=400/WL=40 -> 窗区间 [-160, 240]
    hu = np.array([40.0, 0.0, 100.0], dtype=np.float32)
    gray = apply_window(hu, ww=400.0, wl=40.0)

    expected = np.array([127.5, 102.0, 165.75], dtype=np.float32)
    np.testing.assert_allclose(gray.astype(np.float32), expected, atol=1.0)


# ---------------------------------------------------------------
# 4. 异常输入容错
# ---------------------------------------------------------------
def test_empty_input():
    """空数组：不抛异常，返回空的 uint8 数组。"""
    gray = apply_window(np.array([], dtype=np.float32), ww=1500.0, wl=-600.0)
    assert gray.dtype == np.uint8
    assert gray.size == 0


def test_non_numeric_input():
    """NaN / ±inf：不抛异常，无穷值被饱和到灰度两端。"""
    with np.errstate(invalid="ignore"):  # 忽略 NaN 转 uint8 的告警
        gray = apply_window(np.array([np.nan, np.inf, -np.inf]), ww=1500.0, wl=-600.0)

    assert gray.dtype == np.uint8
    assert gray[1] == 255  # +inf 被裁剪到窗口上限
    assert gray[2] == 0    # -inf 被裁剪到窗口下限
    assert gray[0] == 0    # NaN 经 uint8 转换后为 0，且不抛异常


def test_zero_or_negative_ww():
    """ww<=0 被钳制到 1，避免除零错误。"""
    # ww=0 -> 钳制为 1，窗区间 [-0.5, 0.5]
    gray = apply_window(np.array([0.0, 1.0, -1.0]), ww=0.0, wl=0.0)
    np.testing.assert_array_equal(gray, np.array([127, 255, 0], dtype=np.uint8))

    # 负 ww 同样钳制到 1，输出有限值
    assert apply_window(np.array([0.0]), ww=-50.0, wl=0.0)[0] == 127
