"""全局配置与常量。

集中管理预设窗位、默认参数、伪彩色列表等常量，
避免在业务代码中散落“魔法数字”。
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 预设窗位（WW: 窗宽, WL: 窗位），单位 HU
# 常见参考值：肺窗 / 纵隔窗 / 骨窗 / 脑窗
# ---------------------------------------------------------------------------
PRESET_WINDOWS: dict[str, dict[str, float]] = {
    "lung":        {"ww": 1500.0, "wl": -600.0},  # 肺窗
    "mediastinal": {"ww": 400.0,  "wl": 40.0},    # 纵隔窗
    "bone":        {"ww": 2000.0, "wl": 350.0},   # 骨窗
    "brain":       {"ww": 80.0,   "wl": 40.0},    # 脑窗
}

# 默认窗宽窗位（默认使用肺窗）
DEFAULT_WW: float = PRESET_WINDOWS["lung"]["ww"]
DEFAULT_WL: float = PRESET_WINDOWS["lung"]["wl"]

# 窗宽 / 窗位滑块调节范围
WW_RANGE: tuple[int, int] = (1, 4000)
WL_RANGE: tuple[int, int] = (-2000, 2000)

# ---------------------------------------------------------------------------
# 图像增强默认参数
# ---------------------------------------------------------------------------
DEFAULT_CLAHE_CLIP: float = 2.0
DEFAULT_CLAHE_TILE: int = 8
DEFAULT_GAMMA: float = 1.0
DEFAULT_SHARPEN_STRENGTH: float = 1.0

# ---------------------------------------------------------------------------
# 伪彩色映射列表（"gray" 表示保持灰度，其余在 enhancement.py 中映射到 OpenCV）
# ---------------------------------------------------------------------------
COLORMAPS: list[str] = ["gray", "jet", "hot", "bone", "inferno", "viridis"]
