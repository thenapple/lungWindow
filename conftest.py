"""pytest 配置：确保项目根目录在 sys.path 中，使 `import core` 可用。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
