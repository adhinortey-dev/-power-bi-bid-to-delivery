"""Build a local HTML visual prototype and computed findings from the synthetic CSVs."""
from __future__ import annotations

import csv
import html
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_csv(filename: str) -> list[dict[str, str]]:
    with (ROOT / "data" / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def money(value: float) -> str:
    return "$" + format(value, ",.0f")


def main() -> None:
    projects = read_csv("Projects.csv")
    shipments = read_csv("Shipments.csv")
    counts = Counter(row["Stage"] for row in projects)
    revenue = sum(float(row["QuoteAmount"]) for row in projects if row["Stage"] in {"Awarded", "Fabrication", "Ready for Delivery", "Delivered"})
    cost = sum(float(row["ActualCost"]) for row in projects if row["ActualCost"])
    open_value = sum(float(row["QuoteAmount"]) for row in projects if row["Stage"] in {"Bid Review", "Estimating", "Quote Submitted"})
    awarded_count = sum(counts[s] for s in ["Awarded", "Fabrication", "Ready for Delivery", "Delivered"])
    decided_count = awarded_count + counts["Lost"]
    submitted_count = sum(counts[s] for s in ["Quote Submitted", "Awarded", "Fabrication", "Ready for Delivery", "Delivered", "Lost", "No Response"])
    completed = [s for s in shipments if s["ShipmentStatus"] == "Delivered" and s["ActualShipDate"]]
    on_time = sum(s["ActualShipDate"] <= s["PlannedShipDate"] for s in completed)
    regional = defaultdict(lambda: [0, 0])
    for p in projects:
        if p["Stage"] in {"Awarded", "Fabrication", "Ready for Delivery", "Delivered", "Lost"}:
            regional[p["Region"]][1] += 1
            regional[p["Region"]][0] += p["Stage"] in {"Awarded", "Fabrication", "Ready for Delivery", "Delivered"}

    max_count = max(counts.values())
    stage_rows = "".join(
        f'<div class="bar-row"><span>{html.escape(stage)}</span><div class="bar-track"><i style="width:{counts[stage] / max_count * 100:.1f}%"></i></div><b>{counts[stage]}</b></div>'
        for stage in ["Bid Review", "Estimating", "Quote Submitted", "Awarded", "Fabrication", "Ready for Delivery", "Delivered", "Lost", "No Response"]
    )
    region_rows = "".join(
        f'<div class="region-row"><span>{html.escape(region)}</span><div class="bar-track"><i style="width:{(won / total * 100 if total else 0):.1f}%"></i></div><b>{won / total:.0%}</b><small>{won}/{total} decided</small></div>'
        for region, (won, total) in sorted(regional.items())
    )
    finding_region = max(regional, key=lambda r: regional[r][0] / regional[r][1] if regional[r][1] else 0)
    findings = [
        f"{money(open_value)} sits in Bid Review, Estimating, or Quote Submitted.",
        f"{awarded_count} of {decided_count} decided quotes are awarded ({awarded_count / decided_count:.1%} win rate). No Response is excluded from the decided denominator.",
        f"Awarded work has {money(revenue - cost)} gross margin ({(revenue - cost) / revenue:.1%} of quoted awarded revenue).",
        f"{on_time / len(completed):.1%} of completed shipment lines arrived on or before plan; the strongest region by decided-quote win rate is {finding_region}.",
    ]
    findings_html = "".join(f"<li>{html.escape(item)}</li>" for item in findings)
    on_time_pct = on_time / len(completed) if completed else 0
    html_doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>From Bid to Delivery | Portfolio Preview</title>
<style>
:root{{--bg:#f2f5f7;--surface:#fff;--ink:#172c40;--muted:#687b8d;--line:#e0e7ec;--teal:#1c8584;--navy:#15364d;--mint:#e7f4f1;--orange:#c67c37}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px 'Segoe UI',Arial,sans-serif}}.shell{{max-width:1440px;margin:auto;padding:28px 36px}}header{{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:24px}}.eyebrow{{font-size:10px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--teal)}}h1{{margin:6px 0;font-size:30px;letter-spacing:-.04em}}.sub{{color:var(--muted);margin:0}}.badge{{background:#e6f2ee;color:#28765f;padding:8px 12px;border-radius:99px;font-size:10px;font-weight:800;letter-spacing:.06em}}.layout{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.kpis{{grid-column:1/-1;display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.card,.panel{{background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:0 8px 24px #1a3a4b0a}}.card{{padding:17px 19px;border-top:3px solid var(--teal)}}.card:nth-child(2){{border-top-color:#7583b6}}.card:nth-child(3){{border-top-color:#4a9c76}}.card:nth-child(4){{border-top-color:var(--orange)}}.label{{color:var(--muted);font-size:10px;font-weight:750;letter-spacing:.1em;text-transform:uppercase}}.value{{font-size:30px;font-weight:750;letter-spacing:-.05em;margin:10px 0 2px;font-variant-numeric:tabular-nums}}.hint{{color:var(--muted);font-size:10px}}.panel{{padding:19px 21px}}h2{{font-size:15px;margin:0 0 5px}}.caption{{color:var(--muted);font-size:10px;margin:0 0 17px}}.bar-row,.region-row{{display:grid;grid-template-columns:125px 1fr 34px;gap:9px;align-items:center;margin:10px 0;font-size:10px}}.bar-row span,.region-row span{{color:#52687b}}.bar-track{{height:8px;border-radius:10px;background:#edf1f4;overflow:hidden}}.bar-track i{{display:block;height:100%;border-radius:10px;background:linear-gradient(90deg,#1c8584,#52b8aa)}}.bar-row:nth-child(3n) .bar-track i{{background:linear-gradient(90deg,#7383b7,#9ba8d0)}}.bar-row b,.region-row b{{text-align:right;font-variant-numeric:tabular-nums}}.region-row{{grid-template-columns:90px 1fr 38px 72px}}.region-row small{{color:var(--muted);font-size:9px}}.findings{{grid-column:1/-1;background:linear-gradient(115deg,#12354a,#1d565d);color:white;border:0}}.findings h2{{font-family:Georgia,serif;font-weight:500;font-size:19px}}.findings .caption{{color:#c4d7dc}}.findings ul{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding-left:17px;margin:12px 0 0}}.findings li{{font-size:11px;line-height:1.55;padding-right:8px}}footer{{color:var(--muted);font-size:9px;margin-top:14px;display:flex;justify-content:space-between}}@media(max-width:850px){{.shell{{padding:20px}}.kpis{{grid-template-columns:repeat(2,1fr)}}.layout{{grid-template-columns:1fr}}.findings ul{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:520px){{header{{align-items:flex-start;gap:12px;flex-direction:column}}.shell{{padding:14px}}.kpis{{grid-template-columns:1fr 1fr;gap:8px}}.card{{padding:12px}}.value{{font-size:23px}}.panel{{padding:15px}}.bar-row{{grid-template-columns:95px 1fr 25px}}.region-row{{grid-template-columns:70px 1fr 30px}}.region-row small{{display:none}}.findings ul{{grid-template-columns:1fr}}}}@media print{{body{{background:#fff}}.shell{{max-width:none;padding:12mm}}.card,.panel{{box-shadow:none;break-inside:avoid}}}}
</style></head><body><main class="shell"><header><div><div class="eyebrow">Commercial Operations · Power BI Portfolio</div><h1>From Bid to Delivery</h1><p class="sub">A fictional rebar supplier's opportunity, margin, and shipment performance</p></div><div class="badge">100% SYNTHETIC DATA</div></header>
<section class="layout"><div class="kpis"><article class="card"><div class="label">Open pipeline</div><div class="value">{money(open_value)}</div><div class="hint">Bid Review · Estimating · Quote Submitted</div></article><article class="card"><div class="label">Submitted quotes</div><div class="value">{submitted_count:,}</div><div class="hint">Current snapshot, distinct projects</div></article><article class="card"><div class="label">Win rate</div><div class="value">{awarded_count / decided_count:.1%}</div><div class="hint">Awards ÷ decided quotes</div></article><article class="card"><div class="label">On-time shipments</div><div class="value">{on_time_pct:.1%}</div><div class="hint">Delivered lines on or before plan</div></article></div>
<section class="panel"><h2>Opportunity mix</h2><p class="caption">Project count by current stage · {len(projects):,} opportunities</p>{stage_rows}</section>
<section class="panel"><h2>Win rate by region</h2><p class="caption">Awarded projects divided by awarded plus lost quotes; No Response excluded</p>{region_rows}</section>
<section class="panel"><h2>Awarded work economics</h2><p class="caption">Project-level amounts; shipment rows do not duplicate revenue</p><div class="bar-row"><span>Awarded revenue</span><div class="bar-track"><i style="width:100%"></i></div><b>{money(revenue)}</b></div><div class="bar-row"><span>Actual cost</span><div class="bar-track"><i style="width:{(cost / revenue * 100 if revenue else 0):.1f}%;background:linear-gradient(90deg,#c67c37,#e2a15c)"></i></div><b>{money(cost)}</b></div><div class="bar-row"><span>Gross margin</span><div class="bar-track"><i style="width:{((revenue-cost) / revenue * 100 if revenue else 0):.1f}%;background:linear-gradient(90deg,#4a9c76,#74c395)"></i></div><b>{money(revenue-cost)}</b></div></section>
<section class="panel findings"><h2>Example findings from the generated dataset</h2><p class="caption">These are descriptive results from this synthetic snapshot, not industry benchmarks.</p><ul>{findings_html}</ul></section></section>
<footer><span>Portfolio prototype · Generated from local synthetic CSVs</span><span>{len(projects):,} projects · {len(shipments):,} shipment lines · USD</span></footer></main></body></html>'''
    (ROOT / "PORTFOLIO_PREVIEW.html").write_text(html_doc, encoding="utf-8")
    (ROOT / "SAMPLE_FINDINGS.md").write_text(
        "# Example findings\n\nThese figures are calculated from the included synthetic snapshot. They are not real company results or industry benchmarks.\n\n" + "\n".join(f"- {finding}" for finding in findings) + "\n",
        encoding="utf-8",
    )
    print(f"Built preview and findings for {len(projects)} projects and {len(shipments)} shipment rows.")


if __name__ == "__main__":
    main()
