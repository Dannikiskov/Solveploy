import time

import pysat.solvers

def run_sat_model(solver_name, cnf_string, params=None):
    # Create solver instance
    print("Looking up solver", flush=True)
    solver = None
    print("SOLVERS:", pysat.solvers, "\n\n", flush=True)
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
        elif line.endswith(' 0'):
            line = line[:-1]
            clause = [int(x) for x in line.split() if x]
            print("CLAUSE: ", clause, flush=True)
            solver.add_clause(clause)



    # Solve the SAT problem
    print("\nSolving the SAT problem...", flush=True)
    t1 = time.time()
    result = solver.solve()
    t2 = time.time() - t1
    print(result, flush=True)
    if result:
        return {"result": str(solver.get_model()), "status": "SATISFIED", "executionTime": t2}
    else: 
        return {"result": "UNSATISFIED", "status": "UNSATISFIABLE", "executionTime": t2}
    
