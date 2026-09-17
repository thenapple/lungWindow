"""Streamlit 主入口。

运行方式：
    streamlit run app.py
"""

from __future__ import annotations

import cv2
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

from core import annotation, dicom_loader, enhancement, exporter, windowing
from i18n import t
from ui import components
from utils import validators

st.set_page_config(page_title="LungWindow", page_icon="🫁", layout="wide")


def main() -> None:
    lang = components.language_selector()

    st.title(t("app_title", lang))
    st.caption(t("app_subtitle", lang))

    # ---- 1. 上传文件 ----
    uploaded = st.file_uploader(t("upload_file", lang), type=["dcm", "dicom"])
    if uploaded is None:
        st.info(t("no_file", lang))
        st.caption(t("upload_hint", lang))
        return

    # ---- 2. 读取与校验 ----
    try:
        ds = dicom_loader.load_dicom(uploaded.getvalue())
    except Exception:
        st.error(t("error_invalid", lang))
        return

    if not validators.has_pixel_data(ds):
        st.error(t("error_no_pixel", lang))
        return
    if not validators.is_ct(ds):
        modality = str(getattr(ds, "Modality", "?"))
        st.warning(t("error_not_ct", lang, modality=modality))

    # ---- 3. 帧数 / 切片导航 ----
    n_frames = dicom_loader.get_frame_count(ds)
    frame_index = components.sidebar_slice_control(lang, n_frames)

    # ---- 4. 像素 -> HU ----
    pixel = dicom_loader.get_pixel_array(ds, frame_index)
    hu = dicom_loader.to_hu(ds, pixel)
    spacing = dicom_loader.get_pixel_spacing(ds)
    dicom_window = dicom_loader.get_window(ds)

    # ---- 5. 侧边栏参数 ----
    ww, wl, invert = components.sidebar_window_controls(lang, dicom_window)
    enh = components.sidebar_enhancement(lang)
    cmap = components.sidebar_colormap(lang)

    # ---- 6. 处理流水线：窗位 -> 增强 -> 伪彩色 ----
    gray = windowing.apply_window(hu, ww, wl, invert)
    if enh["clahe_on"]:
        gray = enhancement.clahe(gray, enh["clip"])
    if enh["gamma_on"]:
        gray = enhancement.gamma_correct(gray, enh["gamma"])
    if enh["sharpen_on"]:
        gray = enhancement.sharpen(gray, enh["strength"])

    display_bgr = enhancement.apply_colormap(gray, cmap)
    display_rgb = cv2.cvtColor(display_bgr, cv2.COLOR_BGR2RGB)
    display_pil = Image.fromarray(display_rgb)

    # ---- 7. 布局：左图右信息 ----
    col_img, col_side = st.columns([3, 2])

    with col_side:
        st.subheader(t("metadata_header", lang))
        show_sensitive = st.checkbox(t("show_patient_info", lang), value=False)
        st.caption(t("privacy_note", lang))
        components.render_metadata(ds, lang, show_sensitive)

        st.divider()
        st.subheader(t("histogram_header", lang))
        if st.checkbox(t("histogram_show", lang), value=False):
            components.render_histogram(hu, ww, wl, lang)

        st.divider()
        st.subheader(t("annotation_header", lang))
        drawing_mode = st.radio(
            t("drawing_mode_label", lang),
            options=["rect", "circle", "point", "transform"],
            format_func=lambda m: t(f"mode_{m}", lang),
            horizontal=True,
        )
        st.caption(t("annotation_hint", lang))

    with col_img:
        # 标注画布：背景为当前处理结果，绘制坐标与像素 1:1 对应
        # key 含帧索引：切换切片时清空标注，避免跨切片残留
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.30)",
            stroke_width=2,
            stroke_color="#00ff00",
            background_image=display_pil,
            update_streamlit=True,
            height=display_pil.height,
            width=display_pil.width,
            drawing_mode=drawing_mode,
            key=f"annotation_canvas_{frame_index}",
        )
        shapes = annotation.extract_shapes(canvas_result.json_data if canvas_result else None)
        points = annotation.extract_points(canvas_result.json_data if canvas_result else None)

        # ROI 统计 + 光标 HU 读数
        components.render_roi_table(shapes, hu, spacing, lang)
        components.render_point_readout(points, hu, lang)

        # ---- 8. 导出（叠加标注后的 PNG） ----
        st.subheader(t("export_header", lang))
        annotated_bgr = annotation.draw_shapes(display_bgr, shapes)
        png_bytes = exporter.encode_png(cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB))
        st.download_button(
            t("export_button", lang),
            data=png_bytes,
            file_name=f"{t('export_filename', lang)}.png",
            mime="image/png",
        )
        st.caption(t("export_hint", lang))


if __name__ == "__main__":
    main()
