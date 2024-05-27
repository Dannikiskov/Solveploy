import tempfile
import psycopg2
from psycopg2 import sql


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
        result = [item[0] for item in result] if result and len(result[0]) == 1 else result

    else:
        result = None

    conn.commit()
    cur.close()
    conn.close()
    
    return result



# MAXSAT
def handle_maxsat_instance(data):
    query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'maxsat_solvers')"
    result = query_database(query)
    table_exists = result[0]
    if not table_exists:
        database_init()

    feature_vector_dict = data["featureVector"]
    feature_vector = ",".join(str(x) for x in feature_vector_dict.values())
    feature_vector_str = "{" + feature_vector + "}"
    solver_name = data["solverName"]
    execution_time = data["executionTime"]
    status = data["status"]

    params = None

    query = "SELECT id FROM maxsat_solvers WHERE name = %s"
    params = (solver_name,)
    solver_id = query_database(query, params)
    if len(solver_id) == 0:
        print("inserting solver", flush=True)
        query = "INSERT INTO maxsat_solvers (name) VALUES (%s) RETURNING id"
        params = (solver_name,)
        solver_id = query_database(query, params)
        

    query = "SELECT id FROM maxsat_feature_vectors WHERE features = %s"
    params = (feature_vector_str,)
    feat_id = query_database(query, params)
    print("feat_id", feat_id, flush=True)
    if len(feat_id) == 0:
        print("inserting feature", flush=True)
        query = "INSERT INTO maxsat_feature_vectors (features) VALUES (%s) RETURNING id"
        params = (feature_vector_str,)
        feat_id = query_database(query, params)


    query = """
        SELECT * FROM maxsat_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s
    """
    params = (solver_id[0], feat_id[0])
    existing_entry = query_database(query, params)
    if len(existing_entry) == 0:
        query = """
            INSERT INTO maxsat_solver_featvec_time 
            (solver_id, feature_vec_id, execution_time, status) 
            VALUES (%s, %s, %s, %s)
        """
        params = (solver_id[0], feat_id[0], execution_time, status)

    query_database(query, params)

    print_stuff()


def is_instance_solved_maxsat(instance, solver):
    print("from is_instance_solved_maxsat", flush=True)
    print("instance", instance, flush=True)
    print("solver", solver, flush=True)
    query = "SELECT id FROM maxsat_solvers WHERE name = %s"
    params = (solver["name"],)
    solver_id = query_database(query, params)

    if not solver_id:
        return "Solver not found"

    instance = str(instance).replace(' ', '')
    instance = instance.replace('[', '')
    instance = instance.replace(']', '')
    instance = "{" + instance + "}"

    query = "SELECT id FROM maxsat_feature_vectors WHERE features = %s"
    params = (instance,)
    feature_vector_id = query_database(query, params)
    if not feature_vector_id:
        return "Feature vector not found"

    query = """
        SELECT * FROM maxsat_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s
    """
    params = (solver_id[0], feature_vector_id[0])
    result = query_database(query, params)[0]
    if result:
        result = True
    else:
        result = False

    print("result", result, flush=True)

    return result

def get_maxsat_solver_id_by_name(solver_name):
    query = "SELECT id FROM maxsat_solvers WHERE name = %s"
    params = (solver_name,)
    return query_database(query, params)[0]

def get_all_maxsat_feature_vectors():
    query = "SELECT features FROM maxsat_feature_vectors"
    result = query_database(query)
    if len == 0:
        return None
    extracted_result = [t[0] for t in result]
    print("g_a_m_f_v: ", extracted_result, flush=True)
    print("type: ", type(extracted_result), flush=True)
    print("inner type, ", type(extracted_result[0]), flush=True)
    return extracted_result

def get_all_solved_maxsat():
    query = f"SELECT * FROM maxsat_solver_featvec_time"
    return query_database(query)


def get_maxsat_feature_vector_id(feature_vector):
    print("g_m_feature_vector", feature_vector, flush=True)
    feature_vector = str(feature_vector).replace(' ', '')
    feature_vector = feature_vector.replace('[', '')
    feature_vector = feature_vector.replace(']', '')
    feature_vector = "{" + str(feature_vector) + "}"

    query = "SELECT id FROM maxsat_feature_vectors WHERE features = %s"
    params = (feature_vector,)
    result = query_database(query, params)

    if len(result) == 0:
        return None
    
    return result[0]


def all_maxsat_feature_vectors():
    query = "SELECT features FROM maxsat_feature_vectors"
    return query_database(query)


def get_solved_times_maxsat(solver_name, insts):
    print("solver_name", solver_name, flush=True)
    print("insts length", len(insts), flush=True)
    solver_id = get_maxsat_solver_id_by_name(solver_name)
    print("solver_id", solver_id, flush=True)

    if not solver_id:
        print("Solver not found", flush=True)
        return "Solver not found"

    sim_inst_ids= []
    for vect in insts:
        print("vect", vect, flush=True)
        feat_vec_id = get_maxsat_feature_vector_id(vect)
        print("feat_vec_id", feat_vec_id, flush=True)
        if feat_vec_id:
            print("appending: ", feat_vec_id, flush=True)
            sim_inst_ids.append(feat_vec_id)

    solved_times = []

    for id in sim_inst_ids:
        print("ID: ", id, flush=True)
        query = """
            SELECT execution_time FROM maxsat_solver_featvec_time 
            WHERE solver_id = %s AND feature_vec_id = %s 
            ORDER BY execution_time ASC
        """
        params = (solver_id, id)
        result = query_database(query, params)[0]
        print("result", result, flush=True)
        solved_times.append(result)

    return solved_times


def get_maxsat_solvers():
    query = "SELECT * FROM maxsat_solvers"
    return query_database(query)


# SAT
def handle_sat_instance(data):
    query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sat_solvers')"
    result = query_database(query)
    table_exists = result[0]
    if not table_exists:
        database_init()

    feature_vector_dict = data["featureVector"]
    feature_vector = ",".join(str(x) for x in feature_vector_dict.values())
    feature_vector_str = "{" + feature_vector + "}"
    solver_name = data["solverName"]
    execution_time = data["executionTime"]
    status = data["status"]
    satFileName = data["satFileName"]

    params = None

    query = "SELECT id FROM sat_solvers WHERE name = %s"
    params = (solver_name,)
    solver_id = query_database(query, params)
    if len(solver_id) == 0:
        print("inserting solver", flush=True)
        query = "INSERT INTO sat_solvers (name) VALUES (%s) RETURNING id"
        params = (solver_name,)
        solver_id = query_database(query, params)
        

    query = "SELECT id FROM sat_feature_vectors WHERE features = %s"
    params = (feature_vector_str,)
    feat_id = query_database(query, params)
    print("feat_id", feat_id, flush=True)
    if len(feat_id) == 0:
        print("inserting feature", flush=True)
        query = "INSERT INTO sat_feature_vectors (features, sat_file_name) VALUES (%s, %s) RETURNING id"
        params = (feature_vector_str, satFileName)
        feat_id = query_database(query, params)


    query = """
        SELECT * FROM sat_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s
    """
    params = (solver_id[0], feat_id[0])
    existing_entry = query_database(query, params)
    if len(existing_entry) == 0:
        query = """
            INSERT INTO sat_solver_featvec_time 
            (solver_id, feature_vec_id, execution_time, status, sat_file_name) 
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (solver_id[0], feat_id[0], execution_time, status, satFileName)

    query_database(query, params)

    print_stuff()

def is_instance_solved_sat(instance, solver):
    print("from is_instance_solved_sat", flush=True)
    print("instance", instance, flush=True)
    print("solver", solver, flush=True)
    query = "SELECT id FROM sat_solvers WHERE name = %s"
    params = (solver,)
    solver_id = query_database(query, params)

    if not solver_id:
        return "Solver not found"

    instance = str(instance).replace(' ', '')
    instance = instance.replace('[', '')
    instance = instance.replace(']', '')
    instance = "{" + instance + "}"

    query = "SELECT id FROM sat_feature_vectors WHERE features = %s"
    params = (instance,)
    feature_vector_id = query_database(query, params)
    if not feature_vector_id:
        return "Feature vector not found"

    query = """
        SELECT * FROM sat_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s
    """
    params = (solver_id[0], feature_vector_id[0])
    result = query_database(query, params)[0]
    if result:
        result = True
    else:
        result = False

    print("result", result, flush=True)

    return result

def get_sat_solver_id_by_name(solver_name):
    query = "SELECT id FROM sat_solvers WHERE name = %s"
    params = (solver_name,)
    return query_database(query, params)[0]

def get_all_sat_feature_vectors():
    query = "SELECT features FROM sat_feature_vectors"
    result = query_database(query)
    if len == 0:
        return None
    extracted_result = [t[0] for t in result]
    print("g_a_m_f_v: ", extracted_result, flush=True)
    print("type: ", type(extracted_result), flush=True)
    print("inner type, ", type(extracted_result[0]), flush=True)
    return extracted_result

def get_all_solved_sat():
    query = f"SELECT * FROM sat_solver_featvec_time"
    return query_database(query)


def get_sat_feature_vector_id(feature_vector):
    print("g_m_feature_vector", feature_vector, flush=True)
    feature_vector = str(feature_vector).replace(' ', '')
    feature_vector = feature_vector.replace('[', '')
    feature_vector = feature_vector.replace(']', '')
    feature_vector = "{" + str(feature_vector) + "}"

    query = "SELECT id FROM sat_feature_vectors WHERE features = %s"
    params = (feature_vector,)
    result = query_database(query, params)

    if len(result) == 0:
        return None
    
    return result[0]


def all_sat_feature_vectors():
    query = "SELECT features FROM sat_feature_vectors"
    return query_database(query)


def get_solved_times_sat(solver_name, insts):
    print("solver_name", solver_name, flush=True)
    print("insts length", len(insts), flush=True)
    solver_id = get_sat_solver_id_by_name(solver_name)
    print("solver_id", solver_id, flush=True)

    if not solver_id:
        print("Solver not found", flush=True)
        return "Solver not found"

    sim_inst_ids= []
    for vect in insts:
        print("vect", vect, flush=True)
        feat_vec_id = get_sat_feature_vector_id(vect)
        print("feat_vec_id", feat_vec_id, flush=True)
        if feat_vec_id:
            print("appending: ", feat_vec_id, flush=True)
            sim_inst_ids.append(feat_vec_id)

    solved_times = []

    for id in sim_inst_ids:
        print("ID: ", id, flush=True)
        query = """
            SELECT execution_time FROM sat_solver_featvec_time 
            WHERE solver_id = %s AND feature_vec_id = %s 
            ORDER BY execution_time ASC
        """
        params = (solver_id, id)
        result = query_database(query, params)[0]
        print("result", result, flush=True)
        solved_times.append(result)

    return solved_times


def get_sat_solvers():
    query = "SELECT * FROM sat_solvers"
    return query_database(query)


# MZN
def get_mzn_solver_id_by_name(solver_name):
    query = "SELECT id FROM mzn_solvers WHERE name = %s"
    params = (solver_name,)
    return query_database(query, params)[0]

def get_all_mzn_feature_vectors():
    query = "SELECT features FROM mzn_feature_vectors"
    result = query_database(query)
    if len == 0:
        return None
    extracted_result = [t[0] for t in result]
    print("g_a_m_f_v: ", extracted_result, flush=True)
    print("type: ", type(extracted_result), flush=True)
    print("inner type, ", type(extracted_result[0]), flush=True)
    return extracted_result

def handle_mzn_instance(data):
    query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'mzn_solvers')"
    result = query_database(query)
    table_exists = result[0]
    if not table_exists:
        database_init()

    feature_vector = data["featureVector"]
    feature_vector_str = "{" + feature_vector + "}"
    solver_name = data["solverName"]
    execution_time = data["executionTime"]
    opt_goal = data["optGoal"]
    status = data["status"]
    mznFileName = data["mznFileName"]
    dataFileName = data["dataFileName"]
    params = None

    query = "SELECT id FROM mzn_solvers WHERE name = %s"
    params = (solver_name,)
    solver_id = query_database(query, params)
    if len(solver_id) == 0:
        print("inserting solver", flush=True)
        query = "INSERT INTO mzn_solvers (name) VALUES (%s) RETURNING id"
        params = (solver_name,)
        solver_id = query_database(query, params)
        

    query = "SELECT id FROM mzn_feature_vectors WHERE features = %s"
    params = (feature_vector_str,)
    feat_id = query_database(query, params)
    print("feat_id", feat_id, flush=True)
    if len(feat_id) == 0:
        print("inserting feature", flush=True)
        query = "INSERT INTO mzn_feature_vectors (features, mzn_file_name, data_file_name) VALUES (%s, %s, %s) RETURNING id"
        params = (feature_vector_str, mznFileName, dataFileName)
        feat_id = query_database(query, params)


    query = """
        SELECT * FROM mzn_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s
    """
    params = (solver_id[0], feat_id[0])
    existing_entry = query_database(query, params)
    if len(existing_entry) == 0:
        print("inserting mzn_solver_featvec_time", flush=True)
        if data["optVal"] != "N/A" and data["optVal"] is not None:
            opt_value = data["optVal"]
            query = """
                INSERT INTO mzn_solver_featvec_time 
                (solver_id, feature_vec_id, opt_value, opt_goal, execution_time, status) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (solver_id[0], feat_id[0], opt_value, opt_goal, execution_time, status)
        else: 
            query = """
                INSERT INTO mzn_solver_featvec_time 
                (solver_id, feature_vec_id, execution_time, status, opt_goal) 
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (solver_id[0], feat_id[0], execution_time, status, opt_goal)

        query_database(query, params)

    print_stuff()

def is_instance_solved_mzn(instance, solver):
    print("from is_instance_solved_mzn", flush=True)
    print("instance", instance, flush=True)
    print("solver", solver, flush=True)
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
    result = query_database(query, params)[0]
    if result:
        result = True
    else:
        result = False

    print("result", result, flush=True)

    return result


def get_all_solved_mzn():
    query = f"SELECT * FROM mzn_solver_featvec_time"
    return query_database(query)


def get_mzn_feature_vector_id(feature_vector):
    print("g_m_feature_vector", feature_vector, flush=True)
    feature_vector = str(feature_vector).replace(' ', '')
    feature_vector = feature_vector.replace('[', '')
    feature_vector = feature_vector.replace(']', '')
    feature_vector = "{" + str(feature_vector) + "}"

    query = "SELECT id FROM mzn_feature_vectors WHERE features = %s"
    params = (feature_vector,)
    result = query_database(query, params)

    if len(result) == 0:
        return None
    
    return result[0]


def all_mzn_feature_vectors():
    query = "SELECT features FROM mzn_feature_vectors"
    return query_database(query)


def get_solved_times_mzn(solver_name, insts):
    print("solver_name", solver_name, flush=True)
    print("insts length", len(insts), flush=True)
    solver_id = get_mzn_solver_id_by_name(solver_name)
    print("solver_id", solver_id, flush=True)

    if not solver_id:
        print("Solver not found", flush=True)
        return "Solver not found"

    sim_inst_ids= []
    for vect in insts:
        print("vect", vect, flush=True)
        feat_vec_id = get_mzn_feature_vector_id(vect)
        print("feat_vec_id", feat_vec_id, flush=True)
        if feat_vec_id:
            print("appending: ", feat_vec_id, flush=True)
            sim_inst_ids.append(feat_vec_id)

    solved_times = []

    for id in sim_inst_ids:
        print("ID: ", id, flush=True)
        query = """
            SELECT execution_time FROM mzn_solver_featvec_time 
            WHERE solver_id = %s AND feature_vec_id = %s 
            ORDER BY execution_time ASC
        """
        params = (solver_id, id)
        result = query_database(query, params)[0]
        print("result", result, flush=True)
        solved_times.append(result)

    return solved_times


def get_mzn_solvers():
    query = "SELECT * FROM mzn_solvers"
    return query_database(query)


def print_stuff():
    query = "SELECT * FROM sat_solver_featvec_time"
    result = query_database(query)
    print(result, flush=True)

# General
def print_all_tables():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    tables = query_database(query)
    print(f"Tables: {tables}", flush=True)
    if tables is not None:
        for table in tables:
            print(table[0], ": ", flush=True)
            query = f"SELECT * FROM {table[0]}"
            print(query_database(query)[0], flush=True)
            print("\n\n-----------------------------------\n\n-----------------------------------\n", flush=True)


def get_data():
    query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'maxsat_solvers')"
    result = query_database(query)
    table_exists = result[0]
    if not table_exists:
        database_init()
    
    query = """SELECT 
        solver_name,
        jsonb_object_agg(mzn_file_name, files) AS files
    FROM (
        SELECT 
            solver_name,
            mzn_file_name,
            jsonb_object_agg(data_file_name, solved_files) AS files
        FROM (
            SELECT 
                mzn_solvers.name AS solver_name,
                mzn_feature_vectors.mzn_file_name,
                mzn_feature_vectors.data_file_name,
                jsonb_agg(jsonb_build_object(
                    'opt_value', mzn_solver_featvec_time.opt_value,
                    'opt_goal', mzn_solver_featvec_time.opt_goal,
                    'execution_time', CAST(mzn_solver_featvec_time.execution_time AS VARCHAR),
                    'status', mzn_solver_featvec_time.status
                )) AS solved_files
            FROM 
                mzn_solvers
            JOIN 
                mzn_solver_featvec_time ON mzn_solvers.id = mzn_solver_featvec_time.solver_id
            JOIN
                mzn_feature_vectors ON mzn_solver_featvec_time.feature_vec_id = mzn_feature_vectors.id
            GROUP BY 
                mzn_solvers.name, mzn_feature_vectors.mzn_file_name, mzn_feature_vectors.data_file_name
        ) sub1
        GROUP BY 
            solver_name, mzn_file_name
    ) sub2
    GROUP BY 
        solver_name;    """

    print("RESUTL:", flush=True)
    result = query_database(query)
    print(result, flush=True)
    
    return result

def database_init():

    # MZN tables
    query = """
        CREATE TABLE IF NOT EXISTS mzn_feature_vectors (
            id SERIAL PRIMARY KEY,
            features FLOAT[] UNIQUE,
            mzn_file_name VARCHAR(255),
            data_file_name VARCHAR(255)
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
            opt_value VARCHAR(2047),
            opt_goal VARCHAR(2047),
            execution_time FLOAT NOT NULL,
            status VARCHAR(2047),
            result VARCHAR(2047)
        );
    """
    query_database(query)

    # SAT tables
    query = """   
        CREATE TABLE IF NOT EXISTS sat_feature_vectors (
            id SERIAL PRIMARY KEY,
            features FLOAT[] UNIQUE,
            sat_file_name VARCHAR(255)
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
            execution_time FLOAT NOT NULL,
            status VARCHAR(2047)
        );
    """
    query_database(query)

    # MAXSAT tables
    query = """
        CREATE TABLE IF NOT EXISTS maxsat_feature_vectors (
            id SERIAL PRIMARY KEY,
            features FLOAT[] UNIQUE,
            maxsat_file_name VARCHAR(255)
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