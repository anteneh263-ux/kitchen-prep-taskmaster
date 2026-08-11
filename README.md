# Kitchen Prep Taskmaster

Kitchen Prep Taskmaster is an autonomous kitchen-planning agent for restaurant teams. It turns demand signals, bookings, menu data, inventory, and weather into a practical daily prep plan—reducing manual planning, avoidable waste, and stockouts.

## Problem

Restaurant kitchens spend significant time every day on prep planning, inventory control, FEFO rotation, and purchase suggestions. These tasks combine uncertain demand with strict operational rules, making them time-consuming and error-prone.

## Solution

The agent runs automatically each morning. It forecasts demand, calculates ingredient requirements, checks available inventory using FEFO, identifies prep shortages, proposes purchases, and publishes a mobile-friendly daily briefing with a step-by-step run log.

## Features

- Automatic daily run at 07:00
- Gemini-based demand forecasting
- Deterministic ingredient calculations
- FEFO inventory allocation and waste warnings
- Prep shortages and purchase suggestions
- Deterministic fallback when AI or network services are unavailable
- Mobile-friendly daily plan
- Step-by-step execution log
- Idempotent scheduled runs
- Human approval for menu changes

## Architecture

![Kitchen Prep Taskmaster architecture](docs/architecture.png)

A scheduled request starts the FastAPI service on Cloud Run. The orchestrator loads data from Firestore and weather data from Open-Meteo, asks Gemini for a demand forecast, performs authoritative calculations in Python, asks Gemini to prioritize and explain the result, validates the output, and stores the plan and run log in Firestore.

## How Gemini Is Used

Gemini is used for two bounded reasoning tasks:

1. **Demand forecasting** — Gemini evaluates contextual signals such as recent sales, bookings, menu information, and weather to produce a structured forecast.
2. **Prioritization and briefing** — Gemini converts the verified calculation results into a clear, actionable kitchen briefing.

All authoritative mathematics, inventory allocation, FEFO logic, safety rules, and final validation are performed in Python. Gemini does not directly modify inventory or approve menu changes.

## Technology

- Gemini 3.5 Flash
- Google Agent Development Kit (ADK)
- Google Cloud Run
- Google Cloud Scheduler
- Google Cloud Firestore
- FastAPI
- Open-Meteo
- Python

## Data Sources

- Open-Meteo weather data
- Synthetic menu data
- Synthetic sales history
- Synthetic inventory and booking data

No real restaurant data, trade secrets, or personally identifiable information is used.

## Local Setup

### Requirements

- Python 3.10+
- A Google API key

### Installation

```bash
git clone https://github.com/anteneh263-ux/kitchen-prep-taskmaster.git
cd kitchen-prep-taskmaster
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your API key to `.env`. Never commit `.env` or credentials.

### Generate Data

```bash
python scripts/generate_sales_history.py
python scripts/verify_data.py
```

### Run Tests

```bash
pytest -m "not integration"
```

### Run Locally

```bash
python -m kitchen_prep.orchestrator --date 2026-08-14
```

## Google Cloud Deployment

1. Create or select a Google Cloud project.
2. Enable Cloud Run, Cloud Build, Firestore, Secret Manager, and Cloud Scheduler APIs.
3. Create a Firestore database in an appropriate region.
4. Store the Google API key in Secret Manager; never place it in source code or deployment commands.
5. Build and deploy the FastAPI service to Cloud Run.
6. Give the service account only the minimum required Firestore and Secret Manager permissions.
7. Configure runtime environment variables without committing secrets.
8. Create an authenticated Cloud Scheduler job that sends `POST /runs/daily` to Cloud Run at 07:00 in the desired timezone.
9. Run a manual request, inspect the stored run log, and verify that repeated requests for the same date are idempotent.
10. Add the deployed URL to the Demo section below.

Do not commit real project IDs, API keys, credentials, or other secrets.

## API Endpoints

### Start daily run

```http
POST /runs/daily
```

Starts an idempotent daily planning run.

### View latest plan

```http
GET /plans/latest
```

Returns the latest validated daily plan.

## Safety and Reliability

- Gemini output is schema-validated before use.
- Programming errors are surfaced and are not disguised as model failures.
- Deterministic fallback is used for model and network failures.
- Scheduler-triggered runs are idempotent.
- Menu changes require human approval.
- The execution log is saved even when a run fails.
- Secrets are stored outside the repository.

## Testing

The test suite covers:

- **Future leakage:** forecasts cannot use information unavailable at prediction time.
- **FEFO:** inventory with the earliest expiration date is consumed first.
- **Double counting:** the same demand or inventory quantity is not counted twice.
- **Fallback:** deterministic output is produced when Gemini or network calls fail.
- **Briefing contract:** the generated briefing follows the expected schema and content rules.
- **Local pipeline:** the complete local workflow produces a valid daily plan.
- **Gemini integration:** integration tests verify structured requests and responses separately from the default offline suite.

## Known Limitation

The purchase calculation does not yet model intermediate demand during supplier lead times longer than one day. Purchase suggestions should therefore be reviewed by a human when lead time exceeds one day.

## Findings and Learnings

The main learning is that Gemini is effective at judgment, contextual interpretation, prioritization, and explanation, while Python is the right place for authoritative calculations, inventory accounting, validation, and safety rules.

During development, testing exposed a double-counting bug in which a quantity could be included in more than one stage of the planning pipeline. Explicit data contracts and deterministic tests were added to prevent the same demand or inventory quantity from being counted twice.

## Demo

- Hosted URL: **TO BE ADDED**
- Demo video: **TO BE ADDED**
- Architecture diagram: [docs/architecture.png](docs/architecture.png)

## Repository Structure

```text
kitchen-prep-taskmaster/
├── README.md
├── kitchen_prep/          # Agent, orchestration, calculations, and API
├── tests/                 # Unit, contract, pipeline, and integration tests
├── scripts/               # Synthetic data generation and verification
├── docs/
│   └── architecture.png   # Architecture diagram
├── requirements.txt
└── .env.example
```

## Privacy

All restaurant, menu, sales, booking, and inventory data in this project is synthetic. No real restaurant data, confidential business information, or customer information is included.

## License

This project is intended to be released under the MIT License. Add a root-level `LICENSE` file before distribution.
