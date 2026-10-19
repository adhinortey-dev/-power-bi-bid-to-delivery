# Model and report guide

## Model design

Use a small star-schema / constellation model. Do not join Projects directly to Shipments: a project can have multiple shipment rows, which would duplicate quote amounts and costs.

```text
DimQuoteDate  1 ─── * Projects * ─── 1 DimProject 1 ─── * Shipments * ─── 1 DimShipDate
DimAwardDate  1 ─── * Projects
                 1 DimRegion
                 1 DimEstimator
                 1 DimProjectType
                 1 DimStage
```

Recommended implementation:

- `Projects` remains one row per ProjectID.
- Create `DimProject` as a reference of Projects with only ProjectID, Customer, Region, CustomerSegment, ProjectType, Estimator, Stage, and Priority, then remove duplicates by ProjectID. If using a single project dimension for all page slicers, remove those descriptive columns from Projects after creating the dimension.
- Relate `DimProject[ProjectID]` 1:* to both `Projects[ProjectID]` and `Shipments[ProjectID]`, single direction from dimension to facts. This design allows project attributes to filter both facts without fact-to-fact joins.
- Create `DimQuoteDate`, `DimAwardDate`, and `DimShipDate` as separate calendar tables. Connect them 1:* to `Projects[QuoteDate]`, `Projects[AwardDate]`, and `Shipments[PlannedShipDate]` respectively. Mark each as a date table. Separate role-playing calendars make each report filter's date meaning explicit.
- Keep the descriptive slicer fields (Customer, Region, CustomerSegment, ProjectType, Estimator, Stage, Priority) on `DimProject` for the first version. Do not also add separate dimensions for those same fields; that creates unnecessary parallel filter paths.
- Use single-direction relationships. Check that project filters reach both fact tables and date filters reach only their intended date fact.

For a beginner-friendly first version, use `Projects`, `Shipments`, `DimProject`, and all three date tables.

## Calendar table

Create this calculated table three times, naming the copies `DimQuoteDate`, `DimAwardDate`, and `DimShipDate`. Set the start/end dates to cover the full respective date fields; include 2024-01-01 through 2027-12-31 to cover shipment lead time.

```DAX
Calendar =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2024, 1, 1 ), DATE ( 2027, 12, 31 ) ),
    "Year", YEAR ( [Date] ),
    "Quarter", "Q" & FORMAT ( [Date], "Q" ),
    "Month Number", MONTH ( [Date] ),
    "Month", FORMAT ( [Date], "MMM" ),
    "Year Month", FORMAT ( [Date], "YYYY-MM" ),
    "Year Month Sort", YEAR ( [Date] ) * 100 + MONTH ( [Date] )
)
```

Sort `Month` by `Month Number`; sort `Year Month` by `Year Month Sort`. Mark `[Date]` as the date column for each calendar table.

## Report page 1 — Executive overview (included in the current PBIX)

Purpose: summarize bid health and operating results at a glance.

- Multi-measure KPI card: Open Pipeline Value, Win Rate, Awarded Revenue, Gross Margin $, and On-time Shipment %.
- Horizontal bar charts: Project Count by Stage and Win Rate by Region.
- Monthly line charts: Awarded Revenue by award month and Quoted Value by quote month.
- Slicers: Region and ProjectType; title and subtitle text boxes.

The current PBIX has one report page with the visuals listed above. The additional page designs below are suggested future work and are not yet included in the PBIX. The current quoted-value line chart should use `Year Month` as its displayed axis and sort it chronologically by `Year Month Sort`; do not display the numeric sort key as a category.

## Future page 2 — Bid performance

- Open pipeline by stage, region, estimator, and customer segment.
- Submitted quote count and value, won / lost / no-response split.
- Win rate by estimator and project type; include counts in tooltips to make small samples visible.
- Average days to award for awarded projects.
- Detail table with ProjectID, customer, quote date, stage, quoted tons, amount, and estimator.

## Future page 3 — Delivery and margin

- On-time shipment percentage and late shipment tonnage.
- Planned vs. actual shipment tons by month.
- Project margin dollars and margin percentage for awarded work.
- Margin by project type and region.
- Shipment detail table with project, planned date, actual date, tons, and variance days.

## Design and accessibility

Use a consistent restrained navy / teal palette, descriptive chart titles, currency and percentage formats, and a visible data-as-of note. Keep stage colors consistent across pages. Add alt text to visuals, ensure readable contrast, and avoid relying on color alone to communicate status.

## Validation before publishing

- Confirm ProjectID is unique in Projects and ShipmentID is unique in Shipments.
- Confirm every Shipments ProjectID exists in Projects.
- Compare total Project count with a distinct count, not a shipment row count.
- Validate quote totals from Projects only; validate shipped tons and on-time results from Shipments only.
- Check that blank actual ship dates are excluded from on-time delivery calculations.
- Label all visuals as synthetic portfolio data.
