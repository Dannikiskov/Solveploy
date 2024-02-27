import subprocess
import psycopg2
import tempfile

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


    temp_file = tempfile.NamedTemporaryFile(suffix=".mzn", delete=False)
    temp_file.write(data['mznFileContent'].encode())

    command = ["mzn2feat", "-i", temp_file.name]
    result = subprocess.run(command, capture_output=True, text=True)
    features = result.stdout.strip()
    feature_vector = [float(number) for number in features.split(",")]
    temp_file.close()

    query = f"SELECT id FROM feature_vectors WHERE features = ARRAY{feature_vector}"
    feat_id = query_database(query)
    if not feat_id:
        query = f"INSERT INTO feature_vectors (features) VALUES (ARRAY{feature_vector}) RETURNING id"
        result = query_database(query)
    
    query = f"INSERT INTO "




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

    # Create feature_vectors table
    query = """
        CREATE TABLE IF NOT EXISTS feature_vectors (
            id SERIAL PRIMARY KEY,
            features FLOAT[]
        );
    """
    query_database(query)

    # Create solvers table
    query = """
        CREATE TABLE IF NOT EXISTS solvers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
    """
    query_database(query)

    # Create solver_featvec_time table
    query = """
        CREATE TABLE IF NOT EXISTS solver_featvec_time (
            id SERIAL PRIMARY KEY,
            solver_id INT REFERENCES solvers(id),
            feature_vec_id INT REFERENCES feature_vectors(id),
            solve_time FLOAT NOT NULL
        );
    """
    query_database(query)