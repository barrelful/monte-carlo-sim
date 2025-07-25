import os
import sys

# Add the 'src' folder to the Python module search path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src/monte_carlo_sim"))

from simulation import run_simulation

if __name__ == "__main__":
    input_file = "data/Monte Carlo CSV updated.csv"  # CSV input file in project root
    iterations = 10000  # Number of Monte Carlo iterations

    run_simulation(input_file, iterations)
