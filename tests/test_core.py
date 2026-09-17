"""核心模块单元测试。"""

import io

import numpy as np
import pydicom
import pytest
from PIL import Image
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ImplicitVRLittleEndian

from core import anonymizer, annotation, enhancement, exporter, windowing
from core.dicom_loader import (
    get_frame_count,
    get_pixel_array,
    get_window,
    to_hu,
)
from utils import validators


def make_ct_dataset() -> Dataset:
    """构造一个最小可用的 CT DICOM 数据集。"""
    ds = Dataset()
    ds.Rows = 8
    ds.Columns = 8
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.RescaleSlope = 1.0
    ds.RescaleIntercept = -1024.0
    ds.PixelSpacing = [0.7, 0.7]
    ds.PatientName = "Test^Patient"
    ds.PatientID = "12345"
    ds.Modality = "CT"
    arr = np.zeros((8, 8), dtype=np.uint16)
    ds.PixelData = arr.tobytes()
    # pydicom 3.x 解码像素数据需要传输语法
    ds.file_meta = FileMetaDataset()
    ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
    return ds


def test_to_hu():
    ds = make_ct_dataset()
    pixel = get_pixel_array(ds)
    hu = to_hu(ds, pixel)
    # 像素 0，斜率 1，截距 -1024 -> -1024 HU
    assert hu[0, 0] == pytest.approx(-1024.0)


def test_apply_window_clips():
    hu = np.array([[-2000.0], [0.0], [2000.0]], dtype=np.float32)
    gray = windowing.apply_window(hu, ww=400.0, wl=40.0)  # 范围 [-160, 240]
    assert gray[0, 0] == 0     # 低于下限 -> 0
    assert gray[1, 0] == 102   # (0 - (-160)) / 400 * 255 = 102
    assert gray[2, 0] == 255   # 高于上限 -> 255


def test_gamma_identity():
    gray = np.array([[0, 128, 255]], dtype=np.uint8)
    out = enhancement.gamma_correct(gray, gamma=1.0)
    np.testing.assert_array_equal(out, gray)


def test_roi_stats_rect():
    hu = np.zeros((8, 8), dtype=np.float32)
    hu[2:6, 2:6] = 100.0
    shape = {"type": "rect", "left": 2, "top": 2, "width": 4, "height": 4}
    stats = annotation.roi_stats(hu, shape, pixel_spacing=(0.7, 0.7))
    assert stats["mean"] == pytest.approx(100.0)
    assert stats["width_mm"] == pytest.approx(2.8)   # 4 px * 0.7 mm
    assert stats["height_mm"] == pytest.approx(2.8)


def test_anonymize():
    ds = make_ct_dataset()
    clean = anonymizer.anonymize(ds)
    assert str(clean.PatientName) == "Anonymous^Patient"
    assert clean.PatientID == "ANONYMOUS"
    assert clean.PatientIdentityRemoved == "YES"


def test_apply_window_invert():
    hu = np.zeros((1, 1), dtype=np.float32)
    gray = windowing.apply_window(hu, ww=400.0, wl=40.0, invert=False)
    inv = windowing.apply_window(hu, ww=400.0, wl=40.0, invert=True)
    assert gray[0, 0] + inv[0, 0] == 255


def test_get_frame_count():
    ds = make_ct_dataset()
    assert get_frame_count(ds) == 1  # 单帧二维图像
    ds.NumberOfFrames = 4
    assert get_frame_count(ds) == 4


def test_get_window():
    ds = make_ct_dataset()
    assert get_window(ds) is None  # 无窗宽窗位标签
    ds.WindowCenter = -600.0
    ds.WindowWidth = 1500.0
    assert get_window(ds) == (1500.0, -600.0)
    # 多值（MultiValue）取首值
    ds.WindowCenter = pydicom.multival.MultiValue(float, [-600.0, 40.0])
    ds.WindowWidth = pydicom.multival.MultiValue(float, [1500.0, 400.0])
    assert get_window(ds) == (1500.0, -600.0)


def test_sharpen():
    gray = np.zeros((16, 16), dtype=np.uint8)
    gray[6:10, 6:10] = 200
    same = enhancement.sharpen(gray, 0.0)
    np.testing.assert_array_equal(same, gray)
    out = enhancement.sharpen(gray, 2.0)
    assert out.dtype == np.uint8
    assert out.shape == gray.shape


def test_apply_colormap():
    gray = np.zeros((8, 8), dtype=np.uint8)
    gray_3ch = enhancement.apply_colormap(gray, "gray")
    jet_3ch = enhancement.apply_colormap(gray, "jet")
    assert gray_3ch.shape == (8, 8, 3)
    assert jet_3ch.shape == (8, 8, 3)
    assert not np.array_equal(gray_3ch, jet_3ch)


def test_encode_png_roundtrip():
    rgb = np.zeros((4, 4, 3), dtype=np.uint8)
    rgb[..., 0] = 255
    data = exporter.encode_png(rgb)
    img = Image.open(io.BytesIO(data))
    assert img.size == (4, 4)
    assert img.mode == "RGB"


def test_validators():
    ds = make_ct_dataset()
    assert validators.has_pixel_data(ds)
    assert validators.is_ct(ds)
    assert validators.has_pixel_spacing(ds)
    ds.PixelSpacing = None
    assert not validators.has_pixel_spacing(ds)


def test_roi_stats_circle():
    hu = np.zeros((8, 8), dtype=np.float32)
    hu[3:6, 3:6] = 50.0
    shape = {"type": "circle", "left": 3, "top": 3, "radius": 2}
    stats = annotation.roi_stats(hu, shape, pixel_spacing=(0.7, 0.7))
    assert stats is not None
    assert stats["area_px"] > 0
    assert stats["diameter_mm"] == pytest.approx(2 * 2 * 0.7)


def test_point_hu():
    hu = np.zeros((8, 8), dtype=np.float32)
    hu[2, 5] = 42.0
    val = annotation.point_hu(hu, {"type": "point", "left": 5, "top": 2})
    assert val["hu"] == pytest.approx(42.0)
    assert val["x"] == 5 and val["y"] == 2
    # 越界返回 None
    assert annotation.point_hu(hu, {"type": "point", "left": 99, "top": 99}) is None
