# ROW Swim Club — 2026-27 Program Structure

Everything needed to rebuild the 2026-27 schedule documents.

## What this is

A pool schedule for twelve training groups across three venues, with the
documents that explain it to coaches and families. The schedule is held as
data; the documents are generated from it. Change the data, rebuild, and
every document stays consistent.

**Current version: v26.**

## Quick start

```bash
pip install reportlab pdfplumber
cd build && python3 build_all.py
```

Output lands in `output/`.

## Layout

```
data/     the plan and everything that describes it
lib/      shared code and the lane solver
build/    one script per document
output/   generated PDFs
check.py  rule check, run before publishing
```

## The workflow

**1. Edit the plan.** `data/CURRENT.json` holds every session as
`group: [[day, time, venue], ...]`. This is the only file to edit by hand
when changing times.

**2. Re-solve the lanes.**

```bash
python3 lib/solve_lanes.py
```

Assigns each session to specific lanes and writes `data/lane_map.json`.
Reports whether any pool preference had to be relaxed.

**3. Check the rules.**

```bash
python3 check.py
```

Thirteen checks. Exits non-zero if any fail. Do not publish on a failure.

**4. Rebuild.**

```bash
cd build && python3 build_all.py
```

**5. Bump the version.** Edit `data/VERSION`. Filenames carry it, so v26
documents never mix with v27 ones. Move all documents together.

## The documents

| Script | Output | Audience |
|---|---|---|
| `executive_summary.py` | Executive Summary | families, 11 pages |
| `group_schedules.py 12` / `24` | Group Schedules | families, two clock formats |
| `pool_grid.py` | Pool Grid | internal, one day per page |
| `schedules_by_coach.py` | Schedules by Coach | coaches, one section each |

## The data files

| File | Holds |
|---|---|
| `CURRENT.json` | **the plan.** Every session, by group |
| `capacity.json` | maximum swimmers per group |
| `group_names.json` | display name and age descriptor |
| `fixed_lanes.json` | groups with a set lane count (JD1, JD2, TOPS) |
| `lane_overrides.json` | one-off lane counts for specific sessions |
| `pool_pins.json` | which end of WLU a group sits in, by day |
| `tops_options.json` | the five TOPS schedule options |
| `lane_map.json` | **generated.** Do not edit; run the solver |
| `VERSION` | current version string |

## The rules

These govern the schedule and are checked by `check.py`.

1. Lanes fit the water the club holds.
2. Twelve hours between an evening session and the next morning.
3. A maximum session length for every group.
4. Swimmers per lane, by group and by course.
5. Sessions per week rise through each level.
6. Weekly hours rise through each level.
7. Weekday mornings never fall as the level rises.
8. One session a day, except ND and PD1.
9. The Rec Centre is used by the Recreation pathway only.
10. Cameron Heights after 8:00 pm is held for Recreation.
11. No group is split across the two WLU pools.
12. A group keeps the same lanes for a whole session.
13. Competitive groups train at WLU and Cameron Heights.

Rules 11 and 12 are enforced by the solver rather than the checker.

## The venues

**WLU** — two adjoining six lane pools. Lanes 1-6 are the deep end,
7-12 the shallow end. 50 m on Wednesday and Friday mornings.
ND and PD1 have first call on the deep end.

**Cameron Heights** — 6 lanes, weekday evenings and Saturday morning.

**Rec Centre** — mornings only. 5 lanes Monday and Friday, 8 lanes
Tuesday to Thursday. Recreation pathway only.

## The groups

Numbers count down as a swimmer moves up.

| Pathway | Groups |
|---|---|
| National | ND — 18 & Under |
| Provincial | PD1 — 18 & Under, PD2 — 14 & Under, PD3 — 12 & Under |
| Regional | SD — 18 & Under, AGD 1 — 14 & Under, AGD 2 — 12 & Under |
| Junior | JD1, JD2, TOPS 3x (2 options), TOPS 2x (3 options) |
| Recreation | REC AM (mornings), REC PM (evenings) |
| Foundation | ROW Swim Academy |

Internal keys in `CURRENT.json` are historical: `RD` means Regional,
`PD` Provincial. `group_names.json` maps them to display names.

## Open items

- Recreation: whether swimmers choose 3 or 5 sessions from the 8 available,
  or the AM/PM split stays fixed. Awaiting input.
- AGD 1 and AGD 2 both publish a capacity of 36, against a combined roster
  of about 70. Little headroom.
- Fees are published with registration by mid-August.
- Coach review of the draft schedules is outstanding.
