# govspend.opendata.scot

A static website that visualises Scottish Government payment card spending over £500, sourced from the official monthly reports published at https://www.gov.scot/collections/government-spend-over-gbp500-monthly-reports/

Live site: https://govspend.opendata.scot

## Overview

The site is built with [Eleventy](https://www.11ty.dev/) and deployed to GitHub Pages. Data is scraped from gov.scot using a Python script and stored as JSON files in the repository. A GitHub Actions workflow runs monthly to fetch any newly published reports and rebuild the site automatically.

## Repository structure

```
.
├── .github/
│   └── workflows/
│       ├── build.yml          # Builds and deploys the site on push to main
│       └── update-data.yml    # Monthly cron to fetch new spend reports
├── _assets/
│   ├── css/main.scss          # Bootstrap overrides and site styles
│   └── js/
│       ├── main.js            # JS entry point
│       ├── charts.js          # Highcharts visualisations
│       └── constants.js       # Shared constants (currency formatting)
├── _data/
│   ├── site.js                # Site metadata (name, URL, build time)
│   └── spendsOver500/         # One JSON file per monthly report (YYYY-MM.json)
├── _includes/
│   └── layouts/base.njk       # Base HTML layout
├── index.njk                  # Homepage
├── spendover500.njk           # Monthly detail pages (paginated)
├── spendover500.json.njk      # JSON export pages (/spends/YYYY-MM.json)
├── scrape_data.py             # Data scraper
├── headers.csv                # Column schema log (one row per month)
├── package.json               # Node dependencies and build scripts
└── requirements.txt           # Python dependencies
```

## Data

Each monthly report is stored as `_data/spendsOver500/YYYY-MM.json`. Records follow this schema:

| Field | Description |
|---|---|
| `Directorate` | Scottish Government directorate or department |
| `Merchant Name` | Vendor or supplier name |
| `Merchant Category Name` | Payment category |
| `Transaction Date` | Date of transaction (DD/MM/YYYY) |
| `Transaction Amount` | Value in GBP (numeric) |
| `Expense Description` | Description of the purchase |

Data covers May 2016 onwards and includes only transactions over £500.

## Getting started

### Prerequisites

- Node.js (LTS recommended)
- Python 3.x
- pip

### Fetch spend data

To download all monthly reports from gov.scot:

```bash
pip install requests beautifulsoup4 pandas lxml
python scrape_data.py
```

To only download months that are not already present locally (faster for incremental updates):

```bash
python scrape_data.py --skip-existing
```

### Build the site

```bash
npm install
npm run build
```

The built site is output to `_site/`.

### Run locally

```bash
npm start
```

This starts Eleventy with live reload and the Parcel asset bundler in watch mode.

## Automated data updates

The `update-data.yml` workflow runs at 09:00 UTC on the first of every month. It:

1. Runs `scrape_data.py --skip-existing` to fetch any newly published monthly reports
2. Commits the new JSON files and updated `headers.csv` to `main`
3. Rebuilds and redeploys the site to GitHub Pages

The workflow can also be triggered manually from the Actions tab in GitHub using the `workflow_dispatch` event, which is useful for backfilling missing months.

## Deployment

The site is deployed automatically to GitHub Pages on every push to `main` (via `build.yml`), and also as part of the monthly data update workflow. GitHub Pages should be configured to serve from the `gh-pages` branch.

## License

MIT
