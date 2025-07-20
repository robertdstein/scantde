import pandas as pd
from tdescore.combine.parse import combine_all_sources


def tag_junk(df) -> list[bool]:
    full_df = combine_all_sources(df, save=False)

    infant_class_mask = full_df["tdescore_best"].isin(["infant", "week", "month"])
    old_infant_mask = infant_class_mask & (full_df["age"] > 30.0)

    alt_age = df["jdendhist"] - df["jdstarthist"]

    # Select AGN that flare again after many past detections
    jd_infant_mask = infant_class_mask & (alt_age > 60.0) & (df["ndethist"] > 50)

    high_noise_mask = full_df["tdescore_high_noise"]
    low_score_mask = full_df["tdescore"] < 0.01

    lc_score_mask = (full_df["tdescore_lc_score"] < 0.1) & (
        full_df["tdescore_best"].isin(
            ["thermal_None", "thermal_365.0", "thermal_180.0"])
    )

    old_mask = (full_df["age"] > 500.0) & (full_df["tdescore"] < 0.5)

    ancient_mask = (full_df["age"] > 1000.0)

    mask = old_infant_mask | jd_infant_mask | high_noise_mask | low_score_mask | lc_score_mask | old_mask | ancient_mask

    return mask
