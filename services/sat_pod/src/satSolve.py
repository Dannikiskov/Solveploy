import re
import subprocess
import tempfile
import time

import pysat.solvers

def run_sat_model(solver_name, cnf_string, cores=None, params=None):
    if cores == None or cores <= 1 and solver_name != "gimsatul":
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

        for line in cnf_lines:
            if line.startswith('c') or line.startswith('p'):
                # Skip comments and problem line
                pass
            elif line.endswith(' 0'):
                line = line[:-1]
                clause = [int(x) for x in line.split() if x]
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
    
    else:
        if solver_name == "glucose421":
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False) as temp_model_file:
                temp_model_file.write(cnf_string)
                temp_model_path = temp_model_file.name
                temp_model_file.close()
            print(temp_model_path)
            command = ["glucose-syrup", "-model", f"-cpu-lim={cores}", f"{temp_model_path}"]
            print("COMMAND: ", command, flush=True)
            try:
                cmd_result = str(subprocess.run(command, capture_output=True, text=True).stdout)
            except subprocess.CalledProcessError as e:
                print(e, flush=True)
                
            print(cmd_result, flush=True)

            # Extract the number after "c real time : "
            match = re.search(r'c real time : (\d+\.\d+)', cmd_result)
            real_time = None
            if match:
                real_time = match.group(1)

            if cmd_result.strip().split('\n')[-2] == "s SATISFIABLE":       
                last_line = cmd_result.strip().split('\n')[-1]
                if last_line.startswith('v'):
                    last_line = last_line[1:].strip()
                    print({"result": last_line, "status": "SATISFIED", "executionTime": real_time}, flush=True)
                return {"result": last_line, "status": "SATISFIED", "executionTime": real_time}            
            else:
                return {"result": "UNSATISFIED", "status": "UNSATISFIABLE", "executionTime": real_time}
        
        elif solver_name == "gimsatul":
            print("gimsatul")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False) as temp_model_file:
                print("\n", cnf_string, "\n", flush=True)
                temp_model_file.write(cnf_string)
                temp_model_path = temp_model_file.name
                temp_model_file.close()
            print(temp_model_path)
            command = ["gimsatul", f"{temp_model_path}", f"--threads={cores}"]
            print("COMMAND: ", command, flush=True)
            t1 = time.time()
            cmd_result = str(subprocess.run(command, capture_output=True, text=True).stdout)
            real_time = time.time() - t1
            print(cmd_result, flush=True)

            if "s SATISFIABLE" in cmd_result.strip().split('\n'):
                # Extract the lines starting with "v"
                solution_lines = [line for line in cmd_result.strip().split('\n') if line.startswith('v')]

                # Remove the leading "v" and whitespace from each line
                solutions = [line[1:].strip() for line in solution_lines]

                return {"result": solutions, "status": "SATISFIED", "executionTime": real_time}