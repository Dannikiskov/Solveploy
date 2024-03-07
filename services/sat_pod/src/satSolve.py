import minizinc
import tempfile
import os
import time
import pysat.solvers

def run_sat_model(cnf_string, solver_name):
    # Create a Glucose3 solver instance
    solver = pysat.solvers.SolverNames[solver_name]()

    # Split the CNF string into lines
    cnf_lines = cnf_string.strip().split('\n')

    # Add clauses to the solver
    for line in cnf_lines:
        if line.startswith('c') or line.startswith('p'):
            # Skip comments and problem line
            pass  # Add an indented block here
        else:
            clause = list(map(int, line.split()[:-1]))
            solver.add_clause(clause)

    # Solve the SAT problem
    result = solver.solve()

    if result:
        return solver.get_model()
    else:
        return "Unsatisfiable."

