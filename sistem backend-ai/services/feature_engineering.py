import pandas as pd
import numpy as np


def create_features(df):
    # =========================
    # COPY DATAFRAME
    # =========================
    df = df.copy()

    # =========================
    # LOG AMOUNT
    # =========================
    if "TransactionAmt" in df.columns:
        df["TransactionAmt"] = pd.to_numeric(
            df["TransactionAmt"],
            errors="coerce"
        )

        df["amount_log"] = np.log1p(
            df["TransactionAmt"]
        )

    # =========================
    # EMAIL MATCH
    # =========================
    if (
        "P_emaildomain" in df.columns and
        "R_emaildomain" in df.columns
    ):
        df["email_match"] = (
            df["P_emaildomain"] ==
            df["R_emaildomain"]
        ).astype(int)

     # =========================
    # CARD FREQUENCY
    # =========================
    if "card1" in df.columns:
        card_freq = df["card1"].value_counts()

        df["card1_frequency"] = df["card1"].map(
            card_freq
        )

    # =========================
    # CARD AVG AMOUNT
    # =========================
    if (
        "TransactionAmt" in df.columns and
        "card1" in df.columns
    ):
        df["card1_amt_mean"] = (
            df.groupby("card1")["TransactionAmt"]
            .transform("mean")
        )

    # =========================
    # ADDRESS AVG AMOUNT
    # =========================
    if (
        "TransactionAmt" in df.columns and
        "addr1" in df.columns
    ):
        df["addr1_amt_mean"] = (
            df.groupby("addr1")["TransactionAmt"]
            .transform("mean")
        )

    # =========================
    # ADDRESS MATCH
    # =========================
    if (
        "addr1" in df.columns and
        "addr2" in df.columns
    ):
        df["addr_match"] = (
            df["addr1"].astype(str) +
            "_" +
            df["addr2"].astype(str)
        )

    # =========================
    # TEMPORAL HOUR BUCKET
    # =========================
    if "TransactionDT" in df.columns:
        df["TransactionDT"] = pd.to_numeric(
            df["TransactionDT"],
            errors="coerce"
        )

        df["transaction_hour"] = (
            (df["TransactionDT"] // 3600) % 24
        )

        df["is_night_transaction"] = (
            (
                (df["transaction_hour"] <= 5) |
                (df["transaction_hour"] >= 23)
            )
        ).astype(int)

    # =========================
    # MISSING VALUE COUNT
    # =========================
    df["missing_count"] = df.isnull().sum(axis=1)

    # =========================
    # C FEATURE AGGREGATION
    # =========================
    c_cols = [
        col for col in df.columns
        if col.startswith("C")
    ]

    if len(c_cols) > 0:
        df[c_cols] = df[c_cols].apply(
            pd.to_numeric,
            errors="coerce"
        )

        df["C_sum"] = df[c_cols].sum(axis=1)

    # =========================
    # D FEATURE AGGREGATION
    # =========================
    d_cols = [
        col for col in df.columns
        if col.startswith("D")
    ]

    if len(d_cols) > 0:
        df[d_cols] = df[d_cols].apply(
            pd.to_numeric,
            errors="coerce"
        )

        df["D_sum"] = df[d_cols].sum(axis=1)

    # =========================
    # V FEATURE AGGREGATION
    # =========================
    v_cols = [
        col for col in df.columns
        if col.startswith("V")
    ]

    if len(v_cols) > 0:
        df[v_cols] = df[v_cols].apply(
            pd.to_numeric,
            errors="coerce"
        )

        df["V_mean"] = df[v_cols].mean(axis=1)

    # =========================
    # HANDLE INF
    # =========================
    df.replace(
        [np.inf, -np.inf],
        0,
        inplace=True
    )

    # =========================
    # FILL NAN SAFE
    # =========================
    df.fillna(0, inplace=True)

    return df