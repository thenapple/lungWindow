"""LungWindow 命令行入口。

读取 DICOM CT 影像，按窗宽窗位（Window Width / Window Level）将原始 HU 值
映射为 8 位灰度图，并导出 PNG。适合无图形界面的批处理 / 快速验证场景。

用法：
    # 标准肺窗（默认 WW=1500, WL=-600），输出与输入同目录、同名 .png
    python main.py -i sample_data/lung_phantom.dcm

    # 自定义窗宽窗位与输出路径（纵隔窗）
    python main.py -i input.dcm -w 400 -l 40 -o mediastinal.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 将项目根目录加入 sys.path，保证脚本可从任意位置独立运行
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from core import dicom_loader, exporter, windowing
from utils import validators


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="lungwindow",
        description="DICOM CT 肺窗图像处理：读取 DICOM → 窗宽窗位转换 → 导出 PNG",
        epilog="示例：python main.py -i sample_data/lung_phantom.dcm",
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="输入的 DICOM 文件路径（.dcm）",
    )
    parser.add_argument(
        "-w", "--ww", type=float, default=config.DEFAULT_WW,
        help=f"窗宽（Window Width），默认 {config.DEFAULT_WW:g}",
    )
    parser.add_argument(
        "-l", "--wl", type=float, default=config.DEFAULT_WL,
        help=f"窗位（Window Level），默认 {config.DEFAULT_WL:g}",
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="输出 PNG 路径；默认与输入同目录、同名、.png 后缀",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    """执行主流程，返回进程退出码（0 成功，非 0 失败）。"""
    input_path = Path(args.input)

    # 1. 输入文件校验
    if not input_path.is_file():
        print(f"[错误] 输入文件不存在：{input_path}", file=sys.stderr)
        return 1

    # 2. 窗宽合法性提示（apply_window 内部会将 ww<=0 钳制到 1）
    if args.ww <= 0:
        print(f"[提示] 窗宽 {args.ww:g} 无效（需 > 0），已自动钳制为 1。")

    # 3. 确定输出路径：默认与输入同目录、同名、.png 后缀
    output_path = Path(args.output) if args.output else input_path.with_suffix(".png")

    # 4. 读取 DICOM
    try:
        ds = dicom_loader.load_dicom_file(str(input_path))
    except Exception as exc:
        print(f"[错误] DICOM 读取失败：{exc}", file=sys.stderr)
        return 1

    # 5. 校验像素数据
    if not validators.has_pixel_data(ds):
        print("[错误] 该 DICOM 不包含像素数据，无法处理。", file=sys.stderr)
        return 1
    if not validators.is_ct(ds):
        modality = str(getattr(ds, "Modality", "未知"))
        print(f"[提示] 影像模态为 {modality}（非 CT），仍按 HU 值执行窗宽窗位转换。")

    # 6. 窗宽窗位转换 + 导出 PNG
    try:
        pixel = dicom_loader.get_pixel_array(ds, 0)          # 取第 1 帧
        hu = dicom_loader.to_hu(ds, pixel)                   # 原始像素值 -> HU
        gray = windowing.apply_window(hu, args.ww, args.wl)  # HU -> 8 位灰度
        output_path.parent.mkdir(parents=True, exist_ok=True)
        exporter.save_png(gray, str(output_path))            # 灰度 -> PNG
    except Exception as exc:
        print(f"[错误] 处理失败：{exc}", file=sys.stderr)
        return 1

    # 7. 控制台输出处理结果
    print("[完成] 窗宽窗位转换成功")
    print(f"  输入文件：{input_path}")
    print(f"  窗宽窗位：WW={args.ww:g}  WL={args.wl:g}")
    print(f"  图像尺寸：{gray.shape[1]} × {gray.shape[0]} 像素")
    print(f"  HU 值范围：{float(hu.min()):.1f} ~ {float(hu.max()):.1f}")
    print(f"  输出文件：{output_path}")
    return 0


def main() -> int:
    """命令行入口：解析参数并执行主流程。"""
    parser = build_parser()
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
