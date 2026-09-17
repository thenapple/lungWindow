"""DICOM 文件读取与基础处理。

主要职责：
1. 从字节流 / 文件路径读取 DICOM 数据集；
2. 提取像素矩阵并转换为 HU（亨氏单位）；
3. 抽取界面展示所需的元数据。
"""

from __future__ import annotations

import io
from typing import Any, Optional

import numpy as np
import pydicom
from pydicom.dataset import Dataset


def load_dicom(data: bytes) -> Dataset:
    """从字节流读取 DICOM 数据集（适配 Streamlit 上传文件）。"""
    return pydicom.dcmread(io.BytesIO(data))


def load_dicom_file(path: str) -> Dataset:
    """从本地路径读取 DICOM 数据集。"""
    return pydicom.dcmread(path)


def get_pixel_array(ds: Dataset, frame_index: int = 0) -> np.ndarray:
    """提取像素矩阵（float32），支持多帧数据取指定帧。

    CT 通常为单帧二维图像；多帧数据按第一维切片。
    """
    arr = ds.pixel_array
    if arr.ndim == 3:
        arr = arr[frame_index]
    return arr.astype(np.float32)


def get_frame_count(ds: Dataset) -> int:
    """返回帧数（多帧 DICOM 为帧数，单帧二维图像为 1）。"""
    n = getattr(ds, "NumberOfFrames", None)
    if n is not None:
        return int(n)
    return 1


def get_window(ds: Dataset) -> Optional[tuple[float, float]]:
    """从 DICOM 自带窗宽窗位标签读取 (窗宽, 窗位)。

    WindowCenter / WindowWidth 可能为多值（MultiValue），取首值。
    缺失或无法解析时返回 None。
    """
    center = getattr(ds, "WindowCenter", None)
    width = getattr(ds, "WindowWidth", None)
    if center is None or width is None:
        return None

    def _first(value: Any) -> Optional[float]:
        # MultiValue 是 pydicom 的多值类型（非 list 子类），需单独判断
        if isinstance(value, (pydicom.multival.MultiValue, list, tuple)):
            value = value[0] if len(value) else None
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    c = _first(center)
    w = _first(width)
    if c is None or w is None or w <= 0:
        return None
    return w, c


def to_hu(ds: Dataset, pixel_array: np.ndarray) -> np.ndarray:
    """将像素原始值转换为 HU 值。

    HU = pixel * RescaleSlope + RescaleIntercept
    斜率 / 截距从 DICOM 标签读取，缺失时取默认值（1 / 0）。
    """
    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))
    return pixel_array * slope + intercept


def get_pixel_spacing(ds: Dataset) -> Optional[tuple[float, float]]:
    """返回像素间距 (行间距, 列间距)，单位 mm；缺失时返回 None。

    PixelSpacing[0] 为行间距（对应图像纵向 / y），
    PixelSpacing[1] 为列间距（对应图像横向 / x）。
    """
    spacing = getattr(ds, "PixelSpacing", None)
    if spacing is None or len(spacing) < 2:
        return None
    return float(spacing[0]), float(spacing[1])


def get_metadata(ds: Dataset) -> dict[str, Any]:
    """抽取关键元数据，供界面展示。"""
    def _str(value: Any) -> str:
        """安全转字符串；单元素列表 / 多值类型取首元素。"""
        if value is None:
            return ""
        if isinstance(value, (list, tuple)) and len(value) == 1:
            return str(value[0])
        return str(value)

    return {
        "PatientName": _str(getattr(ds, "PatientName", "")),
        "PatientID": _str(getattr(ds, "PatientID", "")),
        "Modality": _str(getattr(ds, "Modality", "")),
        "StudyDate": _str(getattr(ds, "StudyDate", "")),
        "SeriesDescription": _str(getattr(ds, "SeriesDescription", "")),
        "Rows": int(getattr(ds, "Rows", 0)),
        "Columns": int(getattr(ds, "Columns", 0)),
        "NumberOfFrames": int(getattr(ds, "NumberOfFrames", 1)),
        "PixelSpacing": get_pixel_spacing(ds),
        "SliceThickness": _str(getattr(ds, "SliceThickness", "")),
        "WindowCenter": _str(getattr(ds, "WindowCenter", "")),
        "WindowWidth": _str(getattr(ds, "WindowWidth", "")),
        "RescaleSlope": _str(getattr(ds, "RescaleSlope", "")),
        "RescaleIntercept": _str(getattr(ds, "RescaleIntercept", "")),
        "Manufacturer": _str(getattr(ds, "Manufacturer", "")),
        "BitsAllocated": _str(getattr(ds, "BitsAllocated", "")),
    }
