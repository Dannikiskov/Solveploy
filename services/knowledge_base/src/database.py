import subprocess
import psycopg2
import re


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
    query = f"SELECT id FROM mzn_solvers WHERE name = '{solver_name}'"
    return query_database(query)

def get_all_mzn_feature_vectors():
    query = "SELECT features FROM mzn_feature_vectors"
    return query_database(query)

def handle_mzn_instance(data):
    feature_vector = str(data["featureVector"])
    feature_vector = [float(num) for num in re.findall(r'\b\d+\.\d+\b', feature_vector)]
    solver_name = data["solverName"]
    execution_time = data["executionTime"]
    feature_vector_str = "{" + ",".join(map(str, feature_vector)) + "}"

    query = f"SELECT id FROM mzn_solvers WHERE name = '{solver_name}'"
    solver_id = query_database(query)
    if not solver_id:
        query = f"INSERT INTO mzn_solvers (name) VALUES ('{solver_name}') RETURNING id"
        solver_id = query_database(query)
        

    query = f"SELECT id FROM mzn_feature_vectors WHERE features = '{feature_vector_str}'"
    feat_id = query_database(query)
    if not feat_id:
        query = f"INSERT INTO mzn_feature_vectors (features) VALUES ('{feature_vector_str}') RETURNING id"
        feat_id = query_database(query)


    query = f"SELECT * FROM mzn_solver_featvec_time WHERE solver_id = '{solver_id[0]}' AND feature_vec_id = '{feat_id[0]}' AND execution_time = '{execution_time}'"
    existing_entry = query_database(query)

    if not existing_entry:
        query = f"INSERT INTO mzn_solver_featvec_time (solver_id, feature_vec_id, execution_time) VALUES ('{solver_id[0]}', '{feat_id[0]}', '{execution_time}')"
        query_database(query)

    print_all_tables()

def is_instance_solved_mzn(instance, solver):
    print("INSTANCE: ", instance, flush=True)
    print("SOLVER: ", solver["name"], flush=True)
    query = f"SELECT id FROM mzn_solvers WHERE name = '{solver["name"]}'"
    solver_id = query_database(query)
    if not solver_id:
        return "Solver not found"

    feature_vector = str(instance)
    feature_vector = [float(num) for num in re.findall(r'\b\d+\.\d+\b', feature_vector)]
    feature_vector_str = "{" + ",".join(map(str, feature_vector)) + "}"

    query = f"SELECT id FROM mzn_feature_vectors WHERE features = '{feature_vector_str}'"
    feature_vector_id = query_database(query)
    if not feature_vector_id:
        return "Feature vector not found"

    query = f"SELECT * FROM mzn_solver_featvec_time WHERE solver_id = {solver_id[0]} AND feature_vec_id = {feature_vector_id[0]}"
    result = query_database(query)

    return result


def get_all_solved_mzn():
    query = f"SELECT * FROM mzn_solver_featvec_time"
    return query_database(query)


def get_mzn_feature_vector_id(feature_vector):
    print("ASDASDASDASDASDASDASDASDASD", all_mzn_feature_vectors(), flush=True)
    feature_vector_str = "{" + ",".join(map(str, feature_vector)) + "}"
    query = f"SELECT id FROM mzn_feature_vectors WHERE features = '{feature_vector_str}'"
    result = query_database(query)
    print("RESULT: ", result, flush=True)
    return result[0]


def all_mzn_feature_vectors():
    query = "SELECT features FROM mzn_feature_vectors"
    return query_database(query)


def get_insts_times_mzn(similar_insts):

    sim_inst_ids= []
    for vect in similar_insts:
        print("VECT: ", vect, flush=True)
        sim_inst_ids.append(get_mzn_feature_vector_id(vect))

    solved_times = {}

    for id in sim_inst_ids:
        print("ID: ", id, flush=True)
        query = f"SELECT execution_time FROM mzn_solver_featvec_time WHERE solver_id = {id}"
        result = query_database(query)[0][0]
        solved_times[id] = result

    print("SOLVED TIMES: ", solved_times, flush=True)
    return {"solvedTimesDict": solved_times}


def get_solver_times_mzn(solver_name, insts):

    solver_id = get_mzn_solver_id_by_name(solver_name)
    if not solver_id:
        return "Solver not found"

    sim_inst_ids= []
    for vect in insts:
        print("VECT: ", vect, flush=True)
        sim_inst_ids.append(get_mzn_feature_vector_id(vect))

    solved_times = []

    for id in sim_inst_ids:
        print("ID: ", id, flush=True)
        query = f"SELECT execution_time FROM mzn_solver_featvec_time WHERE solver_id = {solver_id[0]} AND feature_vec_id = {id} ORDER BY execution_time ASC"
        result = query_database(query)[0]
        print("db RESULT: ", result, flush=True)
        print("db type RESULT: ", type(result), flush=True)
        solved_times.append(result)

    print("SOLVED TIMES: ", solved_times, flush=True)
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
    print("\n\n-----------------------------------\n", flush=True)

def set_allocatable_resources(data):
    cpu = data["allocatable_cpu"]
    memory = data["allocatable_memory"][:-2]
    query = f"INSERT INTO k8s_resources (allocatable_cpu, allocatable_memory) VALUES ({cpu}, {memory})"
    query_database(query)

def update_in_use_resources(data):
    cpu = data["cpu"]
    memory = data["memory"][:-2]
    query = f"UPDATE k8s_resources SET in_use_cpu = in_use_cpu + {cpu}, in_use_memory = in_use_memory + {memory}"
    query_database(query)

def get_available_k8s_resources():
    query = "SELECT * FROM k8s_resources"
    return query_database(query)

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

    # General tables
    query = """
        CREATE TABLE IF NOT EXISTS k8s_resources (
            id SERIAL PRIMARY KEY,
            allocatable_cpu FLOAT NOT NULL,
            allocatable_memory FLOAT NOT NULL,
            in_use_cpu FLOAT,
            in_use_memory FLOAT 
        );
    """
    query_database(query)