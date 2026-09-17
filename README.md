# LungWindow — DICOM 肺窗图像处理工具

基于 **Python + pydicom + OpenCV + Streamlit** 的医学影像处理 Web 应用，
支持 DICOM CT 影像的读取、HU 值转换、窗宽窗位调整、图像增强、病灶标注与 PNG 导出。

> 本项目适合作为本科「医学影像处理」方向的课程设计 / 简历项目。

## 功能特性

- **DICOM 读取**：上传 `.dcm` 文件，解析像素数据与关键元数据
- **HU 值转换**：按 `RescaleSlope / RescaleIntercept` 还原 CT 值（亨氏单位）
- **多层面浏览**：支持多帧 DICOM，滑块 / 滚轮切换切片，浏览一整卷 CT
- **窗宽窗位**：手动调节 + 肺窗 / 纵隔窗 / 骨窗 / 脑窗预设 + 自动套用 DICOM 自带窗宽窗位，支持反色
- **图像增强**：CLAHE 直方图均衡、伽马校正、锐化
- **伪彩色**：Jet / Hot / Bone 等多种颜色映射
- **病灶标注**：鼠标交互绘制矩形 / 圆形，自动统计 ROI 平均 HU、标准差、极值与毫米尺寸
- **光标 HU 读数**：点选任意像素实时读取该点 HU 值
- **灰度直方图**：实时显示当前窗宽窗位下的灰度分布
- **PNG 导出**：一键下载处理结果（含标注叠加）
- **中英文界面**：一键切换
- **隐私脱敏**：患者信息默认隐藏，附带命令行脱敏工具

## 技术栈

| 库 | 用途 |
|---|---|
| pydicom | DICOM 读取与元数据解析 |
| numpy | 像素 / HU 矩阵运算 |
| opencv-python-headless | 窗位映射、CLAHE、标注绘制 |
| streamlit | 本地 Web 界面 |
| streamlit-drawable-canvas | 交互式标注画布 |
| Pillow | 图像格式转换与 PNG 编码 |

## 环境要求

- Python 3.9+（已在 Python 3.13 验证通过）
- Windows / macOS / Linux

## 安装与运行

```bash
# 1. 创建虚拟环境（推荐）
python -m venv .venv

# Windows 激活：
.venv\Scripts\activate
# macOS / Linux 激活：
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501 。

### ⚠️ 依赖版本说明（重要）

`requirements.txt` 中 `streamlit` 与 `streamlit-drawable-canvas` 已**锁定**为
`streamlit==1.40.0` + `streamlit-drawable-canvas==0.9.3`，请勿随意升级。原因：

| 组件 | 兼容性问题 |
|---|---|
| `streamlit >= 1.41` | 移除了 `streamlit.elements.image.image_to_url`，导致 canvas 0.9.x 在传入背景图时运行报错 `module has no attribute 'image_to_url'` |
| `streamlit-drawable-canvas >= 0.10` | 迁移到 Streamlit 的 `components.v2` 组件系统，但包内的 `pyproject.toml` 声明与注册名不一致，导入即报 `must be declared in pyproject.toml with asset_dir` |

也就是说：canvas 0.9.x 只能配 streamlit ≤ 1.40，canvas 0.10+ 依赖的 v2 机制在当前版本又有 bug，
交叉升级会直接导致应用无法运行。锁定上述组合可稳定运行。

### 国内网络 / 镜像提示

默认 `pip` 可能走国内镜像（如清华源）。若安装时提示 `opencv-python-headless`
或其它包「找不到版本」（部分镜像对 Python 3.13 的 wheel 同步不全），
可临时切换到官方源安装：

```bash
pip install -r requirements.txt -i https://pypi.org/simple
```

## 使用说明

1. 上传 `.dcm` CT 文件（数据仅本地处理，不会上传到服务器）
2. 多帧数据会在左侧出现「切片」滑块，切换浏览不同层面
3. 在左侧选择预设窗位（含自动套用 DICOM 窗宽窗位），或拖动窗宽 / 窗位滑块
4. 按需开启 CLAHE、伽马校正、锐化或伪彩色
5. 选择「矩形」或「圆形」工具框选病灶；选择「点」工具单击读取该点 HU 值
6. 查看 ROI 统计表（平均 HU、标准差、毫米尺寸）
7. 点击「下载 PNG」导出结果

## 生成演示数据（无需真实 DICOM）

项目不内置真实患者数据，但提供脚本生成一个**合成肺 CT 幻影**（多帧 + 含病灶结节），
可用于演示多层面浏览、窗宽窗位与病灶标注：

```bash
python scripts/make_phantom.py
```

生成的 `sample_data/lung_phantom.dcm` 为 16 帧 × 256×256 的多帧 CT 序列，
含胸腔软组织、双肺含气区与一个高密度结节，可直接上传到界面测试。

## 核心原理

### HU 值转换
```
HU = pixel × RescaleSlope + RescaleIntercept
```

### 窗宽窗位映射
```
low  = WL - WW / 2
high = WL + WW / 2
gray = clip((HU - low) / (high - low), 0, 1) × 255
```

### 病灶尺寸测量
利用 DICOM 的 `PixelSpacing (0028,0030)` 将像素尺寸换算为毫米：
```
尺寸(mm) = 像素数 × 像素间距(mm/px)
```

## 数据脱敏

出于隐私保护：
- 界面默认将患者姓名 / ID 显示为「已脱敏」
- 导出的 PNG 为纯图像，不含任何患者元数据
- 如需分享原始 DICOM，请先用脱敏工具生成副本：

```bash
python scripts/anonymize.py input.dcm output.dcm          # 单个文件
python scripts/anonymize.py ./raw_data ./anonymized_data  # 批量
```

## 目录结构

```
LungWindow/
├── app.py                  # Streamlit 主入口
├── config.py               # 全局常量（预设窗位、默认参数等）
├── requirements.txt        # 依赖清单
├── conftest.py             # pytest 路径配置
├── i18n/                   # 中英文文案
│   ├── __init__.py
│   ├── zh.py
│   └── en.py
├── core/                   # 核心处理逻辑
│   ├── dicom_loader.py     # DICOM 读取 + HU 转换 + 元数据
│   ├── windowing.py        # 窗宽窗位映射
│   ├── enhancement.py      # CLAHE / 伽马 / 锐化 / 伪彩色
│   ├── annotation.py       # 标注绘制 + ROI 统计 + 尺寸测量
│   ├── exporter.py         # PNG 导出
│   └── anonymizer.py       # DICOM 脱敏
├── ui/                     # Streamlit UI 组件
│   └── components.py
├── utils/                  # 工具函数
│   └── validators.py       # DICOM 校验
├── scripts/
│   ├── anonymize.py        # 命令行脱敏工具
│   └── make_phantom.py     # 合成肺 CT 幻影数据生成器
├── tests/                  # 单元测试
│   └── test_core.py
├── sample_data/            # 测试数据（需自行脱敏放入）
└── docs/                   # 文档与截图
    └── screenshots.md
```

## 运行测试

```bash
pytest
```

共 14 个单元测试，覆盖 HU 转换、窗宽窗位、反色、增强、伪彩色、PNG 导出、
矩形 / 圆形 ROI、点读数、多帧读取、窗位标签解析、脱敏与校验器。
测试使用代码内合成的 DICOM 数据集，无需真实影像数据即可运行。

## 许可证

MIT
