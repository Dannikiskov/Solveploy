import psycopg2


def query_database(query, params=None):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="knowledge-base-database-service",
        database="postgres",
        user="postgres",
        password="postgres"
    )

    cur = conn.cursor()

    cur.execute(query, params)

    if(cur.description):
        result = cur.fetchall()
        result = [item[0] for item in result] if len(result) == 1 else result

    else:
        result = None

    conn.commit()
    cur.close()
    conn.close()
    
    return result


# MAXSAT
def handle_maxsat_instance(data):
    feature_vector = str(data["featureVector"])
    solver_name = data["solverName"]
    execution_time = data["executionTime"]

    query = f"SELECT id FROM maxsat_solvers WHERE name = '{solver_name}'"
    solver_id = query_database(query)
    if not solver_id:
        query = f"INSERT INTO maxsat_solvers (name) VALUES ('{solver_name}') RETURNING id"
        solver_id = query_database(query)

    query = f"SELECT id FROM maxsat_feature_vectors WHERE features = '{feature_vector}'"
    feat_id = query_database(query)
    if not feat_id:
        query = f"INSERT INTO maxsat_feature_vectors (features) VALUES ('{feature_vector}') RETURNING id"
        feat_id = query_database(query)

    print(feat_id)

    query = f"SELECT * FROM maxsat_solver_featvec_time WHERE solver_id = '{solver_id[0]}' AND feature_vec_id = '{feat_id[0]}' AND execution_time = '{execution_time}'"
    existing_entry = query_database(query)

    if not existing_entry:
        query = f"INSERT INTO maxsat_solver_featvec_time (solver_id, feature_vec_id, execution_time) VALUES ('{solver_id[0]}', '{feat_id[0]}', '{execution_time}')"
        query_database(query)

    print_all_tables()

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
def get_mzn_solver_id_by_name(solver_name):
    query = "SELECT id FROM mzn_solvers WHERE name = %s"
    params = (solver_name,)
    return query_database(query, params)

def get_all_mzn_feature_vectors():
    query = "SELECT features FROM mzn_feature_vectors"
    return query_database(query)

def handle_mzn_instance(data):
    feature_vector = "{" + str(data["featureVector"]) + "}"
    solver_name = data["solverName"]
    execution_time = data["executionTime"]
    result = data["result"]
    params = None

    query = "SELECT id FROM mzn_solvers WHERE name = %s"
    params = (solver_name,)
    solver_id = query_database(query, params)
    if not solver_id:
        query = "INSERT INTO mzn_solvers (name) VALUES (%s) RETURNING id"
        params = (solver_name,)
        solver_id = query_database(query, params)
        

    query = "SELECT id FROM mzn_feature_vectors WHERE features = %s"
    params = (feature_vector,)
    feat_id = query_database(query, params)
    if not feat_id:
        query = f"INSERT INTO mzn_feature_vectors (features) VALUES ('{feature_vector}') RETURNING id"
        feat_id = query_database(query, params)


    query = """
        SELECT * FROM mzn_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s AND execution_time = %s
    """
    params = (solver_id[0], feat_id[0], execution_time)
    existing_entry = query_database(query, params)

    if not existing_entry:
        if data["optVal"] != "" and data["optVal"] is not None:
            opt_value = data["optVal"]
            query = """
                INSERT INTO mzn_solver_featvec_time 
                (solver_id, feature_vec_id, opt_value, execution_time) 
                VALUES (%s, %s, %s)
            """
            params = (solver_id[0], feat_id[0], opt_value, execution_time, result)
        else: 
            query = """
                INSERT INTO mzn_solver_featvec_time 
                (solver_id, feature_vec_id, execution_time) 
                VALUES (%s, %s, %s)
            """
            params = (solver_id[0], feat_id[0], execution_time, result)
        query_database(query, params)
    print_all_tables()

def is_instance_solved_mzn(instance, solver):
    query = "SELECT id FROM mzn_solvers WHERE name = %s"
    params = (solver["name"],)
    solver_id = query_database(query, params)

    if not solver_id:
        return "Solver not found"

    instance = str(instance).replace(' ', '')
    instance = instance.replace('[', '')
    instance = instance.replace(']', '')
    instance = "{" + instance + "}"

    query = "SELECT id FROM mzn_feature_vectors WHERE features = %s"
    params = (instance,)
    feature_vector_id = query_database(query, params)
    if not feature_vector_id:
        return "Feature vector not found"

    query = """
        SELECT * FROM mzn_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s
    """
    params = (solver_id[0], feature_vector_id[0])
    result = query_database(query, params)

    return result


def get_all_solved_mzn():
    query = f"SELECT * FROM mzn_solver_featvec_time"
    return query_database(query)


def get_mzn_feature_vector_id(feature_vector):
    feature_vector = "{" + str(feature_vector) + "}"

    query = "SELECT id FROM mzn_feature_vectors WHERE features = %s"
    params = (feature_vector,)
    result = query_database(query, params)

    if not result:
        return None
    
    return result[0]


def all_mzn_feature_vectors():
    query = "SELECT features FROM mzn_feature_vectors"
    return query_database(query)


def get_insts_times_mzn(similar_insts):

    sim_inst_ids= []
    for vect in similar_insts:
        vect = str(vect).replace(' ', '')
        vect = vect.replace('[', '')
        vect = vect.replace(']', '')
        sim_inst_ids.append(get_mzn_feature_vector_id(vect))

    solved_times = {}

    for id in sim_inst_ids:
        print("ID: ", id, flush=True)
        query = "SELECT execution_time FROM mzn_solver_featvec_time WHERE solver_id = %s"
        params = (id,)
        result = query_database(query, params)[0][0]
        solved_times[id] = result

    return {"solvedTimesDict": solved_times}

def get_solver_times_mzn(solver_name, insts):

    solver_id = get_mzn_solver_id_by_name(solver_name)
    if not solver_id:
        return "Solver not found"

    sim_inst_ids= []
    for vect in insts:
        vect = str(vect).replace(' ', '')
        vect = vect.replace('[', '')
        vect = vect.replace(']', '')
        feat_vec_id = get_mzn_feature_vector_id(vect)
        if feat_vec_id:
            sim_inst_ids.append(feat_vec_id)

    solved_times = []

    for id in sim_inst_ids:
        query = """
            SELECT execution_time FROM mzn_solver_featvec_time 
            WHERE solver_id = %s AND feature_vec_id = %s 
            ORDER BY execution_time ASC
        """
        params = (solver_id[0], id)
        result = query_database(query, params)[0]
        solved_times.append(result)

    return solved_times


def get_mzn_solvers():
    query = "SELECT * FROM mzn_solvers"
    return query_database(query)


# General
def print_all_tables():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    tables = query_database(query)
    print(f"Tables: {tables}", flush=True)
    if tables is not None:
        for table in tables:
            print(table[0], ": ", flush=True)
            query = f"SELECT * FROM {table[0]}"
            print(query_database(query), flush=True)
            print("\n\n-----------------------------------\n\n-----------------------------------\n", flush=True)

def database_init():

    # MZN tables
    query = """
        CREATE TABLE IF NOT EXISTS mzn_feature_vectors (
            id SERIAL PRIMARY KEY,
            features FLOAT[] UNIQUE
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
            solver_id INT REFERENCES mzn_solvers(id),
            feature_vec_id INT REFERENCES mzn_feature_vectors(id),
            opt_value FLOAT,
            execution_time FLOAT NOT NULL,
            result VARCHAR(2047)
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
            solver_id INT REFERENCES sat_solvers(id),
            feature_vec_id INT REFERENCES sat_feature_vectors(id),
            execution_time FLOAT NOT NULL
        );
    """
    query_database(query)

    # MAXSAT tables
    query = """
        CREATE TABLE IF NOT EXISTS maxsat_feature_vectors (
            id SERIAL PRIMARY KEY,
            features VARCHAR(2047) UNIQUE
        );
    """
    query_database(query)


    query = """
        CREATE TABLE IF NOT EXISTS maxsat_solvers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
    """
    query_database(query)


    query = """
        CREATE TABLE IF NOT EXISTS maxsat_solver_featvec_time (
            id SERIAL PRIMARY KEY,
            solver_id INT REFERENCES maxsat_solvers(id),
            feature_vec_id INT REFERENCES maxsat_feature_vectors(id),
            execution_time FLOAT NOT NULL
        );
    """
    query_database(query)