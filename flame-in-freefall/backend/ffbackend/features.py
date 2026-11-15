import numpy as np, pandas as pd

def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    """Partial pressure of O2 (kPa) = O2% * total pressure / 100."""
    df = df.copy()
    if {"o2_pct", "pressure_kpa"} <= set(df.columns):
        df["ppo2_kpa"] = df["o2_pct"] * df["pressure_kpa"] / 100.0
    return df

def log_target(rate_mm_s):
    return np.log(np.asarray(rate_mm_s, float))

def exp_group_id(df: pd.DataFrame) -> pd.Series:
    """Unique experiment key across sources, used for GroupKFold."""
    return df["source"].astype(str) + "::" + df["experiment_id"].astype(str)
