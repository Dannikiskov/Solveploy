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
        query = "INSERT INTO maxsat_solvers (name) VALUES (%s) RETURNING id"
        params = (solver_name,)
        solver_id = query_database(query, params)
        

    query = "SELECT id FROM maxsat_feature_vectors WHERE features = %s"
    params = (feature_vector_str,)
    feat_id = query_database(query, params)
    if len(feat_id) == 0:
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
    query = "SELECT id FROM maxsat_solvers WHERE name = %s"
    params = (solver,)
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
        SELECT * FROM sat_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s AND status != %s
    """
    params = (solver_id[0], feature_vector_id[0], "UNKNOWN")
    result = query_database(query, params)[0]
    if result:
        result = True
    else:
        result = False

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
    return extracted_result

def get_all_solved_maxsat():
    query = f"SELECT * FROM maxsat_solver_featvec_time"
    return query_database(query)


def get_maxsat_feature_vector_id(feature_vector):
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

    solver_id = get_maxsat_solver_id_by_name(solver_name)

    if not solver_id:
        print("Solver not found", flush=True)
        return "Solver not found"

    sim_inst_ids= []
    for vect in insts:
        feat_vec_id = get_maxsat_feature_vector_id(vect)
        if feat_vec_id:
            sim_inst_ids.append(feat_vec_id)

    solved_times = []

    for id in sim_inst_ids:
        query = """
            SELECT execution_time FROM maxsat_solver_featvec_time 
            WHERE solver_id = %s AND feature_vec_id = %s 
            ORDER BY execution_time ASC
        """
        params = (solver_id, id)
        result = query_database(query, params)[0]
        solved_times.append(result)

    return solved_times


def get_maxsat_solvers():
    query = "SELECT * FROM maxsat_solvers"
    return query_database(query)

def get_solved_time_maxsat(solver_name, inst):
    solver_id = get_maxsat_solver_id_by_name(solver_name)
    feat_vec_id = get_maxsat_feature_vector_id(inst)

    query = """
        SELECT execution_time FROM maxsat_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s 
    """

    params = (solver_id, feat_vec_id)
    result = query_database(query, params)[0]

    return result

def maxsat_matrix(solvers, insts, T):

    if not (isinstance(insts[0], list)):
        insts = [[x] for x in insts]

    # Convert each inner list to an array literal
    insts_array_literals = [sql.SQL("ARRAY[{}]::float[]").format(
        sql.SQL(',').join(sql.Literal(float(inst)) for inst in inner_list)
    ) for inner_list in insts]

    # Create a subquery that returns the arrays
    insts_subquery = sql.SQL("SELECT unnest(ARRAY[{}])").format(
        sql.SQL(',').join(insts_array_literals)
    )

    query = sql.SQL("""
    SELECT 
        s.name AS solver_name, 
        f.id AS feature_vector_id, 
        CASE 
            WHEN t.execution_time > %s THEN 'T' 
            ELSE CAST(t.execution_time AS VARCHAR) 
        END AS execution_time
    FROM 
        maxsat_solvers s
    JOIN 
        maxsat_solver_featvec_time t ON s.id = t.solver_id
    JOIN 
        maxsat_feature_vectors f ON t.feature_vec_id = f.id
    WHERE 
        s.name IN ({}) AND 
        EXISTS (
            SELECT 1 FROM unnest(f.features) feature
            WHERE feature = ANY ({})
        )
    ORDER BY 
        s.name, f.id;
    """).format(
        sql.SQL(',').join(sql.Literal(solver) for solver in solvers),  # Use sql.Literal for string values
        insts_subquery  # Use the subquery for insts
    )
    params = (T,)
    result = query_database(query, params)
    return result

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
        query = "INSERT INTO sat_solvers (name) VALUES (%s) RETURNING id"
        params = (solver_name,)
        solver_id = query_database(query, params)
        

    query = "SELECT id FROM sat_feature_vectors WHERE features = %s"
    params = (feature_vector_str,)
    feat_id = query_database(query, params)
    if len(feat_id) == 0:
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
            (solver_id, feature_vec_id, execution_time, status) 
            VALUES (%s, %s, %s, %s)
        """
        params = (solver_id[0], feat_id[0], execution_time, status)

    query_database(query, params)

    print_stuff()

def is_instance_solved_sat(instance, solver):
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
    result = query_database(query, params)
    
    if result:
        if result[0][4] == "UNSATISFIED":
            result = False
        else:
            result = True
    else:
            result = False


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
    return extracted_result

def get_all_solved_sat():
    query = f"SELECT * FROM sat_solver_featvec_time"
    return query_database(query)


def get_sat_feature_vector_id(feature_vector):
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
    solver_id = get_sat_solver_id_by_name(solver_name)

    if not solver_id:
        print("Solver not found", flush=True)
        return "Solver not found"

    sim_inst_ids= []
    for vect in insts:
        feat_vec_id = get_sat_feature_vector_id(vect)
        if feat_vec_id:
            sim_inst_ids.append(feat_vec_id)

    solved_times = []

    for id in sim_inst_ids:
        query = """
            SELECT execution_time FROM sat_solver_featvec_time 
            WHERE solver_id = %s AND feature_vec_id = %s 
            ORDER BY execution_time ASC
        """
        params = (solver_id, id)
        result = query_database(query, params)[0]
        solved_times.append(result)

    return solved_times


def get_sat_solvers():
    query = "SELECT * FROM sat_solvers"
    return query_database(query)


def sat_matrix(solvers, insts, T):

    if not (isinstance(insts[0], list)):
        insts = [[x] for x in insts]

    # Convert each inner list to an array literal
    insts_array_literals = [sql.SQL("ARRAY[{}]::float[]").format(
        sql.SQL(',').join(sql.Literal(float(inst)) for inst in inner_list)
    ) for inner_list in insts]

    # Create a subquery that returns the arrays
    insts_subquery = sql.SQL("SELECT unnest(ARRAY[{}])").format(
        sql.SQL(',').join(insts_array_literals)
    )

    query = sql.SQL("""
    SELECT 
        s.name AS solver_name, 
        f.id AS feature_vector_id, 
        CASE 
            WHEN t.execution_time > %s THEN 'T' 
            ELSE CAST(t.execution_time AS VARCHAR) 
        END AS execution_time
    FROM 
        sat_solvers s
    JOIN 
        sat_solver_featvec_time t ON s.id = t.solver_id
    JOIN 
        sat_feature_vectors f ON t.feature_vec_id = f.id
    WHERE 
        s.name IN ({}) AND 
        EXISTS (
            SELECT 1 FROM unnest(f.features) feature
            WHERE feature = ANY ({})
        )
    ORDER BY 
        s.name, f.id;
    """).format(
        sql.SQL(',').join(sql.Literal(solver) for solver in solvers),  # Use sql.Literal for string values
        insts_subquery  # Use the subquery for insts
    )
    params = (T,)
    result = query_database(query, params)
    return result


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
    return result

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
    print(f"handling mzn instance {solver_name} : {mznFileName} : {dataFileName}. ", flush=True)

    params = None
    query = "SELECT id FROM mzn_solvers WHERE name = %s"
    params = (solver_name,)
    solver_id = query_database(query, params)
    if len(solver_id) == 0:
        query = "INSERT INTO mzn_solvers (name) VALUES (%s) RETURNING id"
        params = (solver_name,)
        solver_id = query_database(query, params)
        

    query = "SELECT id FROM mzn_feature_vectors WHERE features = %s"
    params = (feature_vector_str,)
    feat_id = query_database(query, params)
    if len(feat_id) == 0:
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

def is_instance_solved_mzn(instance, solver):
    query = "SELECT id FROM mzn_solvers WHERE name = %s"
    params = (solver,)
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
        SELECT * FROM sat_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s AND status != %s
    """
    params = (solver_id[0], feature_vector_id[0], "UNKNOWN")
    result = query_database(query, params)[0]
    if result:
        result = True
    else:
        result = False

    return result


def get_all_solved_mzn():
    query = f"SELECT * FROM mzn_solver_featvec_time"
    return query_database(query)


def get_mzn_feature_vector_id(feature_vector):
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

    solver_id = get_mzn_solver_id_by_name(solver_name)


    if not solver_id:
        print("Solver not found", flush=True)
        return "Solver not found"

    sim_inst_ids= []
    for vect in insts:
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
        params = (solver_id, id)
        result = query_database(query, params)[0]
        solved_times.append(result)

    return solved_times


def get_mzn_solvers():
    query = "SELECT * FROM mzn_solvers"
    return query_database(query)

def get_solved_time_mzn(solver_name, inst):
    solver_id = get_mzn_solver_id_by_name(solver_name)
    feat_vec_id = get_mzn_feature_vector_id(inst)

    query = """
        SELECT execution_time FROM mzn_solver_featvec_time 
        WHERE solver_id = %s AND feature_vec_id = %s 
    """

    params = (solver_id, feat_vec_id)
    result = query_database(query, params)[0]

    return result

def mzn_matrix(solvers, insts, T):
    print("solvers: ", solvers, flush=True)
    print("insts: \n", insts, flush=True)
    print()

    if not (isinstance(insts[0], list)):
        insts = [[x] for x in insts]

    # Convert each inner list to an array literal
    insts_array_literals = [sql.SQL("ARRAY[{}]::float8[]").format(
        sql.SQL(',').join(sql.Literal(float(inst)) for inst in inner_list)
    ) for inner_list in insts]

    # Combine the array literals into a single array
    combined_insts = sql.SQL('ARRAY[{}]').format(
        sql.SQL(',').join(insts_array_literals)
    )

    query = sql.SQL("""
    WITH insts AS (
        SELECT unnest({})::float8[] AS features
    )
    SELECT 
        s.name AS solver_name, 
        f.id AS feature_vector_id, 
        CASE 
            WHEN t.status != 'OPTIMAL_SOLUTION' THEN 'T' 
            ELSE CAST(t.execution_time AS VARCHAR) 
        END AS execution_time
    FROM 
        mzn_solvers s
    JOIN 
        mzn_solver_featvec_time t ON s.id = t.solver_id
    JOIN 
        mzn_feature_vectors f ON t.feature_vec_id = f.id
    WHERE 
        s.name IN ({}) AND 
        f.features = ANY (SELECT features FROM insts)
    ORDER BY 
        s.name, f.id;
    """).format(
        combined_insts,
        sql.SQL(',').join(sql.Literal(solver) for solver in solvers)  # Use sql.Literal for string values
    )
    
    result = query_database(query)
    print("Result: ", flush=True)
    print(result, flush=True)
    return result

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


def get_mzn_data():
    query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'mzn_solvers')"
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


    result = query_database(query)
    return result

def get_sat_data():
    query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sat_solvers')"
    result = query_database(query)
    table_exists = result[0]
    if not table_exists:
        database_init()

    query = """
    SELECT 
        s.name AS solver_name, 
        json_agg(
            json_build_object(
                'sat_file_name', f.sat_file_name, 
                'status', t.status, 
                'execution_time', t.execution_time
            )
        ) AS data
    FROM 
        sat_solvers s
    JOIN 
        sat_solver_featvec_time t ON s.id = t.solver_id
    JOIN 
        sat_feature_vectors f ON t.feature_vec_id = f.id
    GROUP BY 
        s.name;
    """
    result = query_database(query)
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