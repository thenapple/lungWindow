"""国际化支持。

用法：
    from i18n import t
    t("app_title", lang="zh")
"""

from __future__ import annotations

from . import en, zh

# 语言代码 -> 文案字典
LANGS: dict[str, dict[str, str]] = {
    "zh": zh.STRINGS,
    "en": en.STRINGS,
}


def t(key: str, lang: str = "zh", **kwargs) -> str:
    """获取指定语言下的文案，支持 format 占位符。

    找不到 key 时原样返回 key，便于开发时发现遗漏。
    """
    strings = LANGS.get(lang, zh.STRINGS)
    text = strings.get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
