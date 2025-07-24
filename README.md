# Monte Carlo Simulation for Project Scheduling

This project estimates project duration and critical paths using Monte Carlo simulation based on task duration estimates and dependencies defined in an ODS spreadsheet.

## Features
- PERT distribution sampling
- Task dependency graph (Finish-Start)
- Histogram and cumulative duration charts
- Critical path estimation

## Usage

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python main.py
```