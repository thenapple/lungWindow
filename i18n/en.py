"""English strings."""

STRINGS: dict[str, str] = {
    # App title
    "app_title": "DICOM Lung Window Image Tool",
    "app_subtitle": "Read · Window/Level · Enhance · Annotate · Export",

    # Upload
    "upload_file": "Upload DICOM file",
    "upload_hint": "Supports .dcm CT images. Files are processed locally and never uploaded.",
    "no_file": "Please upload a DICOM file first.",

    # Metadata
    "metadata_header": "Image Metadata",
    "show_patient_info": "Show full patient info (sensitive fields)",
    "privacy_note": "For privacy, patient name / ID are anonymized by default. The exported PNG is a plain image with no patient metadata.",
    "anonymized": "Anonymized",

    "meta_patient_name": "Patient Name",
    "meta_patient_id": "Patient ID",
    "meta_modality": "Modality",
    "meta_study_date": "Study Date",
    "meta_series_desc": "Series Description",
    "meta_rows_cols": "Image Size",
    "meta_frames": "Frames",
    "meta_pixel_spacing": "Pixel Spacing",
    "meta_slice_thickness": "Slice Thickness",
    "meta_window_center": "Window Center (WL)",
    "meta_window_width": "Window Width (WW)",
    "meta_rescale_slope": "Rescale Slope",
    "meta_rescale_intercept": "Rescale Intercept",
    "meta_manufacturer": "Manufacturer",
    "meta_bits": "Bits Allocated",

    # Slice navigation
    "slice_header": "Slice Navigation",
    "slice_label": "Slice",
    "frame_indicator": "Frame {current} / {total}",

    # Window / level
    "window_header": "Window / Level",
    "preset_label": "Preset",
    "preset_auto": "Auto (from DICOM)",
    "preset_lung": "Lung (1500 / -600)",
    "preset_mediastinal": "Mediastinal (400 / 40)",
    "preset_bone": "Bone (2000 / 350)",
    "preset_brain": "Brain (80 / 40)",
    "preset_custom": "Custom",
    "ww_label": "Window Width (WW)",
    "wl_label": "Window Level (WL)",
    "invert_label": "Invert",

    # Enhancement
    "enhancement_header": "Enhancement",
    "clahe_label": "CLAHE equalization",
    "clahe_clip_label": "CLAHE clip limit",
    "gamma_label": "Gamma correction",
    "gamma_value_label": "Gamma value",
    "sharpen_label": "Sharpen",
    "sharpen_strength_label": "Sharpen strength",

    # Pseudocolor
    "colormap_header": "Pseudocolor",
    "colormap_label": "Colormap",
    "cmap_gray": "Grayscale",
    "cmap_jet": "Jet",
    "cmap_hot": "Hot",
    "cmap_bone": "Bone",
    "cmap_inferno": "Inferno",
    "cmap_viridis": "Viridis",

    # Histogram
    "histogram_header": "Histogram",
    "histogram_show": "Show histogram in the current window",
    "histogram_x": "HU value",
    "histogram_y": "Pixel count",

    # Annotation
    "annotation_header": "Lesion Annotation",
    "drawing_mode_label": "Drawing tool",
    "mode_rect": "Rectangle",
    "mode_circle": "Circle",
    "mode_point": "Point (readout)",
    "mode_transform": "Select / Move",
    "annotation_hint": "Drag to draw the lesion region and read the ROI stats below; pick Point then click to read HU at that pixel.",

    # Cursor HU readout
    "point_header": "Cursor HU Readout",
    "point_coord": "Coord (px)",
    "point_value": "HU value",
    "point_empty": "No point yet. Pick the Point tool and click on the image.",

    # ROI statistics
    "roi_header": "ROI Statistics",
    "roi_empty": "No annotation yet. Draw a region on the image.",
    "roi_index": "Region",
    "roi_mean": "Mean HU",
    "roi_std": "Std Dev",
    "roi_min": "Min HU",
    "roi_max": "Max HU",
    "roi_width_mm": "Width (mm)",
    "roi_height_mm": "Height (mm)",
    "roi_diameter_mm": "Diameter (mm)",
    "roi_no_spacing": "Pixel spacing unavailable, cannot compute mm size.",

    # Export
    "export_header": "Export",
    "export_button": "Download PNG",
    "export_hint": "Exports the current preview (window/level, enhancement and annotation overlay).",
    "export_filename": "lungwindow",

    # Errors
    "error_invalid": "Cannot parse this file. Please check it is a valid DICOM file.",
    "error_no_pixel": "This DICOM file has no pixel data.",
    "error_not_ct": "This file is not a CT image (Modality: {}). Window/level presets are designed for CT.",
}
