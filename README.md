
# Manufacturing Machine Monitoring and OEE Analytics

## 1. Project Overview

This project generates synthetic manufacturing data and provides tools to validate production records, detect data anomalies, and calculate preliminary Overall Equipment Effectiveness (OEE) metrics.

The project uses Python and CSV/JSON files to model plants, production lines, machines, products, production orders, shifts, machine state events, production counts, quality inspections, and planned breaks.

## 2. Dataset

The current generated dataset contains:

| Dataset | Expected rows |
|---|---:|
| Plants | 1 |
| Production lines | 5 |
| Machines | 30 |
| Products | 20 |
| Shifts | 270 |
| Production orders | 1,000 |
| Machine state events | 100,000 |
| Production counts | 500,003, including injected anomalies |
| Quality inspections | 500,000 |
| Planned breaks | 270 |

The production-count dataset includes deliberately injected anomaly records. The row counts above describe the current dataset, not necessarily the clean base dataset.

## 3. Project Structure

```text
manufacturing-oee-system/
├── app/
│   └── services/
│       ├── oee_calculator.py
│       ├── oee_report.py
│       ├── anomaly_detector.py
│       ├── count_validator.py
│       └── break_validator.py
├── generator/
│   ├── generate_data.py
│   ├── generate_orders.py
│   ├── generate_events.py
│   ├── generate_counts.py
│   ├── generate_quality.py
│   ├── generate_breaks.py
│   ├── inject_anomalies.py
│   ├── inject_count_anomaly.py
│   ├── check_anomalies.py
│   ├── check_row_counts.py
│   └── validate_data.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── ground_truth/
├── tests/
├── requirements.txt
└── README.md
```

## 4. Requirements

- Python 3.11 or newer, subject to dependency compatibility
- pip
- Git (optional, for version control)

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## 5. Generate Data

Run commands from the project root directory.

The intended generation order is:

```powershell
python -m generator.generate_data
python -m generator.generate_orders
python -m generator.generate_events
python -m generator.generate_counts
python -m generator.generate_quality
python -m generator.generate_breaks
```

The generators use seed `20261022` where implemented. Some scripts overwrite generated CSVs. Review their behavior before rerunning them on data containing injected anomalies.

## 6. Inject Test Anomalies

The project includes examples of:
- Overlapping machine state events
- Invalid scrap quantities
- Production count decreases without correction events

After generating clean data, inject the labelled examples:

```powershell
python -m generator.inject_count_anomaly
python -m generator.inject_anomalies
```

The injection scripts are designed to retain labelled anomaly records. Check the resulting row counts and ground-truth labels after each run.

## 7. Validate Data

Check dataset row counts:

```powershell
python -m generator.check_row_counts
```

Validate primary keys, foreign keys, event intervals, and expected injected anomalies:

```powershell
python -m generator.validate_data
```

Generate the anomaly report:

```powershell
python -m generator.check_anomalies
```

The report is written to:

```text
data/processed/anomaly_report.json
```

## 8. OEE Reports

Generate preliminary machine and shift reports:

```powershell
python -m app.services.oee_report
```

Outputs:

```text
data/processed/oee_by_machine.json
data/processed/oee_by_machine_shift.json
```

OEE combines three metrics:

- Availability = Run Time / Planned Production Time
- Performance = Ideal Cycle Time × Total Count / Run Time
- Quality = Good Count / Total Count

OEE = Availability × Performance × Quality

The current reports have known limitations. Shift-level production counts and run-time alignment must be verified before treating the results as final. Shift durations and planned breaks are currently based on simplified assumptions.

## 9. Run Tests

Run the automated test suite:

```powershell
python -m pytest tests -v
```

The current test suite covers OEE calculations, invalid OEE inputs, overlapping machine states, count decreases, and downtime/break interval checks.

## 10. Current Validation Status

The implemented data validator has passed checks for:
- Unique primary keys
- Valid foreign-key references
- Valid event intervals
- Expected injected overlap anomaly
- Expected injected count anomaly
- No unexpected overlaps or count arithmetic errors under current validation rules

Passing these checks does not mean every challenge requirement is complete. Reproducibility checks, full shift-level OEE accuracy, and remaining data-quality rules still require verification.

## 11. Reproducibility

The intended random seed is:

```text
20261022
```

To establish reproducibility, generate data from a clean state twice using the same seed and compare row counts and file checksums. Perform this test on a backup or clean working copy because generators may overwrite existing CSV files.

## 12. Limitations and Future Improvements

- Add explicit shift end times and planned production time.
- Align production counts and quality inspections to their actual timestamps, machine, order, and shift.
- Validate machine-product ideal cycle-time mappings.
- Associate planned breaks with the correct machines and shifts.
- Improve cumulative count and correction-event modeling.
- Add checksum-based reproducibility tests.
- Add integration tests and CI automation.
- Complete the data dictionary and source manifest.

## 13. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 13. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
