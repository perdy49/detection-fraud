import joblib
import numpy as np
import pandas as pd

from services.feature_engineering import create_features


# =========================================================
# LOAD MODEL PREPROCESSING
# =========================================================

scaler = joblib.load(
    "model/scaler.pkl"
)

feature_names = joblib.load(
    "model/feature_names.pkl"
)


# =========================================================
# LABEL ENCODER COMPATIBILITY
# =========================================================
#
# Training menggunakan LabelEncoder().
#
# Karena encoder asli tidak disimpan oleh preprocess.py,
# kita gunakan kategori IEEE-CIS yang memang digunakan
# oleh dataset training.
#
# LabelEncoder mengurutkan kategori secara alfabetis.
# =========================================================

PRODUCT_CODES = [
    "C",
    "H",
    "R",
    "S",
    "W",
]

CARD_TYPES = [
    "american express",
    "discover",
    "mastercard",
    "visa",
]

P_EMAIL_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "anonymous.com",
    "aol.com",
    "comcast.net",
    "icloud.com",
    "outlook.com",
    "msn.com",
    "att.net",
    "live.com",
    "sbcglobal.net",
    "verizon.net",
    "ymail.com",
    "bellsouth.net",
    "yahoo.com.mx",
    "me.com",
    "cox.net",
    "optonline.net",
    "charter.net",
    "live.com.mx",
    "rocketmail.com",
    "mail.com",
    "earthlink.net",
    "gmail",
    "outlook.es",
    "mac.com",
    "juno.com",
    "aim.com",
    "hotmail.es",
    "roadrunner.com",
    "windstream.net",
    "hotmail.fr",
    "frontier.com",
    "embarqmail.com",
    "web.de",
    "netzero.com",
    "twc.com",
    "prodigy.net.mx",
    "centurylink.net",
    "netzero.net",
    "frontiernet.net",
    "q.com",
    "suddenlink.net",
    "cfl.rr.com",
    "sc.rr.com",
    "cableone.net",
    "gmx.de",
    "yahoo.fr",
    "yahoo.es",
    "hotmail.co.uk",
    "protonmail.com",
    "yahoo.de",
    "ptd.net",
    "live.fr",
    "yahoo.co.uk",
    "hotmail.de",
    "servicios-ta.com",
    "yahoo.co.jp",
]


def make_label_map(values):
    """
    Meniru perilaku LabelEncoder:
    kategori diurutkan alfabetis kemudian diberi
    angka 0, 1, 2, ...
    """

    values = list(values)

    if "0" not in values:
        values.append("0")

    values = sorted(
        set(str(v) for v in values)
    )

    return {
        value: index
        for index, value in enumerate(values)
    }


PRODUCT_MAP = make_label_map(
    PRODUCT_CODES
)

CARD_MAP = make_label_map(
    CARD_TYPES
)

EMAIL_MAP = make_label_map(
    P_EMAIL_DOMAINS
)


# =========================================================
# HELPERS
# =========================================================

def encode_category(
    value,
    mapping
):
    """
    Encode kategori dengan mapping yang kompatibel
    dengan konsep LabelEncoder.

    Jika kategori tidak dikenal, gunakan kategori '0'
    sebagai fallback.
    """

    if value is None:
        value = "0"

    value = str(value).strip().lower()

    if value == "":
        value = "0"

    return mapping.get(
        value,
        mapping["0"]
    )


# =========================================================
# SINGLE TRANSACTION PREPROCESSING
# =========================================================

def preprocess_single_transaction(
    amount: float,
    product_code: str,
    card_type: str,
    email_domain: str,
    transaction_hour: int,
):
    """
    Preprocessing KHUSUS SINGLE TRANSACTION.

    Tidak mengubah preprocessing CSV/full transaction.

    Output:
        numpy array shape (1, 444)
    """

    # -----------------------------------------------------
    # BASIC DATA
    # -----------------------------------------------------

    transaction = pd.DataFrame([
        {
            "TransactionDT": np.nan,

            "TransactionAmt": float(
                amount
            ),

            "ProductCD": (
                product_code
                .strip()
                .upper()
            ),

            "card4": (
                card_type
                .strip()
                .lower()
            ),

            "P_emaildomain": (
                email_domain
                .strip()
                .lower()
            ),

            # Single form tidak mempunyai
            # recipient email.
            "R_emaildomain": np.nan,
        }
    ])

    # -----------------------------------------------------
    # FEATURE ENGINEERING
    # -----------------------------------------------------

    transaction = create_features(
        transaction
    )

    # -----------------------------------------------------
    # SINGLE-SPECIFIC TIME
    # -----------------------------------------------------

    if "transaction_hour" in transaction.columns:

        transaction["transaction_hour"] = (
            int(transaction_hour)
        )

    if "is_night_transaction" in transaction.columns:

        transaction["is_night_transaction"] = int(
            transaction_hour <= 5
            or transaction_hour >= 23
        )

    # -----------------------------------------------------
    # CATEGORY ENCODING
    # -----------------------------------------------------
    #
    # Training menggunakan LabelEncoder.
    #
    # predict.py sebelumnya melakukan:
    #
    # pd.to_numeric(... errors="coerce")
    #
    # sehingga "W", "visa", "gmail.com", dll
    # berubah menjadi NaN.
    #
    # Itu yang kita perbaiki di sini.
    # -----------------------------------------------------

    if "ProductCD" in transaction.columns:

        transaction["ProductCD"] = (
            encode_category(
                transaction.loc[
                    transaction.index[0],
                    "ProductCD"
                ],
                PRODUCT_MAP
            )
        )

    if "card4" in transaction.columns:

        transaction["card4"] = (
            encode_category(
                transaction.loc[
                    transaction.index[0],
                    "card4"
                ],
                CARD_MAP
            )
        )

    if "P_emaildomain" in transaction.columns:

        transaction["P_emaildomain"] = (
            encode_category(
                transaction.loc[
                    transaction.index[0],
                    "P_emaildomain"
                ],
                EMAIL_MAP
            )
        )

    if "R_emaildomain" in transaction.columns:

        # Tidak ada R_emaildomain dari form.
        transaction["R_emaildomain"] = (
            EMAIL_MAP["0"]
        )

    # -----------------------------------------------------
    # EMAIL MATCH
    # -----------------------------------------------------
    #
    # Karena R_emaildomain tidak diberikan,
    # email_match = 0.
    # -----------------------------------------------------

    if "email_match" in transaction.columns:

        transaction["email_match"] = 0

    # -----------------------------------------------------
    # MISSING COUNT
    # -----------------------------------------------------
    #
    # Single transaction hanya memiliki sebagian
    # informasi dari 444 feature training.
    #
    # Nilai missing_count dari dataframe kecil
    # tidak comparable dengan training.
    #
    # Gunakan mean training sebagai neutral value.
    # -----------------------------------------------------

    if "missing_count" in feature_names:

        idx = feature_names.index(
            "missing_count"
        )

        transaction["missing_count"] = (
            scaler.mean_[idx]
        )

    # -----------------------------------------------------
    # REMOVE ID
    # -----------------------------------------------------

    if "TransactionID" in transaction.columns:

        transaction = transaction.drop(
            columns=["TransactionID"]
        )

    # -----------------------------------------------------
    # ALIGN 444 FEATURES
    # -----------------------------------------------------

    aligned = pd.DataFrame(
        index=transaction.index,
        columns=feature_names,
        dtype=float
    )

    # -----------------------------------------------------
    # COPY KNOWN FEATURES
    # -----------------------------------------------------

    for feature in feature_names:

        if feature not in transaction.columns:
            continue

        value = transaction.iloc[0][
            feature
        ]

        numeric_value = pd.to_numeric(
            pd.Series([value]),
            errors="coerce"
        ).iloc[0]

        if pd.notna(numeric_value):

            aligned.loc[
                aligned.index[0],
                feature
            ] = float(
                numeric_value
            )

    # -----------------------------------------------------
    # UNKNOWN FEATURES
    # -----------------------------------------------------
    #
    # Fitur lain seperti C*, D*, V*, card1, addr,
    # identity, dll tidak tersedia pada form.
    #
    # Gunakan mean training supaya setelah StandardScaler
    # nilainya menjadi sekitar 0.
    # -----------------------------------------------------

    for i, feature in enumerate(
        feature_names
    ):

        if pd.isna(
            aligned.iloc[0, i]
        ):

            aligned.iloc[
                0,
                i
            ] = scaler.mean_[i]

    # -----------------------------------------------------
    # TRANSACTIONDT
    # -----------------------------------------------------
    #
    # TransactionDT training adalah time-delta,
    # sedangkan form memberikan datetime.
    #
    # Kita tidak boleh memasukkan Unix timestamp
    # langsung ke feature ini.
    #
    # Gunakan mean training.
    # -----------------------------------------------------

    if "TransactionDT" in feature_names:

        idx = feature_names.index(
            "TransactionDT"
        )

        aligned.iloc[
            0,
            idx
        ] = scaler.mean_[idx]

    # -----------------------------------------------------
    # CLEAN
    # -----------------------------------------------------

    aligned = aligned.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # -----------------------------------------------------
    # FINAL FALLBACK
    # -----------------------------------------------------

    for i in range(
        len(feature_names)
    ):

        if pd.isna(
            aligned.iloc[0, i]
        ):

            aligned.iloc[
                0,
                i
            ] = scaler.mean_[i]

    # -----------------------------------------------------
    # SCALE
    # -----------------------------------------------------

    data_scaled = scaler.transform(
        aligned
    )

    # -----------------------------------------------------
    # VALIDATE
    # -----------------------------------------------------

    if data_scaled.shape[1] != (
        scaler.n_features_in_
    ):

        raise ValueError(
            "Jumlah fitur single transaction "
            f"harus {scaler.n_features_in__}, "
            f"tetapi mendapat "
            f"{data_scaled.shape[1]}"
        )

    return data_scaled