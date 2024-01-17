import subprocess
import psycopg2
import tempfile

def query_database(query):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="solver-database-service",
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


def handle_instance(file_data):
    query = f"SELECT * FROM instance WHERE filename = '{file_data['filename']}'"
    exists = query_database(query)

    # Add instance and its feature vector to database if it doesn't already exist
    if not exists:
        query = f"INSERT INTO instance (filename, file_type, content) VALUES ('{file_data['filename']}', '{file_data['file_type']}', '{file_data['content']}') RETURNING id"
        new_instance_id = query_database(query)

        temp_file = tempfile.NamedTemporaryFile(suffix=f".{file_data['filetype']}", delete=False)
        temp_file.write(file_data['content'].encode())

        command = ["mzn2feat", "-i", temp_file.name]
        result = subprocess.run(command, capture_output=True, text=True)
        features = result.stdout.strip()
        feature_vector = [float(number) for number in features.split(",")]
        temp_file.close()

        query = f"INSERT INTO feature_vectors (instance_id, features) VALUES ({new_instance_id}, ARRAY{feature_vector})"
        query_database(query)


def get_solved_count(s, similar_insts, T):
    count = 0
    for inst in similar_insts:
        query = f"SELECT COUNT(*) FROM solving_times WHERE instance_id = {inst} AND solver_id = {s} AND solve_time <= {T}"
        result = query_database(query)
        count += result[0][0]
    return count


def print_all_tables():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    tables = query_database(query)
    print(f"Tables: {tables}", flush=True)
    if tables is not None:
        for table in tables:
            print(table[0], ": ", flush=True)
            query = f"SELECT * FROM {table[0]}"
            print(query_database(query), flush=True)


def init_database():
    
    # Create feature_vectors table
    query = """
        CREATE TABLE IF NOT EXISTS feature_vectors (
            id SERIAL PRIMARY KEY,
            instance_id INT REFERENCES instances(id),
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

    # Insert MiniZinc Default Solvers
    solvers = [
        "Chuffed",
        "COIN-BC",
        "CPLEX",
        "findMUS",
        "Gecode",
        "Globalizer",
        "Gurobi",
        "HiGHS",
        "OR Tools",
        "SCIP",
        "Xpress"
    ]

    for solver in solvers:
        query = f"INSERT INTO solvers (name) SELECT '{solver}' WHERE NOT EXISTS (SELECT 1 FROM solvers WHERE name = '{solver}')"
        query_database(query)


    # Create instance table
    query = """
        CREATE TABLE IF NOT EXISTS instance (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_type VARCHAR(10) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        );
    """
    query_database(query)

    # Create solving_times table
    query = """
        CREATE TABLE IF NOT EXISTS solving_times (
            id SERIAL PRIMARY KEY,
            solver_id INT REFERENCES solvers(id),
            instance_id INT REFERENCES instances(id),
            solve_time FLOAT NOT NULL,
        );

    """
    query_database(query)

     # Create instance_data table
    query = """
        CREATE TABLE IF NOT EXISTS instance_data (
            id SERIAL PRIMARY KEY,
            instance_id INT REFERENCES instance(id) ON DELETE CASCADE,
            filename VARCHAR(255) NOT NULL,
            file_type VARCHAR(10) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        );
    """
    query_database(query)
