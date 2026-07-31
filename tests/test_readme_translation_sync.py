from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRANSLATED_READMES = {
    "README_DE.md": ("## Hinweise zur Interpretation", "## Vorverarbeitung", "## Phänotypische Ähnlichkeit"),
    "README_ES.md": ("## Notas de interpretación", "## Preprocesamiento", "## Similitud fenotípica"),
    "README_FR.md": ("## Notes d’interprétation", "## Prétraitement", "## Similarité phénotypique"),
    "README_HI.md": ("## व्याख्या संबंधी नोट्स", "## प्रीप्रोसेसिंग", "## Phenotypic similarity"),
    "README_ID.md": ("## Catatan interpretasi", "## Pra-pemrosesan", "## Kesamaan fenotipe"),
    "README_KR.md": ("## 해석 시 주의사항", "## 전처리", "## 표현형 유사도"),
    "README_PT.md": ("## Notas de interpretação", "## Pré-processamento", "## Similaridade fenotípica"),
    "README_VN.md": ("## Lưu ý diễn giải", "## Tiền xử lý", "## Độ tương đồng kiểu hình"),
    "README_ZH_CN.md": ("## 解读注意事项", "## 预处理", "## 表型相似度"),
    "README_ZH_TW.md": ("## 解讀注意事項", "## 前處理", "## 表現型相似度"),
}

INTERPRETATION_TOKENS = (
    "`phenotype_shared_annotations`",
    "MICA",
    "0–100",
    "1–100",
    "`log1p`",
    "`Similarity`",
    "`Top-level MP`",
    "`Female`",
    "`Male`",
    "IMPC Disease Models Portal",
    "`disease_annotation`",
    "`null`",
)

PREPROCESSING_TOKENS = (
    "`mp_term_id`",
    "`Homo`",
    "`Hetero`",
    "`Hemi`",
    "`female_ko_effect_p_value`",
    "`male_ko_effect_p_value`",
    "`Female`",
    "`Male`",
    "`None`",
    "`null`",
)


def test_translated_readmes_include_all_interpretation_topics() -> None:
    for filename, (interpretation_heading, _, _) in TRANSLATED_READMES.items():
        path = PROJECT_ROOT / "doc" / filename
        text = path.read_text(encoding="utf-8")
        start = text.index(interpretation_heading)
        end = text.index("# 🌐", start)
        interpretation = text[start:end]

        assert interpretation.count("\n- **") == 10, f"{filename}: incomplete interpretation topic list"
        for token in INTERPRETATION_TOKENS:
            assert token in interpretation, f"{filename}: missing interpretation token {token}"


def test_translated_readmes_use_current_preprocessing_semantics() -> None:
    for filename, (_, preprocessing_heading, similarity_heading) in TRANSLATED_READMES.items():
        path = PROJECT_ROOT / "doc" / filename
        text = path.read_text(encoding="utf-8")
        start = text.index(preprocessing_heading)
        end = text.index(similarity_heading, start)
        preprocessing = text[start:end]

        for token in PREPROCESSING_TOKENS:
            assert token in preprocessing, f"{filename}: missing preprocessing token {token}"
