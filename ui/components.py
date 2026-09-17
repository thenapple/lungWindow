"""Streamlit 可复用 UI 组件。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

import config
from core import annotation, dicom_loader
from i18n import t


def language_selector() -> str:
    """语言选择器，返回 "zh" 或 "en"。"""
    return st.sidebar.selectbox(
        "语言 / Language",
        options=["zh", "en"],
        format_func=lambda c: {"zh": "中文", "en": "English"}[c],
        index=0,
        key="lang",
    )


def sidebar_window_controls(lang: str, dicom_window: tuple[float, float] | None = None) -> tuple[int, int, bool]:
    """窗宽窗位侧边栏控件，返回 (窗宽, 窗位, 是否反色)。

    dicom_window: DICOM 自带的 (窗宽, 窗位)。存在时增加「自动」预设并默认选中。
    """
    def _clamp(v: float, lo: int, hi: int) -> int:
        return int(min(max(v, lo), hi))

    st.sidebar.subheader(t("window_header", lang))
    presets = ["lung", "mediastinal", "bone", "brain", "custom"]
    if dicom_window is not None:
        presets.insert(0, "auto")
    preset = st.sidebar.selectbox(
        t("preset_label", lang),
        options=presets,
        format_func=lambda p: t(f"preset_{p}", lang),
        index=0,
    )
    if preset == "auto" and dicom_window is not None:
        ww_default = _clamp(dicom_window[0], *config.WW_RANGE)
        wl_default = _clamp(dicom_window[1], *config.WL_RANGE)
    elif preset != "custom":
        ww_default = int(config.PRESET_WINDOWS[preset]["ww"])
        wl_default = int(config.PRESET_WINDOWS[preset]["wl"])
    else:
        ww_default = int(config.DEFAULT_WW)
        wl_default = int(config.DEFAULT_WL)

    # 使用 preset 作为 key：切换预设时滑块自动回到对应默认值
    ww = st.sidebar.slider(
        t("ww_label", lang), config.WW_RANGE[0], config.WW_RANGE[1], ww_default, key=f"ww_{preset}"
    )
    wl = st.sidebar.slider(
        t("wl_label", lang), config.WL_RANGE[0], config.WL_RANGE[1], wl_default, key=f"wl_{preset}"
    )
    invert = st.sidebar.checkbox(t("invert_label", lang), value=False, key="invert")
    return ww, wl, invert


def sidebar_slice_control(lang: str, n_frames: int) -> int:
    """切片导航侧边栏控件，返回当前帧索引（单帧图像返回 0）。"""
    if n_frames <= 1:
        return 0
    st.sidebar.subheader(t("slice_header", lang))
    idx = st.sidebar.slider(t("slice_label", lang), 0, n_frames - 1, 0, key="slice_index")
    st.sidebar.caption(t("frame_indicator", lang, current=idx + 1, total=n_frames))
    return idx


def sidebar_enhancement(lang: str) -> dict:
    """图像增强侧边栏控件，返回参数字典。"""
    st.sidebar.subheader(t("enhancement_header", lang))
    clahe_on = st.sidebar.checkbox(t("clahe_label", lang), value=True)
    clip = st.sidebar.slider(
        t("clahe_clip_label", lang), 0.0, 10.0, config.DEFAULT_CLAHE_CLIP, 0.5, key="clip"
    )
    gamma_on = st.sidebar.checkbox(t("gamma_label", lang), value=False)
    gamma_v = st.sidebar.slider(
        t("gamma_value_label", lang), 0.2, 3.0, config.DEFAULT_GAMMA, 0.1, key="gamma"
    )
    sharpen_on = st.sidebar.checkbox(t("sharpen_label", lang), value=False)
    strength = st.sidebar.slider(
        t("sharpen_strength_label", lang), 0.0, 5.0, config.DEFAULT_SHARPEN_STRENGTH, 0.1, key="sharpen"
    )
    return {
        "clahe_on": clahe_on, "clip": clip,
        "gamma_on": gamma_on, "gamma": gamma_v,
        "sharpen_on": sharpen_on, "strength": strength,
    }


def sidebar_colormap(lang: str) -> str:
    """伪彩色选择。"""
    st.sidebar.subheader(t("colormap_header", lang))
    return st.sidebar.selectbox(
        t("colormap_label", lang),
        options=config.COLORMAPS,
        format_func=lambda c: t(f"cmap_{c}", lang),
        index=0,
        key="cmap",
    )


def render_metadata(ds, lang: str, show_sensitive: bool) -> None:
    """渲染影像元数据面板（表格形式）。"""
    meta = dicom_loader.get_metadata(ds)

    def show(value):
        """缺失值统一显示为 —。"""
        return value if value not in (None, "") else "—"

    patient_name = meta["PatientName"] if (show_sensitive and meta["PatientName"]) else t("anonymized", lang)
    patient_id = meta["PatientID"] if (show_sensitive and meta["PatientID"]) else t("anonymized", lang)

    spacing = meta["PixelSpacing"]
    spacing_str = f"{spacing[0]:.2f} × {spacing[1]:.2f} mm" if spacing else "—"
    size_str = f"{meta['Rows']} × {meta['Columns']}" if meta["Rows"] else "—"

    rows = [
        (t("meta_patient_name", lang), patient_name),
        (t("meta_patient_id", lang), patient_id),
        (t("meta_modality", lang), show(meta["Modality"])),
        (t("meta_study_date", lang), show(meta["StudyDate"])),
        (t("meta_series_desc", lang), show(meta["SeriesDescription"])),
        (t("meta_rows_cols", lang), size_str),
        (t("meta_frames", lang), show(meta["NumberOfFrames"])),
        (t("meta_pixel_spacing", lang), spacing_str),
        (t("meta_slice_thickness", lang), show(meta["SliceThickness"])),
        (t("meta_window_width", lang), show(meta["WindowWidth"])),
        (t("meta_window_center", lang), show(meta["WindowCenter"])),
        (t("meta_rescale_slope", lang), show(meta["RescaleSlope"])),
        (t("meta_rescale_intercept", lang), show(meta["RescaleIntercept"])),
        (t("meta_manufacturer", lang), show(meta["Manufacturer"])),
        (t("meta_bits", lang), show(meta["BitsAllocated"])),
    ]
    st.markdown("|  |  |\n|---|---|")
    for key, value in rows:
        st.markdown(f"| **{key}** | `{value}` |")


def render_histogram(hu: np.ndarray, ww: int, wl: int, lang: str) -> None:
    """渲染当前窗宽窗位下的灰度直方图。"""
    low = wl - ww / 2.0
    high = wl + ww / 2.0
    counts, edges = np.histogram(hu.ravel(), bins=64, range=(low, high))
    centers = (edges[:-1] + edges[1:]) / 2.0
    df = pd.DataFrame({t("histogram_x", lang): centers, t("histogram_y", lang): counts})
    st.bar_chart(df, x=t("histogram_x", lang), y=t("histogram_y", lang), height=220)


def render_roi_table(shapes, hu: np.ndarray, spacing, lang: str) -> None:
    """渲染 ROI 统计表。"""
    st.subheader(t("roi_header", lang))
    if not shapes:
        st.info(t("roi_empty", lang))
        return

    rows = []
    for i, shape in enumerate(shapes, 1):
        stats = annotation.roi_stats(hu, shape, spacing)
        if stats is None:
            continue
        row = {
            t("roi_index", lang): i,
            t("roi_mean", lang): round(stats["mean"], 1),
            t("roi_std", lang): round(stats["std"], 1),
            t("roi_min", lang): round(stats["min"], 1),
            t("roi_max", lang): round(stats["max"], 1),
        }
        if "width_mm" in stats:
            row[t("roi_width_mm", lang)] = round(stats["width_mm"], 1)
            row[t("roi_height_mm", lang)] = round(stats["height_mm"], 1)
        if "diameter_mm" in stats:
            row[t("roi_diameter_mm", lang)] = round(stats["diameter_mm"], 1)
        rows.append(row)

    if not rows:
        st.info(t("roi_empty", lang))
        return

    st.dataframe(pd.DataFrame(rows), hide_index=True)
    if spacing is None:
        st.caption(t("roi_no_spacing", lang))


def render_point_readout(points, hu: np.ndarray, lang: str) -> None:
    """渲染点标注的 HU 读数表。"""
    st.subheader(t("point_header", lang))
    if not points:
        st.caption(t("point_empty", lang))
        return

    rows = []
    for i, p in enumerate(points, 1):
        val = annotation.point_hu(hu, p)
        if val is None:
            continue
        rows.append({
            t("roi_index", lang): i,
            t("point_coord", lang): f"({val['x']}, {val['y']})",
            t("point_value", lang): round(val["hu"], 1),
        })

    if not rows:
        st.caption(t("point_empty", lang))
        return
    st.dataframe(pd.DataFrame(rows), hide_index=True)
