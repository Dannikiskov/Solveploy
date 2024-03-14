from pysat.examples.lbx import LBX
from pysat.formula import WCNF

def solve_maxsat(formula, solver='LBX'):
    if solver == 'LBX':
        with LBX(formula) as lbx_solver:
            model = lbx_solver.compute()
            return model

# Create a WCNF formula
formula = WCNF()

# Add some clauses to the formula
# (replace this with your actual clauses)
formula.append([1], weight=1) 
formula.append([2], weight=100)
formula.append([-1], weight=1) 

# Solve the MaxSAT problem
model = solve_maxsat(formula, solver='LBX')

# Print the solution
print(model)