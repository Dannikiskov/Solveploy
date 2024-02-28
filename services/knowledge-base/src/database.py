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
    else:
        result = None

    conn.commit()
    cur.close()
    conn.close()

    return result


def get_all_feature_vectors():
    query = "SELECT features FROM feature_vectors"
    return query_database(query)


def handle_instance(data):
    feature_vector = str(data["featureVector"])
    solver_name = data["solverName"]
    execution_time = data["executionTime"]

    query = f"SELECT id FROM solvers WHERE name = '{solver_name}'"
    solver_id = query_database(query)
    if not solver_id:
        query = f"INSERT INTO solvers (name) VALUES ('{solver_name}') RETURNING id"
        solver_id = query_database(query)

    query = f"INSERT INTO feature_vectors (features) VALUES ('{feature_vector}') RETURNING id"
    feat_id = query_database(query)
    if not feat_id:
        query = f"INSERT INTO feature_vectors (features) VALUES ('{feature_vector}') RETURNING id"
        feat_id = query_database(query)
        print("FEAT ID::::", feat_id, flush=True)

    print(feat_id)

    query = f"SELECT * FROM solver_featvec_time WHERE solver_id = '{solver_id}' AND feature_vec_id = '{feat_id[0][0]}' AND execution_time = '{execution_time}'"
    existing_entry = query_database(query)

    if not existing_entry:
        query = f"INSERT INTO solver_featvec_time (solver_id, feature_vec_id, execution_time) VALUES ('{solver_id}', '{feat_id[0][0]}', '{execution_time}')"
        query_database(query)

    print_all_tables()




def get_solved(solvers, similar_insts, T):
    resultList = []
    for s in solvers:
        query = f"SELECT * FROM solving_times WHERE solver_id = {s.id} AND instance_id IN ({', '.join(inst.id for inst in similar_insts)}) AND solve_time < {T}"
        
        result = query_database(query)
        resultList.append(result)
    return resultList


def get_solved_times(solver_id, similar_insts):
    query = f"SELECT * FROM solving_times WHERE solver_id = {solver_id} AND instance_id IN ({', '.join(str(inst.id) for inst in similar_insts)})"
    results = query_database(query)
    return results


def get_solvers():
    query = "SELECT * FROM solvers"
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

    query = """
        CREATE TABLE IF NOT EXISTS feature_vectors (
            id SERIAL PRIMARY KEY,
            features VARCHAR(2047) UNIQUE
        );
    """
    query_database(query)


    query = """
        CREATE TABLE IF NOT EXISTS solvers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
    """
    query_database(query)


    query = """
        CREATE TABLE IF NOT EXISTS solver_featvec_time (
            id SERIAL PRIMARY KEY,
            solver_id INT REFERENCES solvers(id),
            feature_vec_id INT REFERENCES feature_vectors(id),
            execution_time FLOAT NOT NULL
        );
    """
    query_database(query)