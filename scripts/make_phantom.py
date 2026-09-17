"""合成肺 CT 幻影数据生成器。

生成一个多帧 CT DICOM 序列（胸腔软组织 + 双肺含气区 + 一个病灶结节），
用于本地演示多层面浏览、窗宽窗位与病灶标注，不包含任何真实患者信息。

用法：
    python scripts/make_phantom.py                  # 默认写入 sample_data/lung_phantom.dcm
    python scripts/make_phantom.py ./my_phantom.dcm # 自定义输出路径
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import CTImageStorage, ImplicitVRLittleEndian, generate_uid

# 将项目根目录加入 sys.path（本脚本可独立运行）
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def build_phantom(n_slices: int = 16, size: int = 256) -> np.ndarray:
    """构建三维 HU 体积，形状 (n_slices, size, size)。

    简化解剖模型：
    - 背景空气：-1000 HU
    - 胸腔软组织椭圆：+30 HU
    - 左右双肺含气区：-800 HU
    - 右肺内一高密度结节（约 +100 HU），仅中部若干层可见
    """
    yy, xx = np.mgrid[:size, :size].astype(np.float32)
    cx, cy = size / 2.0, size / 2.0

    hu = np.full((n_slices, size, size), -1000.0, dtype=np.float32)

    # 胸腔软组织
    body = ((xx - cx) ** 2) / (size * 0.46) ** 2 + ((yy - cy) ** 2) / (size * 0.40) ** 2 <= 1.0
    hu[:, body] = 30.0

    # 双肺（含气）
    left_lung = ((xx - (cx - size * 0.18)) ** 2) / (size * 0.16) ** 2 + ((yy - cy) ** 2) / (size * 0.28) ** 2 <= 1.0
    right_lung = ((xx - (cx + size * 0.18)) ** 2) / (size * 0.16) ** 2 + ((yy - cy) ** 2) / (size * 0.28) ** 2 <= 1.0
    hu[:, left_lung | right_lung] = -800.0

    # 病灶结节（右肺内，中部切片可见，半径随层数变化近似球体）
    nodule_cx, nodule_cy, nodule_r = cx + size * 0.18, cy, size * 0.06
    center_z = n_slices // 2
    for z in range(center_z - 3, center_z + 3):
        frac = 1.0 - abs(z - center_z) / 3.0
        rr = nodule_r * frac
        if rr <= 0:
            continue
        mask = ((xx - nodule_cx) ** 2 + (yy - nodule_cy) ** 2) <= rr ** 2
        hu[z, mask] = 100.0

    return hu


def save_phantom(
    hu: np.ndarray,
    out_path: Path,
    spacing: tuple[float, float] = (0.7, 0.7),
    slice_thickness: float = 5.0,
) -> None:
    """将 HU 体积写入多帧 DICOM 文件。"""
    n_slices, rows, cols = hu.shape

    ds = Dataset()
    ds.SOPClassUID = CTImageStorage
    ds.SOPInstanceUID = generate_uid()
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.Modality = "CT"
    ds.PatientName = "Anonymous^Phantom"
    ds.PatientID = "PHANTOM001"
    ds.SeriesDescription = "Synthetic Lung Phantom"
    ds.StudyDescription = "LungWindow demo"

    ds.Rows = rows
    ds.Columns = cols
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0  # 无符号
    ds.RescaleSlope = 1.0
    ds.RescaleIntercept = -1024.0
    ds.NumberOfFrames = n_slices
    ds.PixelSpacing = list(spacing)
    ds.SliceThickness = slice_thickness
    ds.SpacingBetweenSlices = slice_thickness
    ds.WindowCenter = -600.0
    ds.WindowWidth = 1500.0

    # 存储值 = HU + 1024（非负，适配无符号 16 位）
    stored = np.clip(hu + 1024.0, 0, 65535).astype(np.uint16)
    ds.PixelData = stored.tobytes()

    ds.file_meta = FileMetaDataset()
    ds.file_meta.MediaStorageSOPClassUID = CTImageStorage
    ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # enforce_file_format=True 写入 128 字节导言 + "DICM" 魔数与文件元信息，
    # 保证生成的 DICOM Part 10 文件可被 pydicom.dcmread 直接读取。
    ds.save_as(str(out_path), enforce_file_format=True)
    print(f"[OK] 已生成 {out_path} （{n_slices} 帧 × {rows}×{cols}，层厚 {slice_thickness} mm）")


def main() -> None:
    parser = argparse.ArgumentParser(description="生成合成肺 CT 幻影 DICOM 数据")
    parser.add_argument("output", nargs="?", default=None, help="输出路径（默认 sample_data/lung_phantom.dcm）")
    parser.add_argument("--size", type=int, default=256, help="图像宽高（默认 256）")
    parser.add_argument("--slices", type=int, default=16, help="切片帧数（默认 16）")
    args = parser.parse_args()

    out = Path(args.output) if args.output else ROOT / "sample_data" / "lung_phantom.dcm"
    hu = build_phantom(n_slices=args.slices, size=args.size)
    save_phantom(hu, out)


if __name__ == "__main__":
    main()
