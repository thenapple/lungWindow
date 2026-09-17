"""中文文案。"""

STRINGS: dict[str, str] = {
    # 应用标题
    "app_title": "DICOM 肺窗图像处理工具",
    "app_subtitle": "读取 · 窗宽窗位 · 增强 · 标注 · 导出",

    # 上传
    "upload_file": "上传 DICOM 文件",
    "upload_hint": "支持 .dcm 格式的 CT 影像，文件仅在本地处理，不会上传到服务器。",
    "no_file": "请先上传一个 DICOM 文件。",

    # 元数据
    "metadata_header": "影像元数据",
    "show_patient_info": "显示完整患者信息（含敏感字段）",
    "privacy_note": "出于隐私保护，患者姓名 / ID 默认脱敏显示。导出的 PNG 为纯图像，不含任何患者元数据。",
    "anonymized": "已脱敏",

    "meta_patient_name": "患者姓名",
    "meta_patient_id": "患者 ID",
    "meta_modality": "检查类型",
    "meta_study_date": "检查日期",
    "meta_series_desc": "序列描述",
    "meta_rows_cols": "图像尺寸",
    "meta_frames": "帧数",
    "meta_pixel_spacing": "像素间距",
    "meta_slice_thickness": "层厚",
    "meta_window_center": "窗位 (WL)",
    "meta_window_width": "窗宽 (WW)",
    "meta_rescale_slope": "Rescale 斜率",
    "meta_rescale_intercept": "Rescale 截距",
    "meta_manufacturer": "设备厂商",
    "meta_bits": "位深",

    # 切片浏览
    "slice_header": "切片浏览",
    "slice_label": "切片",
    "frame_indicator": "第 {current} / {total} 帧",

    # 窗宽窗位
    "window_header": "窗宽 / 窗位",
    "preset_label": "预设窗位",
    "preset_auto": "自动（来自 DICOM）",
    "preset_lung": "肺窗 (1500 / -600)",
    "preset_mediastinal": "纵隔窗 (400 / 40)",
    "preset_bone": "骨窗 (2000 / 350)",
    "preset_brain": "脑窗 (80 / 40)",
    "preset_custom": "自定义",
    "ww_label": "窗宽 (WW)",
    "wl_label": "窗位 (WL)",
    "invert_label": "反色显示",

    # 图像增强
    "enhancement_header": "图像增强",
    "clahe_label": "CLAHE 直方图均衡",
    "clahe_clip_label": "CLAHE 对比度限幅",
    "gamma_label": "伽马校正",
    "gamma_value_label": "伽马值",
    "sharpen_label": "锐化",
    "sharpen_strength_label": "锐化强度",

    # 伪彩色
    "colormap_header": "伪彩色显示",
    "colormap_label": "颜色映射",
    "cmap_gray": "灰度",
    "cmap_jet": "彩虹 (Jet)",
    "cmap_hot": "热力图 (Hot)",
    "cmap_bone": "骨窗 (Bone)",
    "cmap_inferno": "烈焰 (Inferno)",
    "cmap_viridis": "翠绿 (Viridis)",

    # 直方图
    "histogram_header": "灰度直方图",
    "histogram_show": "显示当前窗宽窗位下的灰度直方图",
    "histogram_x": "HU 值",
    "histogram_y": "像素数量",

    # 标注
    "annotation_header": "病灶区域标注",
    "drawing_mode_label": "绘制工具",
    "mode_rect": "矩形",
    "mode_circle": "圆形",
    "mode_point": "点（读数）",
    "mode_transform": "选择 / 移动",
    "annotation_hint": "拖动鼠标框选病灶区域查看 ROI 统计；选择「点」后单击可读取该点 HU 值。",

    # 光标 HU 读数
    "point_header": "光标 HU 读数",
    "point_coord": "坐标 (px)",
    "point_value": "HU 值",
    "point_empty": "尚未选点。请选择「点」工具后在图像上单击。",

    # ROI 统计
    "roi_header": "ROI 统计结果",
    "roi_empty": "尚未绘制标注。请在图像上框选病灶区域。",
    "roi_index": "区域",
    "roi_mean": "平均 HU",
    "roi_std": "标准差",
    "roi_min": "最小 HU",
    "roi_max": "最大 HU",
    "roi_width_mm": "宽 (mm)",
    "roi_height_mm": "高 (mm)",
    "roi_diameter_mm": "直径 (mm)",
    "roi_no_spacing": "该图像缺少像素间距信息，无法计算毫米尺寸。",

    # 导出
    "export_header": "导出",
    "export_button": "下载 PNG 图像",
    "export_hint": "导出内容为当前预览图像（含窗宽窗位、增强与标注叠加）。",
    "export_filename": "lungwindow",

    # 错误
    "error_invalid": "无法解析该文件，请确认是有效的 DICOM 文件。",
    "error_no_pixel": "该 DICOM 文件不包含像素数据。",
    "error_not_ct": "该文件不是 CT 影像（检查类型: {}），窗宽窗位预设主要针对 CT 设计。",
}
