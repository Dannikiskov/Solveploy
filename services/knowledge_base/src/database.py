import subprocess
import psycopg2


def query_database(query):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="knowledge-base-database-service",
        database="postgres",
        user="postgres",
        password="postgres"
    )

    cur = conn.cursor()

    cur.execute(query)

    if(cur.description):
        result = cur.fetchall()
        result = [item[0] for item in result] if len(result) == 1 else result

    else:
        result = None

    conn.commit()
    cur.close()
    conn.close()

    return result


# SAT
def handle_sat_instance(data):
    feature_vector = str(data["featureVector"])
    solver_name = data["solverName"]
    execution_time = data["executionTime"]

    query = f"SELECT id FROM sat_solvers WHERE name = '{solver_name}'"
    solver_id = query_database(query)
    if not solver_id:
        query = f"INSERT INTO sat_solvers (name) VALUES ('{solver_name}') RETURNING id"
        solver_id = query_database(query)

    query = f"SELECT id FROM sat_feature_vectors WHERE features = '{feature_vector}'"
    feat_id = query_database(query)
    if not feat_id:
        query = f"INSERT INTO sat_feature_vectors (features) VALUES ('{feature_vector}') RETURNING id"
        feat_id = query_database(query)

    print(feat_id)

    query = f"SELECT * FROM sat_solver_featvec_time WHERE solver_id = '{solver_id[0]}' AND feature_vec_id = '{feat_id[0]}' AND execution_time = '{execution_time}'"
    existing_entry = query_database(query)

    if not existing_entry:
        query = f"INSERT INTO sat_solver_featvec_time (solver_id, feature_vec_id, execution_time) VALUES ('{solver_id[0]}', '{feat_id[0]}', '{execution_time}')"
        query_database(query)

    print_all_tables()


# MZN
def get_all_mzn_feature_vectors():
    query = "SELECT features FROM mzn_feature_vectors"
    return query_database(query)

def handle_mzn_instance(data):
    feature_vector = str(data["featureVector"])
    solver_name = data["solverName"]
    execution_time = data["executionTime"]

    query = f"SELECT id FROM mzn_solvers WHERE name = '{solver_name}'"
    solver_id = query_database(query)
    if not solver_id:
        query = f"INSERT INTO mzn_solvers (name) VALUES ('{solver_name}') RETURNING id"
        solver_id = query_database(query)

    query = f"SELECT id FROM mzn_feature_vectors WHERE features = '{feature_vector}'"
    feat_id = query_database(query)
    if not feat_id:
        query = f"INSERT INTO mzn_feature_vectors (features) VALUES ('{feature_vector}') RETURNING id"
        feat_id = query_database(query)

    print(feat_id)

    query = f"SELECT * FROM mzn_solver_featvec_time WHERE solver_id = '{solver_id[0]}' AND feature_vec_id = '{feat_id[0]}' AND execution_time = '{execution_time}'"
    existing_entry = query_database(query)

    if not existing_entry:
        query = f"INSERT INTO mzn_solver_featvec_time (solver_id, feature_vec_id, execution_time) VALUES ('{solver_id[0]}', '{feat_id[0]}', '{execution_time}')"
        query_database(query)

    print_all_tables()




def get_solved_mzn(solvers, similar_insts, T):
    resultList = []
    for s in solvers:
        query = f"SELECT * FROM mzn_solving_times WHERE solver_id = {s.id} AND instance_id IN ({', '.join(inst.id for inst in similar_insts)}) AND solve_time <= {T}"
        
        result = query_database(query)
        resultList.append(result)
    return resultList


def get_solved_times_mzn(solver_id, similar_insts):
    query = f"SELECT * FROM mzn_solving_times WHERE solver_id = {solver_id} AND instance_id IN ({', '.join(str(inst.id) for inst in similar_insts)})"
    results = query_database(query)
    return results


def get_mzn_solvers():
    query = "SELECT * FROM mzn_solvers"
    return query_database(query)


def print_all_tables():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    tables = query_database(query)
    print(f"Tables: {tables}", flush=True)
    if tables is not None:
        for table in tables:
            print(table[0], ": ", flush=True)
            query = f"SELECT * FROM {table[0]}"
            print(query_database(query), flush=True)


def database_init():

    # MZN tables
    query = """
        CREATE TABLE IF NOT EXISTS mzn_feature_vectors (
            id SERIAL PRIMARY KEY,
            features VARCHAR(2047) UNIQUE
        );
    """
    query_database(query)


    query = """
        CREATE TABLE IF NOT EXISTS mzn_solvers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
    """
    query_database(query)


    query = """
        CREATE TABLE IF NOT EXISTS mzn_solver_featvec_time (
            id SERIAL PRIMARY KEY,
            solver_id INT REFERENCES solvers(id),
            feature_vec_id INT REFERENCES feature_vectors(id),
            execution_time FLOAT NOT NULL
        );
    """
    query_database(query)

    # SAT tables
    query = """
        CREATE TABLE IF NOT EXISTS sat_feature_vectors (
            id SERIAL PRIMARY KEY,
            features VARCHAR(2047) UNIQUE
        );
    """
    query_database(query)


    query = """
        CREATE TABLE IF NOT EXISTS sat_solvers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
    """
    query_database(query)


    query = """
        CREATE TABLE IF NOT EXISTS sat_solver_featvec_time (
            id SERIAL PRIMARY KEY,
            solver_id INT REFERENCES solvers(id),
            feature_vec_id INT REFERENCES feature_vectors(id),
            execution_time FLOAT NOT NULL
        );
    """
    query_database(query)