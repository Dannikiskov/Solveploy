import time
from pysat.examples.rc2 import RC2
from pysat.examples.lbx import LBX
from pysat.formula import WCNF
from pysat.formula import CNF

def run_maxsat_model(solver_name, cnf_string):

    # Split the CNF string into lines
    cnf_lines = cnf_string.strip().split('\n')
    w_formula = WCNF()
    formula = CNF()
    weighted_cnf = False
    # Add clauses to the solver
    print("Adding clauses...\n", flush=True)
    try:
        for line in cnf_lines:
            if line.startswith('c'):
                # Skip comments and problem line
                pass
            elif line.startswith('p'):
                if "wcnf" in line:
                    weighted_cnf = True
            else:
                if weighted_cnf:
                    clause = [int(x) for x in line.split(" ")[:-1]]
                    weight = int(clause[0])
                    weightless_clause = clause[1:]
                    w_formula.append(weightless_clause, weight=weight)
                else:
                    clause = [int(x) for x in line.split(" ")[:-1]]
                    formula.append(clause)

    except Exception as e:
        print("Error: ", e, flush=True)

    model = None
    t1 = None
    t2 = None

    if not weighted_cnf:
        print("computing with formula", formula, flush=True)
        t1 = time.time()
        model = RC2(formula).compute()
        t2 = time.time()
    else:
        t1 = time.time()
        model = RC2(w_formula).compute()
        t2 = time.time()

    print("MAXSAT finished.. with model; ", model, flush=True)
    return {"result": model, "executionTime": t2 - t1}
