"""DICOM 文件校验。"""

from __future__ import annotations

from pydicom.dataset import Dataset


def has_pixel_data(ds: Dataset) -> bool:
    """是否包含像素数据。"""
    return hasattr(ds, "PixelData")


def is_ct(ds: Dataset) -> bool:
    """是否为 CT 影像。"""
    modality = str(getattr(ds, "Modality", "")).upper()
    return modality == "CT"


def has_pixel_spacing(ds: Dataset) -> bool:
    """是否包含像素间距信息。"""
    spacing = getattr(ds, "PixelSpacing", None)
    return spacing is not None and len(spacing) >= 2
