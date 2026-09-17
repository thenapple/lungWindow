# 测试数据

本项目不内置真实患者数据。推荐以下方式获取测试数据：

1. **使用自己的 DICOM 文件（注意脱敏）**
   将 CT 影像放入本目录前，请先执行脱敏：
   ```bash
   python scripts/anonymize.py ./raw_data ./sample_data
   ```

2. **公开数据集**（示例）
   - TCIA（The Cancer Imaging Archive）的 NSCLC-Radiomics 等公开 CT 数据集
   - 使用前请遵循相应数据集的许可协议

> 隐私提示：请勿将含患者身份信息的原始 DICOM 提交到公开仓库。
