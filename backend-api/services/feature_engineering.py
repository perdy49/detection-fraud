import numpy as np
import pandas as pd


def create_features(df):
    """
    Feature engineering yang kompatibel dengan pipeline training.

    Catatan:
    - Tidak mengubah model.
    - Tidak melakukan encoding categorical.
    - Missing value categorical dipertahankan sebagai string "0"
      agar kompatibel dengan perilaku pipeline training lama.
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
        df["email_match"] = (df["P_emaildomain"] == df["R_emaildomain"]).astype(int)

    # =========================================================
    # CARD FREQUENCY
    # =========================================================

    if "card1" in df.columns:
        card_freq = df["card1"].value_counts()

        df["card1_frequency"] = df["card1"].map(card_freq)

    # =========================================================
    # CARD AVERAGE AMOUNT
    # =========================================================

    if "TransactionAmt" in df.columns and "card1" in df.columns:
        df["card1_amt_mean"] = df.groupby("card1")["TransactionAmt"].transform("mean")

    # =========================================================
    # ADDRESS AVERAGE AMOUNT
    # =========================================================

    if "TransactionAmt" in df.columns and "addr1" in df.columns:
        df["addr1_amt_mean"] = df.groupby("addr1")["TransactionAmt"].transform("mean")

    # =========================================================
    # ADDRESS MATCH
    # =========================================================

    if "addr1" in df.columns and "addr2" in df.columns:
        df["addr_match"] = df["addr1"].astype(str) + "_" + df["addr2"].astype(str)

    # =========================================================
    # TRANSACTION TIME
    # =========================================================

    if "TransactionDT" in df.columns:
        df["TransactionDT"] = pd.to_numeric(
            df["TransactionDT"],
            errors="coerce",
        )

        df["transaction_hour"] = (df["TransactionDT"] // 3600) % 24

        df["is_night_transaction"] = (
            (df["transaction_hour"] <= 5) | (df["transaction_hour"] >= 23)
        ).astype(int)

    # =========================================================
    # MISSING COUNT
    # =========================================================

    df["missing_count"] = df.isna().sum(axis=1)

    # =========================================================
    # C FEATURES
    # =========================================================

    c_cols = [col for col in df.columns if col.startswith("C")]

    if c_cols:
        df[c_cols] = df[c_cols].apply(
            pd.to_numeric,
            errors="coerce",
        )

        df["C_sum"] = df[c_cols].sum(axis=1)

    # =========================================================
    # D FEATURES
    # =========================================================

    d_cols = [col for col in df.columns if col.startswith("D")]

    if d_cols:
        df[d_cols] = df[d_cols].apply(
            pd.to_numeric,
            errors="coerce",
        )

        df["D_sum"] = df[d_cols].sum(axis=1)

    # =========================================================
    # V FEATURES
    # =========================================================

    v_cols = [col for col in df.columns if col.startswith("V")]

    if v_cols:
        df[v_cols] = df[v_cols].apply(
            pd.to_numeric,
            errors="coerce",
        )

        df["V_mean"] = df[v_cols].mean(axis=1)

    # =========================================================
    # INFINITY
    # =========================================================

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True,
    )

    # =========================================================
    # MISSING VALUE
    # =========================================================
    #
    # Training lama:
    #
    #     df.fillna(0)
    #
    # Pada pandas baru, integer 0 tidak boleh dipaksakan
    # ke dtype string.
    #
    # Jadi hasil akhirnya dibuat:
    #
    # numeric -> 0
    # categorical/string -> "0"
    #
    # Ini mempertahankan representasi yang digunakan
    # pipeline training tanpa memicu error pandas.
    # =========================================================

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("0")

    return df
