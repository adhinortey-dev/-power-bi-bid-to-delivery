# Data dictionary

## Projects.csv

Grain: one row per fictional bid opportunity. `ProjectID` is unique.

| Field | Meaning |
|---|---|
| ProjectID | Synthetic project key, `PRJ-0001` format. |
| QuoteDate | Date the fictional estimate was prepared. |
| BidDeadline | Date the bid was due. |
| AwardDate | Award date for opportunities in Awarded, Fabrication, Ready for Delivery, or Delivered stages; blank otherwise. |
| DeliveryDate | First planned delivery date for Ready for Delivery or Delivered work; blank otherwise. |
| Customer | Fictional customer organization. |
| Region | Synthetic sales region. |
| CustomerSegment | General Contractor, Public Agency, Developer, or Specialty Contractor. |
| ProjectType | Fictional end-market classification. |
| Estimator | Synthetic employee name. |
| Stage | Current snapshot stage: Bid Review, Estimating, Quote Submitted, Awarded, Fabrication, Ready for Delivery, Delivered, Lost, or No Response. |
| QuotedTons | Estimated reinforcing steel tonnage. |
| QuoteAmount | Synthetic quoted revenue in USD. |
| EstimatedCost | Estimated project cost in USD. |
| AwardedTons | Final awarded tons for awarded work; blank for non-awarded work. |
| ActualCost | Synthetic actual cost for awarded work; blank otherwise. |
| Priority | Standard, High, or Urgent. |

## Shipments.csv

Grain: one row per shipment line. `ShipmentID` is unique and `ProjectID` links to Projects. Projects can have several partial shipments.

| Field | Meaning |
|---|---|
| ShipmentID | Synthetic shipment key. |
| ProjectID | Project key linking to Projects. |
| PlannedShipDate | Planned shipment date. |
| ActualShipDate | Actual shipment date for completed shipments; blank while scheduled. |
| ShipmentTons | Tonnage on this shipment line. |
| ShipmentStatus | Scheduled or Delivered. |

## Assumptions and limitations

- All values are synthetic and intended only for demonstrating analytics methods.
- The dataset is a current-state snapshot, not a stage-change history. It cannot support true stage aging or time-in-stage analysis.
- `No Response` is a synthetic outcome category. Its age is not represented as a separate event history.
- Quote amounts and costs are generated from plausible ranges, not market price observations.
- The synthetic generator intentionally assigns different target win rates by region, changes the share of open and no-response work by quote recency, and varies cost assumptions by project type. These designed patterns make the report useful for practicing segmentation; they are not claims about real markets.
- `DeliveryDate` is a project-level first planned shipment date; delivery reliability is measured at shipment-line grain using planned and actual shipment dates.
- Delivery dates may extend beyond the opportunity-generation date range because awards require fabrication lead time.
- Project attributes such as customer, region, estimator, and type are stored on the project fact source for simpler CSV ingestion. Create dimensions from distinct values in Power Query or the model as described in the guide.
