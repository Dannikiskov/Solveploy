import os
import sys
import unittest
from unittest.mock import call, patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

class TestGetSatSolverIdByName(unittest.TestCase):
    @patch('database.query_database')
    def test_get_sat_solver_id_by_name(self, mock_query_database):
        # Arrange
        solver_name = 'solver_name'
        expected_result = 1
        mock_query_database.return_value = [expected_result]

        # Act
        result = database.get_sat_solver_id_by_name(solver_name)

        # Assert
        mock_query_database.assert_called_once_with("SELECT id FROM sat_solvers WHERE name = %s", (solver_name,))
        self.assertEqual(result, expected_result)


class TestGetAllSatFeatureVectors(unittest.TestCase):
    @patch('database.query_database')
    def test_get_all_sat_feature_vectors(self, mock_query_database):
        # Arrange
        expected_result = ['feature1', 'feature2', 'feature3']
        mock_query_database.return_value = [(feature,) for feature in expected_result]

        # Act
        result = database.get_all_sat_feature_vectors()

        # Assert
        mock_query_database.assert_called_once_with("SELECT features FROM sat_feature_vectors")
        self.assertEqual(result, expected_result)


class TestGetAllSolvedSat(unittest.TestCase):
    @patch('database.query_database')
    def test_get_all_solved_sat(self, mock_query_database):
        # Arrange
        expected_result = [('solver1', 'featvec1', 'time1'), ('solver2', 'featvec2', 'time2')]
        mock_query_database.return_value = expected_result

        # Act
        result = database.get_all_solved_sat()

        # Assert
        mock_query_database.assert_called_once_with("SELECT * FROM sat_solver_featvec_time")
        self.assertEqual(result, expected_result)


class TestGetSatFeatureVectorId(unittest.TestCase):
    @patch('database.query_database')
    def test_get_sat_feature_vector_id(self, mock_query_database):
        # Arrange
        feature_vector = [1, 2, 3]
        expected_result = 1
        mock_query_database.return_value = [expected_result]

        # Act
        result = database.get_sat_feature_vector_id(feature_vector)

        # Assert
        mock_query_database.assert_called_once_with("SELECT id FROM sat_feature_vectors WHERE features = %s", ("{1,2,3}",))
        self.assertEqual(result, expected_result)


class TestAllSatFeatureVectors(unittest.TestCase):
    @patch('database.query_database')
    def test_all_sat_feature_vectors(self, mock_query_database):
        # Arrange
        expected_result = ['feature1', 'feature2', 'feature3']
        mock_query_database.return_value = [(feature,) for feature in expected_result]

        # Act
        result = database.all_sat_feature_vectors()

        # Assert
        mock_query_database.assert_called_once_with("SELECT features FROM sat_feature_vectors")
        self.assertEqual(result, [(feature,) for feature in expected_result])


class TestGetSolvedTimesSat(unittest.TestCase):
    @patch('database.get_sat_solver_id_by_name')
    @patch('database.get_sat_feature_vector_id')
    @patch('database.query_database')
    def test_get_solved_times_sat(self, mock_query_database, mock_get_sat_feature_vector_id, mock_get_sat_solver_id_by_name):
        # Arrange
        solver_name = 'solver_name'
        insts = [[1, 2, 3], [4, 5, 6]]
        solver_id = 1
        feature_vector_ids = [1, 2]
        expected_result = [10, 20]
        mock_get_sat_solver_id_by_name.return_value = solver_id
        mock_get_sat_feature_vector_id.side_effect = feature_vector_ids
        mock_query_database.side_effect = [(time,) for time in expected_result]

        # Act
        result = database.get_solved_times_sat(solver_name, insts)

        # Assert
        mock_get_sat_solver_id_by_name.assert_called_once_with(solver_name)
        mock_get_sat_feature_vector_id.assert_has_calls([call(inst) for inst in insts])
        mock_query_database.assert_has_calls([call("""
            SELECT execution_time FROM sat_solver_featvec_time 
            WHERE solver_id = %s AND feature_vec_id = %s 
            ORDER BY execution_time ASC
        """, (solver_id, id)) for id in feature_vector_ids])
        self.assertEqual(result, expected_result)


class TestGetSatSolvers(unittest.TestCase):
    @patch('database.query_database')
    def test_get_sat_solvers(self, mock_query_database):
        # Arrange
        expected_result = [('solver1', 'info1'), ('solver2', 'info2')]
        mock_query_database.return_value = expected_result

        # Act
        result = database.get_sat_solvers()

        # Assert
        mock_query_database.assert_called_once_with("SELECT * FROM sat_solvers")
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()