import pandas as pd

from scantde.log.model import ProcStage

def merge_processing_logs(
    logs: list[list[ProcStage]]
) -> list[ProcStage]:
    """
    Merge multiple processing logs into a single log.

    :param logs: List of lists of ProcStage objects
    :return: Merged list of ProcStage objects
    """

    dfs = [pd.DataFrame([x.model_dump() for x in log]) for log in logs]
    new = dfs[0]

    for df in dfs[1:]:
        new = new.merge(
            df,
            how="outer",
            on=["stage"]
        )
        new["n_sources"] = new["n_sources_x"].fillna(0) + new["n_sources_y"].fillna(0)
        new["tdes"] = [list(set(x["tdes_x"] + x["tdes_x"])) for _, x in new.iterrows()]
        new.sort_values(by=["n_sources"], ascending=False, inplace=True)
        new.drop(columns=["n_sources_x", "n_sources_y", "tdes_x", "tdes_y"], inplace=True)

    merged = [ProcStage(**row) for _, row in new.iterrows()]

    return merged
