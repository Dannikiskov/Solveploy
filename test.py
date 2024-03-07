from pysat.solvers import Glucose3

def solve_sat_problem(cnf_string):
    # Create a Glucose3 solver instance
    solver = Glucose3()

    # Split the CNF string into lines
    cnf_lines = cnf_string.strip().split('\n')

    # Add clauses to the solver
    for line in cnf_lines:
        if line.startswith('c') or line.startswith('p'):
            # Skip comments and problem line
            pass  # Add an indented block here
        else:
            clause = list(map(int, line.split()[:-1]))
            print(clause)
            solver.add_clause(clause)

    # Solve the SAT problem
    result = solver.solve()

    if result:
        print("Satisfiable. Model:", solver.get_model())
    else:
        print("Unsatisfiable.")

# Example Usage
cnf_string = '''
c  simple_v3_c2.cnf
c
p cnf 3 2
1 -3 0
2 3 -1 0
'''
#print(cnf_string)
#solve_sat_problem(cnf_string)

cadical103  = ('cd', 'cd103', 'cdl', 'cdl103', 'cadical103')
cadical153  = ('cd15', 'cd153', 'cdl15', 'cdl153', 'cadical153')
cryptosat   = ('cms', 'cms5', 'crypto', 'crypto5', 'cryptominisat', 'cryptominisat5')
gluecard3   = ('gc3', 'gc30', 'gluecard3', 'gluecard30')
gluecard41  = ('gc4', 'gc41', 'gluecard4', 'gluecard41')
glucose3    = ('g3', 'g30', 'glucose3', 'glucose30')
glucose4    = ('g4', 'g41', 'glucose4', 'glucose41')
glucose42   = ('g42', 'g421', 'glucose42', 'glucose421')
lingeling   = ('lgl', 'lingeling')
maplechrono = ('mcb', 'chrono', 'maplechrono')
maplecm     = ('mcm', 'maplecm')
maplesat    = ('mpl', 'maple', 'maplesat')
mergesat3   = ('mg3', 'mgs3', 'mergesat3', 'mergesat30')
minicard    = ('mc', 'mcard', 'minicard')
minisat22   = ('m22', 'msat22', 'minisat22')
minisatgh   = ('mgh', 'msat-gh', 'minisat-gh')

print(cadical103[-1])
print(cadical153)
print(cryptosat)
print(gluecard3)
print(gluecard41)
print(glucose3)
print(glucose4)
print(glucose42)
print(lingeling)
print(maplechrono)
print(maplecm)
print(maplesat)
print(mergesat3)
print(minicard)
print(minisat22)
print(minisatgh)