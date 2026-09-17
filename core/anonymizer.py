"""DICOM 脱敏（去标识化）。

用于在演示 / 分享前生成脱敏副本，符合医学影像数据的隐私要求。
"""

from __future__ import annotations

import copy

import pydicom
from pydicom.dataset import Dataset

# 需要清除的敏感标签（患者信息 / 机构信息 / 可关联身份的信息）
SENSITIVE_TAGS: list[str] = [
    "PatientName", "PatientID", "PatientBirthDate", "PatientBirthTime",
    "PatientSex", "PatientAge", "PatientAddress", "PatientTelephoneNumbers",
    "PatientMotherBirthName", "OtherPatientIDs", "OtherPatientNames",
    "AccessionNumber", "StudyID", "StudyInstanceUID", "SeriesInstanceUID",
    "SOPInstanceUID", "InstitutionName", "InstitutionAddress",
    "ReferringPhysicianName", "PerformingPhysicianName", "PhysiciansOfRecord",
    "OperatorsName", "DeviceSerialNumber", "StationName",
]

# 用固定占位值覆盖的标签（避免某些工具因字段为空报错）
REPLACE_VALUES: dict[str, str] = {
    "PatientName": "Anonymous^Patient",
    "PatientID": "ANONYMOUS",
    "AccessionNumber": "ANONYMOUS",
    "StudyInstanceUID": "1.2.826.0.1.3680043.10.99.1",
    "SeriesInstanceUID": "1.2.826.0.1.3680043.10.99.2",
    "SOPInstanceUID": "1.2.826.0.1.3680043.10.99.3",
}


def anonymize(ds: Dataset) -> Dataset:
    """返回脱敏后的数据集副本（不修改原对象）。"""
    ds_clean = copy.deepcopy(ds)
    for tag in SENSITIVE_TAGS:
        if tag in ds_clean:
            if tag in REPLACE_VALUES:
                ds_clean.data_element(tag).value = REPLACE_VALUES[tag]
            else:
                del ds_clean[tag]
    ds_clean.PatientIdentityRemoved = "YES"
    ds_clean.DeidentificationMethod = "LungWindow anonymizer"
    return ds_clean


def anonymize_file(src: str, dst: str) -> None:
    """读取 DICOM 文件并写出脱敏副本。"""
    ds = pydicom.dcmread(src)
    ds_clean = anonymize(ds)
    ds_clean.save_as(dst)
