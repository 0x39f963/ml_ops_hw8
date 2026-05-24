import json
from pathlib import Path

import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from evidently.test_preset import DataDriftTestPreset
from evidently.test_suite import TestSuite
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


REPORTS_DIR = Path("reports")


def build_batches() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    wine = load_wine(as_frame=True)
    data = wine.frame.copy()
    x = data.drop(columns=["target"])
    y = data["target"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.40,
        random_state=42,
        stratify=y,
    )
    baseline = x_test.copy()
    current = x_test.copy()
    current["alcohol"] = current["alcohol"] * 1.35
    current["color_intensity"] = current["color_intensity"] * 2.75
    current["flavanoids"] = current["flavanoids"] * 0.45
    return (
        x_train.reset_index(drop=True),
        baseline.reset_index(drop=True),
        current.reset_index(drop=True),
        y_train,
        y_test,
    )


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    reference_df, baseline_df, current_df, y_train, y_current = build_batches()

    report = Report(metrics=[DataDriftPreset(stattest="psi", stattest_threshold=0.2)])
    report.run(reference_data=reference_df, current_data=current_df)
    report.save_html(str(REPORTS_DIR / "data_drift_report.html"))

    tests = TestSuite(tests=[DataDriftTestPreset(stattest_threshold=0.2)])
    tests.run(reference_data=reference_df, current_data=current_df)
    tests.save_html(str(REPORTS_DIR / "data_drift_tests.html"))

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, random_state=42),
    )
    model.fit(reference_df, y_train)

    baseline_pred = model.predict(baseline_df)
    current_pred = model.predict(current_df)
    baseline_acc = accuracy_score(y_current, baseline_pred)
    current_acc = accuracy_score(y_current, current_pred)

    metrics = {
        "baseline_batch": "unchanged holdout batch from sklearn wine",
        "current_batch": "same feature schema with synthetic drift in 3 numeric columns",
        "baseline_acc": round(float(baseline_acc), 4),
        "current_acc": round(float(current_acc), 4),
        "delta": round(float(current_acc - baseline_acc), 4),
        "current_f1_macro": round(float(f1_score(y_current, current_pred, average="macro")), 4),
        "reference_rows": int(len(reference_df)),
        "current_rows": int(len(current_df)),
        "drift_note": "data drift is visible without labels; degradation uses labelled current batch",
    }
    (REPORTS_DIR / "degradation_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
