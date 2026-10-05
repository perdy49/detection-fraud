import numpy as np


def create_sequences(
    X,
    y,
    sequence_length=10
):
    # =========================
    # SAFETY CHECK
    # =========================
    if len(X) < sequence_length:
        raise ValueError(
            f"Jumlah data ({len(X)}) lebih kecil dari "
            f"sequence_length ({sequence_length})"
        )

    # =========================
    # INIT
    # =========================
    X_sequences = []
    y_sequences = []

    # =========================
    # BUILD SEQUENCES
    # =========================
    for i in range(len(X) - sequence_length + 1):

        X_seq = X[
            i:i + sequence_length
        ]

        y_seq = y[
            i + sequence_length - 1
        ]

        X_sequences.append(X_seq)

        y_sequences.append(y_seq)

    # =========================
    # CONVERT TO NUMPY
    # =========================
    X_sequences = np.array(
        X_sequences,
        dtype=np.float32
    )

    y_sequences = np.array(
        y_sequences,
        dtype=np.int32
    )

    # =========================
    # DEBUG INFO
    # =========================
    print(
        f"Sequence created: {X_sequences.shape}"
    )

    print(
        f"Labels created: {y_sequences.shape}"
    )

    return X_sequences, y_sequences