"""
Training Performance Analysis — Set C
Python module (Task 3: P1, P2, P3)

Run from the repository root:
    python python/analysis.py

All paths below are relative to the repo root so this script runs unchanged
on another machine after `git clone`.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# P1 — Load, Clean & Merge
# ---------------------------------------------------------------------------

RAW_ASSESSMENTS = "data/raw/assessments.csv"
RAW_COURSES = "data/raw/courses.csv"

assessments = pd.read_csv(RAW_ASSESSMENTS)
courses = pd.read_csv(RAW_COURSES)

# Confirm numeric types for score and attendance_pct
assessments["score"] = pd.to_numeric(assessments["score"])
assessments["attendance_pct"] = pd.to_numeric(assessments["attendance_pct"])

rows_before = len(assessments)

# Remove the exact duplicate row (assessment_id 12 appears twice)
assessments_clean = assessments.drop_duplicates(keep="first").reset_index(drop=True)

rows_after = len(assessments_clean)
print(f"Row count before de-duplication: {rows_before}")
print(f"Row count after de-duplication:  {rows_after}")
assert rows_before == 13, "Expected 13 raw rows including the duplicate."
assert rows_after == 12, "Expected exactly 12 unique rows after cleaning."

# Left join assessments -> courses on course_id
merged = assessments_clean.merge(courses, on="course_id", how="left")

# Integrity checks required by the spec
assert len(merged) == 12, "Merged DataFrame must contain exactly 12 rows."
assert merged["department"].isna().sum() == 0, (
    "Every course_id in the fact file must match a lookup row "
    "(zero unmatched keys expected)."
)
print("Merge check passed: 12 rows, 0 unmatched course_id -> department values.")

# ---------------------------------------------------------------------------
# P2 — Derived Field & Department Analysis
# ---------------------------------------------------------------------------

merged["pass_flag"] = (merged["score"] >= 50).astype(int)

# Grouped summary by department: count, sum of pass_flag, pass rate (%)
department_summary = (
    merged.groupby("department")
    .agg(
        total_assessments=("pass_flag", "count"),
        passing_count=("pass_flag", "sum"),
    )
    .reset_index()
)
department_summary["pass_rate_pct"] = (
    department_summary["passing_count"] / department_summary["total_assessments"] * 100
).round(2)

print("\nDepartment summary:")
print(department_summary.to_string(index=False))

# Group by course to find the course with the lowest pass rate
course_summary = (
    merged.groupby(["course_id", "course"])
    .agg(
        total_assessments=("pass_flag", "count"),
        passing_count=("pass_flag", "sum"),
    )
    .reset_index()
)
course_summary["pass_rate_pct"] = (
    course_summary["passing_count"] / course_summary["total_assessments"] * 100
).round(2)

lowest_row = course_summary.loc[course_summary["pass_rate_pct"].idxmin()]
print(
    f"\nLowest pass-rate course: {lowest_row['course']} ({lowest_row['course_id']}) — "
    f"{int(lowest_row['passing_count'])}/{int(lowest_row['total_assessments'])} "
    f"passing = {lowest_row['pass_rate_pct']:.2f}%"
)

# ---------------------------------------------------------------------------
# P3 — Chart & Exports
# ---------------------------------------------------------------------------

os.makedirs("outputs", exist_ok=True)
os.makedirs("outputs/sql", exist_ok=True)
os.makedirs("outputs/supplementary", exist_ok=True)
os.makedirs("assets", exist_ok=True)

month_order = ["Jan", "Feb", "Mar"]
monthly_avg = (
    merged.groupby("month")["score"]
    .mean()
    .reindex(month_order)
    .round(2)
)

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(monthly_avg.index, monthly_avg.values, color="#4C72B0")
ax.set_title("Monthly Average Assessment Score (Jan \u2192 Feb \u2192 Mar)")
ax.set_xlabel("Month")
ax.set_ylabel("Average Score")
for i, v in enumerate(monthly_avg.values):
    ax.text(i, v + 1, f"{v:.2f}", ha="center", fontweight="bold")
ax.set_ylim(0, max(monthly_avg.values) + 15)
fig.tight_layout()
fig.savefig("outputs/python_chart.png", dpi=150)
plt.close(fig)
print("\nSaved chart to outputs/python_chart.png")

# Export clean merged dataset
export_cols = [
    "assessment_id",
    "month",
    "course_id",
    "course",
    "department",
    "batch",
    "score",
    "attendance_pct",
    "pass_flag",
]
merged[export_cols].to_csv("outputs/clean_data.csv", index=False)
print("Saved cleaned/merged data to outputs/clean_data.csv")

department_summary.to_csv("outputs/python_summary.csv", index=False)
print("Saved department summary to outputs/python_summary.csv")

# ---------------------------------------------------------------------------
# Cross-tool reconciliation helper — overall pass rate & Technology dept.
# ---------------------------------------------------------------------------
overall_pass_rate = merged["pass_flag"].mean() * 100
tech_pass_rate = department_summary.loc[
    department_summary["department"] == "Technology", "pass_rate_pct"
].values[0]
print(f"\nOverall pass rate (all 12 rows): {overall_pass_rate:.2f}%")
print(f"Technology department pass rate: {tech_pass_rate:.2f}%")

# ---------------------------------------------------------------------------
# P4 (supplementary) — Deeper analysis: correlation, segments, trend, outliers
# These go beyond the exam's minimum P1-P3 requirement and feed the
# "Deeper Insights" section of README.md.
# ---------------------------------------------------------------------------

# 1. Correlation between attendance and score
correlation = merged["score"].corr(merged["attendance_pct"])
print(f"\nCorrelation (score vs attendance_pct): r = {correlation:.3f}")

# 2. Overall score distribution
print(
    f"Overall score distribution: mean={merged['score'].mean():.2f}, "
    f"median={merged['score'].median():.2f}, std={merged['score'].std():.2f}, "
    f"min={merged['score'].min():.2f}, max={merged['score'].max():.2f}"
)

# 3. Batch x department segment table (smallest cells an exam this size can support)
segment = (
    merged.groupby(["batch", "department"])
    .agg(avg_score=("score", "mean"), avg_attendance=("attendance_pct", "mean"), n=("score", "size"))
    .round(2)
    .reset_index()
)
worst_segment = segment.loc[segment["avg_score"].idxmin()]
print("\nBatch x Department segments:")
print(segment.to_string(index=False))
print(
    f"\nWeakest segment: {worst_segment['batch']} / {worst_segment['department']} — "
    f"avg score {worst_segment['avg_score']:.2f} (n={int(worst_segment['n'])})"
)

# 4. Course trend Jan -> Mar (is the course actually improving, or just noisy?)
course_trend = merged.pivot_table(index="course", columns="month", values="score")[month_order]
course_trend["change_jan_to_mar"] = course_trend["Mar"] - course_trend["Jan"]
print("\nCourse score trend by month (Jan -> Feb -> Mar):")
print(course_trend.round(2).to_string())

# 5. Low-attendance rows (attendance < 75%) — do they coincide with failing scores?
low_attendance = merged[merged["attendance_pct"] < 75][
    ["course", "batch", "month", "score", "attendance_pct", "pass_flag"]
]
print("\nRows with attendance below 75%:")
print(low_attendance.to_string(index=False))

# --- Save supplementary outputs ---
# Note: these go beyond the exam's minimum requirement, so they're kept out of
# outputs/'s top level (which holds only the exam's required deliverables) and
# organised into outputs/supplementary/ and assets/ instead.
segment.to_csv("outputs/supplementary/python_deep_analysis.csv", index=False)
course_trend.reset_index().to_csv("outputs/supplementary/python_course_trend.csv", index=False)
print("\nSaved segment table to outputs/supplementary/python_deep_analysis.csv")
print("Saved course trend table to outputs/supplementary/python_course_trend.csv")

# --- Scatter chart: attendance vs score, colored by pass/fail ---
fig2, ax2 = plt.subplots(figsize=(7, 5))
colors = merged["pass_flag"].map({1: "#4C9A5B", 0: "#C0504D"})
ax2.scatter(merged["attendance_pct"], merged["score"], c=colors, s=80, edgecolor="black", zorder=3)
ax2.set_title(f"Attendance vs. Score (r = {correlation:.2f})")
ax2.set_xlabel("Attendance (%)")
ax2.set_ylabel("Score")
ax2.axhline(50, color="gray", linestyle="--", linewidth=1, label="Pass threshold (score = 50)")
ax2.grid(alpha=0.3)
ax2.legend(["Pass threshold (score = 50)"], loc="upper left", fontsize=8)
fig2.tight_layout()
fig2.savefig("assets/python_scatter_attendance_vs_score.png", dpi=150)
plt.close(fig2)
print("Saved scatter chart to assets/python_scatter_attendance_vs_score.png")
