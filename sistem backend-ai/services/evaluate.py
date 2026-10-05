import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve
)


def evaluate_model(y_true, y_pred, y_prob):

    # =========================
    # CREATE RESULTS FOLDER
    # =========================
    os.makedirs(
        "results",
        exist_ok=True
    )

    # =========================
    # SAFE METRICS
    # =========================
    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    # =========================
    # SAFE ROC-AUC
    # =========================
    if len(np.unique(y_true)) > 1:
        roc_auc = roc_auc_score(
            y_true,
            y_prob
        )
    else:
        roc_auc = 0.0

    # =========================
    # PRINT RESULTS
    # =========================
    print("\n===== EVALUATION RESULTS =====")

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1-Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")

    # =========================
    # CLASSIFICATION REPORT
    # =========================
    print("\n===== CLASSIFICATION REPORT =====")

    print(
        classification_report(
            y_true,
            y_pred,
            zero_division=0
        )
    )

    # =========================
    # CONFUSION MATRIX
    # =========================
    cm = confusion_matrix(
        y_true,
        y_pred
    )

    plt.figure(
        figsize=(6, 5)
    )

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues"
    )

    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    plt.savefig(
        "results/confusion_matrix.png"
    )

    plt.close()

    # =========================
    # ROC CURVE
    # =========================
    if len(np.unique(y_true)) > 1:

        fpr, tpr, _ = roc_curve(
            y_true,
            y_prob
        )

        plt.figure(
            figsize=(6, 5)
        )

        plt.plot(
            fpr,
            tpr,
            label=f"AUC = {roc_auc:.4f}"
        )

        plt.plot(
            [0, 1],
            [0, 1],
            linestyle="--"
        )

        plt.title("ROC Curve")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend()

        plt.savefig(
            "results/roc_curve.png"
        )

        plt.close()

    print("\nVisualisasi berhasil disimpan di folder results/")

    # =========================
    # RETURN RESULTS
    # =========================
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": roc_auc
    }