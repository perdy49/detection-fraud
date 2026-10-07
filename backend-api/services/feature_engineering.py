import numpy as np
import pandas as pd


def _normalise_key(value):
    """Normalise numeric/string group keys so CSV and training values match."""
    if pd.isna(value):
        return None

    if isinstance(value, (int, np.integer)):
        return str(int(value))

    if isinstance(value, (float, np.floating)):
        if np.isfinite(value) and float(value).is_integer():
            return str(int(value))

    return str(value).strip().lower()


def build_reference_stats(df):
    """
    Build statistics from the TRAINING dataset only.

    These statistics are used during inference so aggregate features
    such as card1_frequency and card1_amt_mean do not get recalculated
    from the uploaded CSV itself.
    """
    source = df.copy()

    if "TransactionAmt" in source.columns:
        source["TransactionAmt"] = pd.to_numeric(
            source["TransactionAmt"],
            errors="coerce",
        )

    stats = {
        "card1_frequency": {},
        "card1_amt_mean": {},
        "addr1_amt_mean": {},
    }

    if "card1" in source.columns:
        frequency = source["card1"].value_counts(dropna=True)

        stats["card1_frequency"] = {
            _normalise_key(key): int(value)
            for key, value in frequency.items()
            if _normalise_key(key) is not None
        }

    if "card1" in source.columns and "TransactionAmt" in source.columns:
        card_mean = (
            source.groupby("card1")["TransactionAmt"]
            .mean()
            .dropna()
        )

        stats["card1_amt_mean"] = {
            _normalise_key(key): float(value)
            for key, value in card_mean.items()
            if _normalise_key(key) is not None
        }

    if "addr1" in source.columns and "TransactionAmt" in source.columns:
        addr_mean = (
            source.groupby("addr1")["TransactionAmt"]
            .mean()
            .dropna()
        )

        stats["addr1_amt_mean"] = {
            _normalise_key(key): float(value)
            for key, value in addr_mean.items()
            if _normalise_key(key) is not None
        }

    return stats


def create_features(df, reference_stats=None):
    """
    Feature engineering shared by training-compatible preprocessing
    and CSV inference.

    reference_stats:
        None  -> calculate aggregate features from the current dataframe.
        dict  -> use statistics learned from the training dataset.
    """
    df = df.copy()

    # =========================================================
    # TRANSACTION AMOUNT
    # =========================================================

    if "TransactionAmt" in df.columns:
        df["TransactionAmt"] = pd.to_numeric(
            df["TransactionAmt"],
            errors="coerce",
        )

        df["amount_log"] = np.log1p(df["TransactionAmt"])

    # =========================================================
    # EMAIL MATCH
    # =========================================================

    if "P_emaildomain" in df.columns and "R_emaildomain" in df.columns:
        df["email_match"] = (
            df["P_emaildomain"] == df["R_emaildomain"]
        ).astype(int)

    # =========================================================
    # CARD FREQUENCY
    # =========================================================

    if "card1" in df.columns:
        if reference_stats is None:
            card_freq = df["card1"].value_counts(dropna=True)
            df["card1_frequency"] = df["card1"].map(card_freq)
        else:
            frequency_map = reference_stats.get(
                "card1_frequency",
                {},
            )

            df["card1_frequency"] = df["card1"].map(
                lambda value: (
                    frequency_map.get(
                        _normalise_key(value),
                        0,
                    )
                    if _normalise_key(value) is not None
                    else 0
                )
            )

    # =========================================================
    # CARD AVERAGE AMOUNT
    # =========================================================

    if "TransactionAmt" in df.columns and "card1" in df.columns:
        if reference_stats is None:
            df["card1_amt_mean"] = (
                df.groupby("card1")["TransactionAmt"]
                .transform("mean")
            )
        else:
            mean_map = reference_stats.get(
                "card1_amt_mean",
                {},
            )

            df["card1_amt_mean"] = df["card1"].map(
                lambda value: (
                    mean_map.get(
                        _normalise_key(value),
                        0.0,
                    )
                    if _normalise_key(value) is not None
                    else 0.0
                )
            )

    # =========================================================
    # ADDRESS AVERAGE AMOUNT
    # =========================================================

    if "TransactionAmt" in df.columns and "addr1" in df.columns:
        if reference_stats is None:
            df["addr1_amt_mean"] = (
                df.groupby("addr1")["TransactionAmt"]
                .transform("mean")
            )
        else:
            mean_map = reference_stats.get(
                "addr1_amt_mean",
                {},
            )

            df["addr1_amt_mean"] = df["addr1"].map(
                lambda value: (
                    mean_map.get(
                        _normalise_key(value),
                        0.0,
                    )
                    if _normalise_key(value) is not None
                    else 0.0
                )
            )

    # =========================================================
    # ADDRESS MATCH
    # =========================================================

    if "addr1" in df.columns and "addr2" in df.columns:
        df["addr_match"] = (
            df["addr1"].astype(str)
            + "_"
            + df["addr2"].astype(str)
        )

    # =========================================================
    # TRANSACTION TIME
    # =========================================================

    if "TransactionDT" in df.columns:
        df["TransactionDT"] = pd.to_numeric(
            df["TransactionDT"],
            errors="coerce",
        )

        df["transaction_hour"] = (
            (df["TransactionDT"] // 3600) % 24
        )

        df["is_night_transaction"] = (
            (df["transaction_hour"] <= 5)
            | (df["transaction_hour"] >= 23)
        ).astype(int)

    # =========================================================
    # MISSING COUNT
    # =========================================================

    df["missing_count"] = df.isna().sum(axis=1)

    # =========================================================
    # C FEATURES
    # =========================================================

    c_cols = [
        col
        for col in df.columns
        if col.startswith("C")
    ]

    if c_cols:
        df[c_cols] = df[c_cols].apply(
            pd.to_numeric,
            errors="coerce",
        )

        df["C_sum"] = df[c_cols].sum(axis=1)

    # =========================================================
    # D FEATURES
    # =========================================================

    d_cols = [
        col
        for col in df.columns
        if col.startswith("D")
    ]

    if d_cols:
        df[d_cols] = df[d_cols].apply(
            pd.to_numeric,
            errors="coerce",
        )

        df["D_sum"] = df[d_cols].sum(axis=1)

    # =========================================================
    # V FEATURES
    # =========================================================

    v_cols = [
        col
        for col in df.columns
        if col.startswith("V")
    ]

    if v_cols:
        # Do not calculate df[v_cols].mean(axis=1) in one operation here.
        # IEEE-CIS contains hundreds of V columns, and selecting all of them
        # at once can create a multi-GB temporary NumPy array on machines with
        # limited RAM. Process one column at a time instead; the result is the
        # same row-wise mean while using only a few MB of temporary memory.
        v_sum = np.zeros(len(df), dtype=np.float64)
        v_count = np.zeros(len(df), dtype=np.int32)

        for col in v_cols:
            values = pd.to_numeric(
                df[col],
                errors="coerce",
            ).to_numpy(dtype=np.float64, na_value=np.nan)

            valid = np.isfinite(values)
            v_sum[valid] += values[valid]
            v_count[valid] += 1

        df["V_mean"] = np.divide(
            v_sum,
            v_count,
            out=np.zeros(len(df), dtype=np.float64),
            where=v_count > 0,
        )

    # =========================================================
    # INFINITY
    # =========================================================

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True,
    )

    # =========================================================
    # TRAINING-COMPATIBLE MISSING VALUE HANDLING
    # =========================================================
    #
    # The existing trained model was trained with:
    #   numeric     -> 0
    #   categorical -> "0"
    #
    # Keep this representation so the current scaler/model remain
    # compatible. Inference uses the saved categorical defaults for
    # categorical values that were never seen because the training
    # dataset itself did not contain that missing category.
    # =========================================================

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("0")

    return df
