from tdescore.combine.parse import combine_all_sources


def tag_junk(df) -> list[bool]:
    full_df = combine_all_sources(df, save=False)

    infant_class_mask = full_df["tdescore_best"].isin(["infant", "week", "month"])
    old_infant_mask = infant_class_mask & (full_df["age"] > 30.0)

    # alt_infant_mask = ((df["jd"] - df["jdstarthist"]) > 30.0) & infant_class_mask

    # Select AGN that flare again after many past detections
    high_noise_mask = full_df["tdescore_high_noise"]

    # If there are a lot of old detections, we consider it junk
    # More than 20, and more than the number of thermal detections
    predet_mask = (df["n_predets"] > 20.) & (
            df["n_predets"] > df["thermal_n_detections"]
    )

    lc_mask_180 = (full_df["thermal_score"] < 0.1) & (
        full_df["tdescore_best"].isin(
            ["thermal_180"])
    )

    lc_score_old = (full_df["thermal_score"] < 0.5) & (
        full_df["tdescore_best"].isin(
            ["thermal_all", "thermal_365", "thermal_180"])
    )

    old_mask = (full_df["age"] > 365.0) & (full_df["tdescore"] < 0.5) & (full_df["thermal_score"] < 0.5)

    ancient_mask = (full_df["age"] > 1000.0)

    mask = old_infant_mask | high_noise_mask | lc_mask_180 | lc_score_old | old_mask | ancient_mask | predet_mask

    return mask
