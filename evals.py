"""Metrics and calibration plots for binary win-probability models.

The public entry point is :func:`evaluate_predictions`. It reports Brier Skill
Score (BSS), ROC AUC, and Kolmogorov-Smirnov (KS), and creates an
expected-probability versus actual-win-rate calibration chart.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, roc_auc_score, roc_curve


def _validate_inputs(y_true: np.ndarray, y_prob: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    y_true = np.asarray(y_true, dtype=float).reshape(-1)
    y_prob = np.asarray(y_prob, dtype=float).reshape(-1)
    if y_true.size != y_prob.size:
        raise ValueError("y_true and y_prob must have the same length")
    if y_true.size == 0:
        raise ValueError("y_true and y_prob cannot be empty")
    if not np.isin(y_true, [0.0, 1.0]).all():
        raise ValueError("y_true must contain only 0/1 labels")
    if not np.isfinite(y_prob).all() or ((y_prob < 0.0) | (y_prob > 1.0)).any():
        raise ValueError("y_prob must contain finite probabilities in [0, 1]")
    return y_true, y_prob


def calibration_table(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Return expected probability and observed win rate by equal-width bin."""

    if n_bins < 2:
        raise ValueError("n_bins must be at least 2")
    y_true, y_prob = _validate_inputs(y_true, y_prob)
    bin_id = np.minimum((y_prob * n_bins).astype(int), n_bins - 1)
    frame = pd.DataFrame({"bin": bin_id, "y_true": y_true, "y_prob": y_prob})
    grouped = frame.groupby("bin", sort=True, observed=True)
    result = grouped.agg(
        n=("y_true", "size"),
        expected=("y_prob", "mean"),
        actual=("y_true", "mean"),
    ).reset_index()
    result["bin_lower"] = result["bin"] / n_bins
    result["bin_upper"] = (result["bin"] + 1) / n_bins
    return result[["bin", "bin_lower", "bin_upper", "n", "expected", "actual"]]


def evaluate_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    reference_prob: float | None = None,
    n_bins: int = 10,
    title: str = "Expected win probability vs. actual win rate",
    ax=None,
    show: bool = True,
    save_path: str | Path | None = None,
) -> tuple[dict[str, float], pd.DataFrame, plt.Figure]:
    """Evaluate predictions and draw a reliability/calibration chart.

    BSS is calculated against a constant reference probability. If no
    ``reference_prob`` is supplied, the evaluation-sample win rate is used.
    The returned metrics include Brier score and log loss in addition to the
    requested BSS, AUC, and KS values.
    """

    y_true, y_prob = _validate_inputs(y_true, y_prob)
    if reference_prob is None:
        reference_prob = float(y_true.mean())
    if not 0.0 <= reference_prob <= 1.0:
        raise ValueError("reference_prob must be in [0, 1]")

    brier = float(np.mean((y_prob - y_true) ** 2))
    reference_brier = float(np.mean((reference_prob - y_true) ** 2))
    bss = float(1.0 - brier / reference_brier) if reference_brier else float("nan")

    if np.unique(y_true).size == 2:
        auc = float(roc_auc_score(y_true, y_prob))
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        ks = float(np.max(np.abs(tpr - fpr)))
    else:
        auc = float("nan")
        ks = float("nan")

    metrics = {
        "n": float(y_true.size),
        "win_rate": float(y_true.mean()),
        "reference_prob": float(reference_prob),
        "brier_score": brier,
        "reference_brier": reference_brier,
        "BSS": bss,
        "AUC": auc,
        "KS": ks,
        "log_loss": float(log_loss(y_true, y_prob, labels=[0, 1])),
    }

    calibration = calibration_table(y_true, y_prob, n_bins=n_bins)
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 6))
    else:
        fig = ax.figure
    ax.plot([0, 1], [0, 1], linestyle="--", color="0.45", label="Perfect calibration")
    ax.plot(
        calibration["expected"],
        calibration["actual"],
        marker="o",
        linewidth=2,
        label="Model",
    )
    ax.set(
        xlim=(0, 1),
        ylim=(0, 1),
        xlabel="Expected win probability",
        ylabel="Actual win rate",
        title=title,
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=160, bbox_inches="tight")
    if show:
        print(
            f"BSS={metrics['BSS']:.4f} | AUC={metrics['AUC']:.4f} | "
            f"KS={metrics['KS']:.4f}"
        )
        plt.show()
    return metrics, calibration, fig


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a CSV of binary probabilities.")
    parser.add_argument("csv", type=Path, help="CSV containing target and prediction columns")
    parser.add_argument("--target-column", default="target")
    parser.add_argument("--prediction-column", default="prediction")
    parser.add_argument("--reference-prob", type=float, default=None)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()
    frame = pd.read_csv(args.csv)
    metrics, _, _ = evaluate_predictions(
        frame[args.target_column].to_numpy(),
        frame[args.prediction_column].to_numpy(),
        reference_prob=args.reference_prob,
        save_path=args.plot,
    )
    print(pd.Series(metrics).to_string())


if __name__ == "__main__":
    main()
