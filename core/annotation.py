"""病灶标注与 ROI 统计。

解析 streamlit-drawable-canvas 返回的 JSON 对象，在图像上叠加标注，
并计算框选区域的 HU 统计量与毫米尺寸。

坐标约定：streamlit-drawable-canvas 返回的形状以左上角为原点，
矩形为 (left, top, width, height)，圆形为 (left, top, radius)。
"""

from __future__ import annotations

from typing import Any, Optional

import cv2
import numpy as np

ANNOTATION_COLOR = (0, 255, 0)   # 边框颜色（BGR，绿色）
FILL_COLOR = (0, 0, 255)         # 填充颜色（BGR，红色）
FILL_ALPHA = 0.35                # 填充透明度


def extract_shapes(json_data: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
    """从画布 JSON 中提取矩形 / 圆形标注对象。"""
    if not json_data or "objects" not in json_data:
        return []
    return [obj for obj in json_data["objects"] if obj.get("type") in ("rect", "circle")]


def extract_points(json_data: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
    """从画布 JSON 中提取点标注对象（用于读取该点 HU 值）。"""
    if not json_data or "objects" not in json_data:
        return []
    return [obj for obj in json_data["objects"] if obj.get("type") == "point"]


def _point_coords(shape: dict[str, Any]) -> Optional[tuple[int, int]]:
    """解析点的像素坐标，返回 (x, y)；无法解析时返回 None。

    兼容不同版本画布返回的字段：left/top、x/y 或 x1/y1。
    """
    for x_key, y_key in (("left", "top"), ("x", "y"), ("x1", "y1")):
        if x_key in shape and y_key in shape:
            try:
                return int(shape[x_key]), int(shape[y_key])
            except (TypeError, ValueError):
                return None
    return None


def point_hu(hu: np.ndarray, shape: dict[str, Any]) -> Optional[dict[str, Any]]:
    """返回指定点处的 HU 值；坐标越界或无效时返回 None。"""
    coords = _point_coords(shape)
    if coords is None:
        return None
    x, y = coords
    height, width = hu.shape
    if not (0 <= x < width and 0 <= y < height):
        return None
    return {"x": x, "y": y, "hu": float(hu[y, x])}


def _circle_geometry(shape: dict[str, Any]) -> tuple[int, int, int]:
    """返回圆形 (center_x, center_y, radius)。"""
    radius = float(shape.get("radius") or 0.0)
    if radius == 0.0 and shape.get("width"):
        radius = float(shape["width"]) / 2.0
    cx = int(shape.get("left", 0) + radius)
    cy = int(shape.get("top", 0) + radius)
    return cx, cy, int(round(radius))


def draw_shapes(image_bgr: np.ndarray, shapes: list[dict[str, Any]]) -> np.ndarray:
    """在图像上叠加半透明标注，返回 BGR 图像。"""
    overlay = image_bgr.copy()
    for shape in shapes:
        if shape["type"] == "rect":
            p1 = (int(shape["left"]), int(shape["top"]))
            p2 = (int(shape["left"] + shape["width"]), int(shape["top"] + shape["height"]))
            cv2.rectangle(overlay, p1, p2, FILL_COLOR, thickness=-1)
            cv2.rectangle(overlay, p1, p2, ANNOTATION_COLOR, thickness=2)
        elif shape["type"] == "circle":
            cx, cy, radius = _circle_geometry(shape)
            cv2.circle(overlay, (cx, cy), radius, FILL_COLOR, thickness=-1)
            cv2.circle(overlay, (cx, cy), radius, ANNOTATION_COLOR, thickness=2)
    return cv2.addWeighted(overlay, FILL_ALPHA, image_bgr, 1.0 - FILL_ALPHA, 0)


def mask_from_shape(shape: dict[str, Any], height: int, width: int) -> np.ndarray:
    """生成与图像同尺寸的布尔掩码，标记标注内部区域。"""
    mask = np.zeros((height, width), dtype=bool)
    if shape["type"] == "rect":
        x0 = max(int(shape["left"]), 0)
        y0 = max(int(shape["top"]), 0)
        x1 = min(int(shape["left"] + shape["width"]), width)
        y1 = min(int(shape["top"] + shape["height"]), height)
        if x1 > x0 and y1 > y0:
            mask[y0:y1, x0:x1] = True
    elif shape["type"] == "circle":
        cx, cy, radius = _circle_geometry(shape)
        yy, xx = np.ogrid[:height, :width]
        mask[(xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2] = True
    return mask


def roi_stats(
    hu: np.ndarray,
    shape: dict[str, Any],
    pixel_spacing: Optional[tuple[float, float]] = None,
) -> Optional[dict[str, float]]:
    """计算标注区域的 HU 统计量与毫米尺寸。

    Args:
        hu: HU 值矩阵。
        shape: 标注对象（rect / circle）。
        pixel_spacing: (行间距, 列间距)，单位 mm。
            行间距对应 y 方向（高），列间距对应 x 方向（宽）。

    Returns:
        统计字典；若区域内无像素则返回 None。
    """
    height, width = hu.shape
    mask = mask_from_shape(shape, height, width)
    values = hu[mask]
    if values.size == 0:
        return None

    stats: dict[str, float] = {
        "mean": float(values.mean()),
        "std": float(values.std()),
        "min": float(values.min()),
        "max": float(values.max()),
        "area_px": float(values.size),
    }
    if pixel_spacing:
        row_spacing, col_spacing = pixel_spacing
        if shape["type"] == "rect":
            stats["width_mm"] = float(shape["width"]) * col_spacing
            stats["height_mm"] = float(shape["height"]) * row_spacing
        elif shape["type"] == "circle":
            _, _, radius = _circle_geometry(shape)
            stats["diameter_mm"] = 2.0 * radius * col_spacing
    return stats
