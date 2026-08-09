# src/refinement/text_normalization.py
#
# Text cleanup for categorical/string fields before comparison or storage:
# accent stripping, case folding, whitespace/regex cleanup. This is what
# makes "Bogotá" / "BOGOTA" / "bogota d.c." / "Bogota D.C." comparable.
#
# Implement:
#
# strip_accents(text: str) -> str
#   - unicodedata.normalize("NFKD", text), then drop combining marks
#     (unicodedata.combining(ch) != 0).
#
# normalize_whitespace(text: str) -> str
#   - Collapse repeated whitespace (regex \s+ -> " "), strip leading/trailing.
#
# normalize_categorical(text: str) -> str
#   - Compose strip_accents + casefold + normalize_whitespace + a regex
#     cleanup pass (e.g. strip trailing "d.c."/punctuation, normalize
#     separators) into one canonical form suitable for grouping/joining.
#   - Document the exact rule set here in comments as you build it — these
#     are the "business rules" the README asks you to make explicit, and
#     src.refinement.deduplication depends on this being deterministic.
#
# normalize_column(df: pd.DataFrame, column: str, new_column: str | None = None) -> pd.DataFrame
#   - Vectorized application (df[column].map(normalize_categorical), or a
#     .str accessor chain if you can express the whole rule set that way)
#     producing either an in-place normalized column or a new "_normalized"
#     column. Decide which and be consistent — deduplication.py will
#     depend on the choice.
