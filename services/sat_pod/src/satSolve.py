import time

import pysat.solvers

def run_sat_model(solver_name, cnf_string):
    # Create a Glucose3 solver instance
    print("Looking up solver", flush=True)
    solver = None
    for attr in dir(pysat.solvers.SolverNames):
        if not attr.startswith('__'):
            for val in getattr(pysat.solvers.SolverNames, attr):
                if solver_name in val:
                    solver = pysat.solvers.Solver(solver_name)

    # Split the CNF string into lines
    cnf_lines = cnf_string.strip().split('\n')

    # Add clauses to the solver
    print("Adding clauses...\n", flush=True)
    for line in cnf_lines:
        if line.startswith('c') or line.startswith('p'):
            # Skip comments and problem line
            pass
        else:
            clause = list(map(int, line.split()))
            print("CLAUSE: ", clause, flush=True)
            solver.add_clause(clause)



    # Solve the SAT problem
    t1 = time.time()

    print("\nSolving the SAT problem...", flush=True)
    result = solver.solve()
    t2 = time.time()

    if result:
        print("SAT problem solved successfully.", flush=True)
        return {"result": solver.get_model(), "executionTime": t2 - t1}
    else:
        print("Unsatisfiable.", flush=True)
        return {"result": "Unsatisfiable.", "executionTime": t2 - t1}
