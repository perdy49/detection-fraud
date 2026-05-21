import pandas as pd


def load_train_data(
    transaction_path,
    identity_path
):
    transaction_df = pd.read_csv(
        transaction_path
    )

    identity_df = pd.read_csv(
        identity_path
    )

    df = pd.merge(
        transaction_df,
        identity_df,
        on="TransactionID",
        how="left"
    )

    return df


def load_test_data(
    transaction_path,
    identity_path
):
    transaction_df = pd.read_csv(
        transaction_path
    )

    identity_df = pd.read_csv(
        identity_path
    )

    df = pd.merge(
        transaction_df,
        identity_df,
        on="TransactionID",
        how="left"
    )

    return df