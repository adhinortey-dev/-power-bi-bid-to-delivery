"""Generate reproducible, entirely fictional construction opportunity data."""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data"
SEED = 4172026
START = date(2024, 1, 1)
END = date(2026, 9, 30)


def write_csv(name: str, rows: list[dict]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    OUT.mkdir(exist_ok=True)
    customers = [
        "Northstar Builders", "Cedarline Construction", "Summit Civic Group",
        "Bluehaven Infrastructure", "Redwood Project Partners", "Keystone Works",
        "Silverline Contractors", "Atlas Urban Development", "Stonebridge General",
        "Pioneer Structures", "Greenfield Build Co.", "Meridian Siteworks",
        "Harborlight Construction", "Ironwood Development", "Clearwater Public Works",
        "Westmark Builders", "Evergreen Contracting", "Crownpoint Civil",
        "Lakeshore Projects", "Brightpath Construction", "Ridgeway Engineering",
        "Oak & River Builders", "Granite Peak Contractors", "Beacon Municipal Group",
    ]
    regions = ["Northeast", "Mid-Atlantic", "Southeast", "Midwest"]
    project_types = ["Multifamily", "Healthcare", "Education", "Civic", "Commercial", "Transportation"]
    segments = ["General Contractor", "Public Agency", "Developer", "Specialty Contractor"]
    estimators = ["Avery Morgan", "Jordan Lee", "Casey Rivera", "Taylor Brooks", "Riley Chen"]
    open_stage_weights = [25, 30, 45]
    won_stage_weights = [20, 30, 18, 32]
    won_stages = {"Awarded", "Fabrication", "Ready for Delivery", "Delivered"}
    regional_win_rates = {"Northeast": .36, "Mid-Atlantic": .42, "Southeast": .50, "Midwest": .32}
    on_time_weights = {
        "Northeast": [8, 12, 55, 10, 6, 4, 3, 2],
        "Mid-Atlantic": [7, 11, 53, 11, 7, 5, 4, 2],
        "Southeast": [6, 10, 48, 13, 8, 6, 6, 3],
        "Midwest": [7, 11, 51, 12, 7, 5, 5, 2],
    }
    cost_ratio_by_type = {"Multifamily": .78, "Healthcare": .84, "Education": .82, "Civic": .87, "Commercial": .80, "Transportation": .85}
    region_decided_counts = {region: 0 for region in regions}
    region_awarded_counts = {region: 0 for region in regions}
    project_rows: list[dict] = []
    shipment_rows: list[dict] = []
    n = 800
    for i in range(1, n + 1):
        offset = rng.randrange((END - START).days + 1)
        quote_date = START + timedelta(days=offset)
        quote_days = rng.randint(20, 45)
        deadline = quote_date + timedelta(days=quote_days)
        region = rng.choice(regions)
        project_type = rng.choice(project_types)
        days_old = (END - quote_date).days
        open_probability = .56 if days_old < 180 else (.43 if days_old < 365 else .32)
        no_response_probability = .10 if days_old < 180 else .17
        draw = rng.random()
        if draw < open_probability:
            stage = rng.choices(["Bid Review", "Estimating", "Quote Submitted"], open_stage_weights, k=1)[0]
        elif draw < open_probability + no_response_probability:
            stage = "No Response"
        else:
            region_decided_counts[region] += 1
            target_awards = int(regional_win_rates[region] * region_decided_counts[region])
            if region_awarded_counts[region] < target_awards:
                region_awarded_counts[region] += 1
                stage = rng.choices(["Awarded", "Fabrication", "Ready for Delivery", "Delivered"], won_stage_weights, k=1)[0]
            else:
                stage = "Lost"
        days_to_award = rng.randint(5, max(8, quote_days - 2)) if stage in won_stages else ""
        award_date = quote_date + timedelta(days=days_to_award) if days_to_award else ""
        tons = round(rng.triangular(18, 760, 180), 1)
        rate = rng.randint(1550, 2350)
        quote_value = round(tons * rate, 2)
        cost_ratio = max(.68, min(.94, rng.gauss(cost_ratio_by_type[project_type], .045)))
        estimated_cost = round(quote_value * cost_ratio, 2)
        actual_tons = round(tons * rng.uniform(.88, 1.12), 1) if stage in won_stages else ""
        actual_cost = round(estimated_cost * rng.uniform(.96, 1.13), 2) if actual_tons != "" else ""
        delivery_date = ""
        if stage in ("Ready for Delivery", "Delivered") and award_date:
            delivery_date = award_date + timedelta(days=rng.randint(25, 105))
        project = f"PRJ-{i:04d}"
        # Use a fixed project horizon so reruns stay stable regardless of execution day.
        project_rows.append({
            "ProjectID": project,
            "QuoteDate": quote_date.isoformat(),
            "BidDeadline": deadline.isoformat(),
            "AwardDate": award_date.isoformat() if award_date else "",
            "DeliveryDate": delivery_date.isoformat() if delivery_date else "",
            "Customer": rng.choice(customers),
            "Region": region,
            "CustomerSegment": rng.choice(segments),
            "ProjectType": project_type,
            "Estimator": rng.choice(estimators),
            "Stage": stage,
            "QuotedTons": f"{tons:.1f}",
            "QuoteAmount": f"{quote_value:.2f}",
            "EstimatedCost": f"{estimated_cost:.2f}",
            "AwardedTons": f"{actual_tons:.1f}" if actual_tons != "" else "",
            "ActualCost": f"{actual_cost:.2f}" if actual_cost != "" else "",
            "Priority": rng.choices(["Standard", "High", "Urgent"], [68, 25, 7], k=1)[0],
        })
        if stage in ("Ready for Delivery", "Delivered") and delivery_date:
            planned = date.fromisoformat(delivery_date.isoformat())
            total = float(actual_tons)
            remaining = total
            shipment_no = 1
            while remaining > 0.05:
                shipment_tons = min(remaining, round(rng.uniform(22, 100), 1))
                if remaining - shipment_tons < 10:
                    shipment_tons = remaining
                planned_ship = planned + timedelta(days=(shipment_no - 1) * rng.randint(1, 4))
                is_delivered = stage == "Delivered"
                delay = rng.choices([-3, -1, 0, 1, 2, 4, 7, 12], on_time_weights[region], k=1)[0]
                actual_ship = planned_ship + timedelta(days=delay) if is_delivered else ""
                shipment_rows.append({
                    "ShipmentID": f"SHP-{i:04d}-{shipment_no:02d}",
                    "ProjectID": project,
                    "PlannedShipDate": planned_ship.isoformat(),
                    "ActualShipDate": actual_ship.isoformat() if actual_ship else "",
                    "ShipmentTons": f"{shipment_tons:.1f}",
                    "ShipmentStatus": "Delivered" if is_delivered else "Scheduled",
                })
                remaining = round(remaining - shipment_tons, 1)
                shipment_no += 1

    write_csv("Projects.csv", project_rows)
    write_csv("Shipments.csv", shipment_rows or [{"ShipmentID": "", "ProjectID": "", "PlannedShipDate": "", "ActualShipDate": "", "ShipmentTons": "", "ShipmentStatus": ""}])
    print(f"Created {len(project_rows)} fictional opportunities and {len(shipment_rows)} fictional shipment records.")


if __name__ == "__main__":
    main()
