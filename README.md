# Monte Carlo Project Duration Simulation (CSV Version)

This project simulates project completion duration using Monte Carlo methods with PERT distributions and supports advanced task dependencies:

✅ **Supported Dependency Types**:
- Finish-to-Start (FS)
- Start-to-Start (SS)
- Finish-to-Finish (FF)
- Start-to-Finish (SF)

---

## 📁 File Structure

```
monte-carlo-sim/
├── main.py                      # Entry point for simulation
├── simulation.py                # Core logic for PERT and task graph
├── Monte Carlo CSV updated.csv # Sample input file
├── monte_carlo_results.csv     # Output simulation results
├── duration_histogram.png      # Project duration histogram
├── duration_cdf.png            # Cumulative duration chart
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## ▶️ Usage

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the simulation:
   ```bash
   python main.py
   ```

---

## 📥 CSV Input Format

Your CSV should contain the following columns:

| Activity Id | Optimistic Estimate | Most Likely Estimate | Pessimistic Estimate | Dependency   |
|-------------|---------------------|----------------------|----------------------|--------------|
| 1           | 3                   | 5                    | 8                    |              |
| 2           | 2                   | 4                    | 7                    | 1FS          |
| 3           | 5                   | 7                    | 9                    | 1SS;2FS      |
| 4           | 4                   | 5                    | 10                   | 2FF-3SS      |

✅ Use `;` or `-` as separators for multiple dependencies.  
✅ Dependencies like `2FS` mean "Start task 2 when predecessor finishes."

---

## 📈 Output

You will get:
- Printed results:
  ```
  --- Simulation Results ---
  Mean Duration: 44.39
  Median Duration: 44.33
  90th Percentile Duration: 48.27
  Most Likely Critical Path: 1 → 3 → 4 → 5 → 6 → 7
  Confidence in Critical Path: 87.7%
  ```
- `monte_carlo_results.csv`
- `duration_histogram.png`
- `duration_cdf.png`

---

## 🧠 Notes

- Handles task networks with complex dependencies.
- Critical path is estimated based on the most frequently longest path.

---

## 🪪 License

[GNU GPL v3](LICENSE)