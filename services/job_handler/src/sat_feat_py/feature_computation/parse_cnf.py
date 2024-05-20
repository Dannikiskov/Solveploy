
def parse_cnf(cnf_string):
    """
    Parse number of variables, number of clauses and the clauses from a standard .cnf file
    :param cnf_path:
    :return: clauses, number of clauses, and number of variables
    """
    
    clauses_list = []
    c = 0
    v = 0

    for line in cnf_string.strip().split('\n'):
        if line[0] == 'c':
            continue
        if line[0] == 'p':
            sizes = line.split()
            v = int(sizes[2])
            c = int(sizes[3])

        elif line.endswith(' 0'):
            # all following lines should represent a clause, so literals separated by spaces, with a 0 at the end,
            # denoting the end of the line.
            line = line[:-1]
            clause = [int(x) for x in line.split() if x]
            clauses_list.append(clause)

    c = len(clauses_list)
    v = max([abs(l) for clause in clauses_list for l in clause])

    return clauses_list, c, v
