# Power BI Dashboard — Build Guide (Set C)

`.pbix` is a proprietary Microsoft binary format that can only be produced by
Power BI Desktop itself, so it must be built on your machine. This guide
gives you the exact steps, M code, and DAX so it takes about 10 minutes.
Save the finished file as `powerbi/dashboard.pbix`.

## 1. Get Data

`Home > Get Data > Text/CSV` — load both:
- `data/raw/assessments.csv`
- `data/raw/courses.csv`

## 2. Power Query Editor (B1 — 2 marks)

**assessments query:**
1. Set data types: `assessment_id` = Whole Number, `month` = Text,
   `course_id` = Text, `batch` = Text, `score` = Whole Number,
   `attendance_pct` = Whole Number.
2. Select all columns → `Home > Remove Rows > Remove Duplicates`
   (or right-click `assessment_id` column → Remove Duplicates once all
   columns are selected) so the query returns **12 rows**.

**courses query:** set `course_id`, `course`, `department` all to Text.

`Home > Close & Apply`.

## 3. Model view — relationship (B1 — 1 mark)

Drag `courses[course_id]` onto `assessments[course_id]`.
- Cardinality: **One (courses) to Many (assessments)**
- Cross-filter direction: **Single** (courses filters assessments)
- Confirm the relationship is **Active**.

## 4. Measures table (B2 — 3 marks)

`Modeling > New Table` → name it `Measures`, enter:
```
Measures = ROW("_", BLANK())
```
Then `Modeling > New Measure` (with `Measures` table selected) three times:

```DAX
Assessment Count = COUNTROWS(assessments)

Avg Score = AVERAGE(assessments[score])

Pass Rate =
DIVIDE(
    COUNTROWS(FILTER(assessments, assessments[score] >= 50)),
    COUNTROWS(assessments),
    0
)
```
Format `Pass Rate` as **Percentage** in the visual (right-click the card →
Format → Values, or use the ribbon's `%` button while the measure is
selected).

## 5. Report page (B3 — 2 marks)

Add one page with:
1. **Three KPI cards** — `Assessment Count`, `Avg Score`, `Pass Rate`.
2. **Bar chart** — Axis = `courses[department]`, Values = `Avg Score`
   (or `Pass Rate`).
3. **Monthly trend chart** (bar or line) — Axis = `assessments[month]`,
   Values = `Avg Score`. Sort the axis Jan → Feb → Mar:
   `Column tools > Sort by Column`, or add a helper column
   `MonthSort = SWITCH(assessments[month], "Jan", 1, "Feb", 2, "Mar", 3)`
   and sort `month` by `MonthSort`.
4. **Slicer** on `assessments[batch]`, set to filter the whole page
   (default interaction = filter).

Test it: set the slicer to one batch, note the three card values, then
clear the filter. Write the two numeric findings + one recommendation
in the main `README.md` (see the Findings section).

## 6. Screenshot

With the slicer **cleared** (unfiltered state), export/screenshot the page
to `outputs/powerbi_dashboard.png`.

## 7. Refreshing on another machine

Anyone who clones the repo should re-point the two CSV sources:
`Transform Data > Data source settings > Change Source...`, browse to
`data/raw/assessments.csv` and `data/raw/courses.csv` inside their local
clone, then `Refresh`.
