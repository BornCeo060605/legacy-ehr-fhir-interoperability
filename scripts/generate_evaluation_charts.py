"""
Academic & Report-Ready Visualizations for Phase 1 Ground-Truth Evaluation.
Generates 10 high-resolution publication-grade figures (PNG at 300 DPI + PDF).
Strictly adheres to ground-truth evaluation numbers:
  Total Evaluated: 90
  Semantic Accuracy: 88/90 (97.8%)
  Coverage: 87/90 (96.7%)
  Normalized Element Accuracy: 83/90 (92.2%)
  Decision Accuracy: 83/90 (92.2%)
  FHIR Resource Accuracy: 74/90 (82.2%)
  Datatype Accuracy: 74/90 (82.2%)
  Cardinality Accuracy: 69/90 (76.7%)
  Strict Exact Element Accuracy: 68/90 (75.6%)
  Terminology Accuracy: 12/12 applicable (100.0%)
  Accepted Precision: 73/80 (91.3%)
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# Set academic styling
plt.rcParams.update({
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica", "Calibri"],
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "bold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.titleweight": "bold",
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.0,
    "grid.color": "#e0e0e0",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
})

# Academic color palette
PRIMARY_BLUE = "#1f4e79"
ACCENT_TEAL = "#2e8b57"
LIGHT_BLUE = "#5b9bd5"
SOFT_CORAL = "#d9534f"
MUTED_GRAY = "#7f7f7f"
LIGHT_GRAY = "#d9d9d9"
AMBER_WARN = "#ec971f"
DARK_NAVY = "#0d233a"
BORDER_COLOR = "#cccccc"

OUTPUT_DIR = os.path.join("outputs", "reports", "charts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_fig(fig, filename_base):
    png_path = os.path.join(OUTPUT_DIR, f"{filename_base}.png")
    pdf_path = os.path.join(OUTPUT_DIR, f"{filename_base}.pdf")
    fig.tight_layout()
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {png_path} and {pdf_path}")


# ==============================================================================
# CHART 1: Overall Evaluation Metrics
# ==============================================================================
def create_chart_1():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    metrics = [
        ("Semantic Meaning Accuracy", 97.8, 88, 90),
        ("Mapping Coverage", 96.7, 87, 90),
        ("Normalized / Usable FHIR Element", 92.2, 83, 90),
        ("Decision Accuracy", 92.2, 83, 90),
        ("FHIR Resource Accuracy", 82.2, 74, 90),
        ("Datatype Accuracy", 82.2, 74, 90),
        ("Cardinality Accuracy", 76.7, 69, 90),
        ("Strict Exact FHIR Element", 75.6, 68, 90),
    ]
    # Reverse for top-to-bottom descending display in horizontal bar
    metrics = metrics[::-1]
    labels = [m[0] for m in metrics]
    values = [m[1] for m in metrics]
    counts = [f"{m[2]}/{m[3]}" for m in metrics]

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, values, color=PRIMARY_BLUE, height=0.62, edgecolor="#0e2840", linewidth=0.8)

    ax.set_xlim(0, 105)
    ax.set_xlabel("Accuracy / Coverage (%)")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar, val, cnt in zip(bars, values, counts):
        ax.text(val + 1.2, bar.get_y() + bar.get_height() / 2, f"{val:.1f}%  ({cnt})",
                va="center", ha="left", fontsize=9.5, fontweight="bold", color="#1a1a1a")

    ax.set_title("Overall Phase 1 Evaluation Performance\nAccuracy and coverage against 90 independent ground-truth mappings", pad=14)
    
    # Subtext for terminology subset
    ax.text(0.01, -0.12, "Note: Terminology Accuracy is 100.0% (12/12 applicable coded fields; 57 non-coded fields are N/A).",
            transform=ax.transAxes, fontsize=9, style="italic", color="#555555")

    save_fig(fig, "01_overall_evaluation_metrics")


# ==============================================================================
# CHART 2: Strict vs Normalized FHIR Mapping
# ==============================================================================
def create_chart_2():
    fig, ax = plt.subplots(figsize=(8, 5.5))
    
    categories = [
        "Strict Exact Element Accuracy\n(Literal Path Match)",
        "Normalized / Usable Element\n(FHIR R4 Equivalence)"
    ]
    values = [75.6, 92.2]
    counts = ["68 / 90", "83 / 90"]
    colors = [LIGHT_BLUE, PRIMARY_BLUE]

    x_pos = np.arange(len(categories))
    bars = ax.bar(x_pos, values, color=colors, width=0.48, edgecolor="#222222", linewidth=0.9)

    ax.set_ylim(0, 105)
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar, val, cnt in zip(bars, values, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 2.0, f"{val:.1f}%\n({cnt})",
                ha="center", va="bottom", fontsize=10.5, fontweight="bold", color="#1a1a1a")

    # Add difference callout arrow
    ax.annotate(
        "+16.6% Usable Resolution\n(Choice elements, sub-elements & subject links)",
        xy=(1.0, 92.2), xytext=(0.5, 78.0),
        arrowprops=dict(facecolor="#333333", arrowstyle="->", lw=1.2),
        ha="center", fontsize=9.5, bbox=dict(boxstyle="round,pad=0.4", fc="#f7f7f9", ec="#cccccc")
    )

    ax.set_title("FHIR Element Mapping Accuracy\nComparison of exact path matching and normalized FHIR R4 equivalence", pad=14)
    save_fig(fig, "02_fhir_element_accuracy")


# ==============================================================================
# CHART 3: Hospital-Level Generalization
# ==============================================================================
def create_chart_3():
    fig, ax = plt.subplots(figsize=(10, 6))

    hospitals = [
        "Hospital A\n(Clean / Normalized)",
        "Hospital B\n(Abbreviated / Coded)",
        "Hospital C\n[HELD-OUT TEST DIALECT]"
    ]
    
    strict_vals = [83.3, 76.7, 66.7]
    norm_vals = [96.7, 93.3, 86.7]
    res_vals = [90.0, 83.3, 73.3]

    x = np.arange(len(hospitals))
    width = 0.25

    rects1 = ax.bar(x - width, strict_vals, width, label="Strict Exact Element", color=LIGHT_BLUE, edgecolor="#333333")
    rects2 = ax.bar(x, norm_vals, width, label="Normalized / Usable Element", color=PRIMARY_BLUE, edgecolor="#333333")
    rects3 = ax.bar(x + width, res_vals, width, label="FHIR Resource Accuracy", color=ACCENT_TEAL, edgecolor="#333333")

    ax.set_ylim(0, 110)
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(hospitals, fontweight="bold")
    ax.legend(loc="upper right", frameon=True, edgecolor="#cccccc")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    def autolabel(rects):
        for rect in rects:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    # Highlight held-out test dialect
    ax.axvspan(1.5, 2.5, color="#f5f5f5", alpha=0.6, zorder=0)
    ax.text(2.0, 103, "Held-Out Unseen Test Dialect (n=30)", ha="center", fontsize=9, style="italic", color="#555555")

    ax.set_title("Mapping Performance Across Legacy Hospital Dialects\nComparison across three independently generated legacy schema dialects", pad=14)
    save_fig(fig, "03_hospital_generalization")


# ==============================================================================
# CHART 4: Accepted Mapping Precision by Hospital
# ==============================================================================
def create_chart_4():
    fig, ax = plt.subplots(figsize=(9, 5.5))

    groups = [
        "Hospital A\n(Clean)",
        "Hospital B\n(Abbreviated)",
        "Hospital C\n[HELD-OUT TEST]",
        "Overall Pooled\n(All Hospitals)"
    ]
    precision_vals = [100.0, 92.6, 81.5, 91.3]
    counts = ["26 / 26", "25 / 27", "22 / 27", "73 / 80"]
    colors = [PRIMARY_BLUE, PRIMARY_BLUE, AMBER_WARN, DARK_NAVY]

    x_pos = np.arange(len(groups))
    bars = ax.bar(x_pos, precision_vals, color=colors, width=0.48, edgecolor="#222222", linewidth=0.9)

    ax.set_ylim(0, 115)
    ax.set_ylabel("Accepted Mapping Precision (%)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(groups, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar, val, cnt in zip(bars, precision_vals, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 2.5, f"{val:.1f}%\n({cnt})",
                ha="center", va="bottom", fontsize=9.5, fontweight="bold")

    ax.axhline(91.3, color=DARK_NAVY, linestyle=":", alpha=0.7, label="Overall Precision (91.3%)")
    ax.legend(loc="upper right", frameon=True)

    ax.set_title("Precision of Automatically Accepted Mappings\nProportion of ACCEPTED predictions that matched the ground truth", pad=14)
    ax.text(0.01, -0.12, "Note: Distinguishes auto-acceptance reliability from overall dataset accuracy.",
            transform=ax.transAxes, fontsize=9, style="italic", color="#555555")

    save_fig(fig, "04_accepted_mapping_precision")


# ==============================================================================
# CHART 5: Decision Distribution
# ==============================================================================
def create_chart_5():
    fig, ax = plt.subplots(figsize=(8, 5.5))

    categories = ["ACCEPTED", "REVIEW", "UNSUPPORTED"]
    counts = [80, 7, 3]
    percentages = [88.9, 7.8, 3.3]
    colors = [PRIMARY_BLUE, AMBER_WARN, SOFT_CORAL]

    x_pos = np.arange(len(categories))
    bars = ax.bar(x_pos, counts, color=colors, width=0.45, edgecolor="#222222", linewidth=0.9)

    ax.set_ylim(0, 95)
    ax.set_ylabel("Field Count (Total = 90)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar, count, pct in zip(bars, counts, percentages):
        ax.text(bar.get_x() + bar.get_width() / 2, count + 2.0, f"n = {count}\n({pct:.1f}%)",
                ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("Phase 1 Decision Distribution\nFinal deterministic decision across 90 evaluated fields", pad=14)
    ax.text(0.01, -0.12, "Note: Displays pipeline decision outputs, not mapping correctness scores.",
            transform=ax.transAxes, fontsize=9, style="italic", color="#555555")

    save_fig(fig, "05_decision_distribution")


# ==============================================================================
# CHART 6: Decision Correctness
# ==============================================================================
def create_chart_6():
    fig, ax = plt.subplots(figsize=(8.5, 6))

    categories = ["ACCEPTED\n(n = 80)", "REVIEW\n(n = 7)", "UNSUPPORTED\n(n = 3)"]
    correct = [73, 7, 3]
    incorrect = [7, 0, 0]

    x_pos = np.arange(len(categories))
    width = 0.42

    p1 = ax.bar(x_pos, correct, width, label="Correct (True Positive / True Negative)", color=PRIMARY_BLUE, edgecolor="#222222")
    p2 = ax.bar(x_pos, incorrect, width, bottom=correct, label="Incorrect (Discrepancy)", color=SOFT_CORAL, edgecolor="#222222")

    ax.set_ylim(0, 95)
    ax.set_ylabel("Number of Predictions")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontweight="bold")
    ax.legend(loc="upper right", frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    # Annotate ACCEPTED
    ax.text(0, 73 / 2, "73 Correct\n(91.3%)", ha="center", va="center", color="white", fontweight="bold", fontsize=9.5)
    ax.text(0, 73 + 7 / 2, "7 Err", ha="center", va="center", color="white", fontweight="bold", fontsize=8.5)

    # Annotate REVIEW
    ax.text(1, 3.5, "7 Correct\n(100.0%)", ha="center", va="center", color="white", fontweight="bold", fontsize=9)

    # Annotate UNSUPPORTED
    ax.text(2, 1.5, "3 Correct\n(100.0%)", ha="center", va="center", color="white", fontweight="bold", fontsize=9)

    ax.set_title("Decision Outcomes Compared with Ground Truth\nCorrect and incorrect predictions within each deterministic decision category", pad=14)
    save_fig(fig, "06_decision_correctness")


# ==============================================================================
# CHART 7: Confidence Band vs Observed Accuracy
# ==============================================================================
def create_chart_7():
    fig, ax = plt.subplots(figsize=(9, 5.5))

    bands = ["0.00–0.49\n(n = 3)", "0.50–0.74\n(n = 5)", "0.75–0.89\n(n = 32)", "0.90–1.00\n(n = 50)"]
    accuracies = [100.0, 100.0, 93.8, 90.0]
    correct_counts = [3, 5, 30, 45]
    total_counts = [3, 5, 32, 50]

    x_pos = np.arange(len(bands))
    bars = ax.bar(x_pos, accuracies, color=PRIMARY_BLUE, width=0.45, edgecolor="#222222", linewidth=0.9)

    ax.set_ylim(0, 115)
    ax.set_ylabel("Observed Mapping Accuracy (%)")
    ax.set_xlabel("Predicted Confidence Band")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bands, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar, acc, corr, tot in zip(bars, accuracies, correct_counts, total_counts):
        ax.text(bar.get_x() + bar.get_width() / 2, acc + 2.0, f"{acc:.1f}%\n({corr}/{tot})",
                ha="center", va="bottom", fontsize=9.5, fontweight="bold")

    # Annotate high-confidence error callout
    ax.annotate(
        "5 Overconfident Errors\n(45 / 50 correct in 0.90–1.00 band)",
        xy=(3, 90.0), xytext=(2.2, 70.0),
        arrowprops=dict(facecolor=SOFT_CORAL, arrowstyle="->", lw=1.2),
        ha="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.4", fc="#fff1f0", ec=SOFT_CORAL)
    )

    ax.set_title("Confidence Versus Observed Mapping Accuracy\nObserved correctness within each predicted-confidence band", pad=14)
    save_fig(fig, "07_confidence_vs_accuracy")


# ==============================================================================
# CHART 8: Mapping Error Categories
# ==============================================================================
def create_chart_8():
    fig, ax = plt.subplots(figsize=(10.5, 5))

    errors = [
        ("Encounter.subject  →  Patient.identifier", 2),
        ("Condition.identifier  →  Observation.identifier", 2),
        ("Encounter.identifier  →  Observation.identifier", 1),
        ("Encounter.period.start  →  Observation.effectiveDateTime", 1),
        ("Encounter.period.end  →  Observation.effectiveDateTime", 1),
    ]
    # Reverse for top-to-bottom
    errors = errors[::-1]
    labels = [e[0] for e in errors]
    counts = [e[1] for e in errors]

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, counts, color=SOFT_CORAL, height=0.55, edgecolor="#7a1c18", linewidth=0.9)

    ax.set_xlim(0, 3)
    ax.set_xlabel("Number of Discrepancies (Total = 7 / 90)")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontweight="bold", family="monospace", fontsize=9.5)
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar, val in zip(bars, counts):
        ax.text(val + 0.08, bar.get_y() + bar.get_height() / 2, f"Count: {val}",
                va="center", ha="left", fontsize=9.5, fontweight="bold", color="#1a1a1a")

    ax.set_title("Observed FHIR Mapping Errors\nSeven discrepancies identified against the independent ground truth", pad=14)
    save_fig(fig, "08_mapping_errors")


# ==============================================================================
# CHART 9: Error Type Summary
# ==============================================================================
def create_chart_9():
    fig, ax = plt.subplots(figsize=(8, 5))

    categories = [
        "Wrong FHIR Resource\n(Conflating Event/Condition with Observation)",
        "Relationship Error\n(Patient FK mapped to Patient.identifier)"
    ]
    counts = [5, 2]
    percentages = [71.4, 28.6]
    colors = [SOFT_CORAL, AMBER_WARN]

    x_pos = np.arange(len(categories))
    bars = ax.bar(x_pos, counts, color=colors, width=0.45, edgecolor="#222222", linewidth=0.9)

    ax.set_ylim(0, 6.5)
    ax.set_ylabel("Error Count (Total = 7)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontweight="bold", fontsize=9.5)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar, count, pct in zip(bars, counts, percentages):
        ax.text(bar.get_x() + bar.get_width() / 2, count + 0.2, f"n = {count} ({pct:.1f}%)",
                ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("Classification of Observed Mapping Errors\nMutually exclusive root cause categorization across 7 discrepancies", pad=14)
    save_fig(fig, "09_error_type_summary")


# ==============================================================================
# CHART 10: Retrieval vs Reasoning Errors
# ==============================================================================
def create_chart_10():
    fig, ax = plt.subplots(figsize=(8, 5))

    categories = [
        "Retrieval Failures\n(Correct element absent in evidence)",
        "Reasoning / Mapping Errors\n(Target retrieved, but wrong choice made)"
    ]
    counts = [0, 7]
    percentages = [0.0, 100.0]
    colors = [LIGHT_GRAY, SOFT_CORAL]

    x_pos = np.arange(len(categories))
    bars = ax.bar(x_pos, counts, color=colors, width=0.45, edgecolor="#222222", linewidth=0.9)

    ax.set_ylim(0, 8.5)
    ax.set_ylabel("Discrepancy Count (Total = 7)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontweight="bold", fontsize=9.5)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar, count, pct in zip(bars, counts, percentages):
        ax.text(bar.get_x() + bar.get_width() / 2, count + 0.25, f"{count} / 7 ({pct:.1f}%)",
                ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("Location of Observed Mapping Errors\nAll seven observed discrepancies occurred despite correct targets being available in retrieved evidence", pad=14)
    ax.text(0.01, -0.12, "Note: Evaluated across 90 mappings; demonstrates retrieval sufficiency vs reasoning bottleneck.",
            transform=ax.transAxes, fontsize=9, style="italic", color="#555555")

    save_fig(fig, "10_retrieval_vs_reasoning_errors")


def main():
    print("Generating Academic Evaluation Charts in outputs/reports/charts/ ...")
    create_chart_1()
    create_chart_2()
    create_chart_3()
    create_chart_4()
    create_chart_5()
    create_chart_6()
    create_chart_7()
    create_chart_8()
    create_chart_9()
    create_chart_10()
    print("All 10 charts successfully generated.")


if __name__ == "__main__":
    main()
