"""命令行 DICOM 脱敏工具。

用法：
    python scripts/anonymize.py <input> <output>
    - input / output 可以是单个 .dcm 文件，或目录（批量处理）。

示例：
    python scripts/anonymize.py sample.dcm sample_anonymized.dcm
    python scripts/anonymize.py ./raw_data ./anonymized_data
"""

from __future__ import annotations

import sys
from pathlib import Path

# 将项目根目录加入 sys.path，使 `import core` 可用
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import anonymizer  # noqa: E402


def process_file(src: Path, dst: Path) -> None:
    anonymizer.anonymize_file(str(src), str(dst))
    print(f"[OK] {src.name} -> {dst.name}")


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        files = sorted(list(src.glob("*.dcm")) + list(src.glob("*.dicom")))
        if not files:
            print(f"目录 {src} 中未找到 .dcm / .dicom 文件")
            sys.exit(1)
        for f in files:
            process_file(f, dst / f.name)
    elif src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        process_file(src, dst)
    else:
        print(f"找不到输入路径：{src}")
        sys.exit(1)

    print("脱敏完成。")


if __name__ == "__main__":
    main()
