import os
import unittest
from unittest.mock import patch, MagicMock
import base64
import sys
from kubernetes import client
sys.path.insert(0, '../')
import k8sHandler

class TestK8sHandler(unittest.TestCase):
    @patch('k8sHandler.client.CoreV1Api')
    @patch('k8sHandler.client.BatchV1Api')
    @patch('k8sHandler.config')
    def test_start_solver_job(self, mock_config, mock_batch_api, mock_core_api):
        # Mock the Kubernetes configuration loading
        mock_config.load_incluster_config.return_value = None

        # Mock the secret reading
        mock_secret = MagicMock()
        mock_secret.data = {'rabbitmq-password': base64.b64encode(b'secret_password')}
        mock_core_api.return_value.read_namespaced_secret.return_value = mock_secret

        # Mock the job creation
        mock_batch_api.return_value.create_namespaced_job.return_value = None

        # Call the function with test data
        job_name = k8sHandler.start_solver_job('solver', '123', 'prefix', 1, 1)

        # Assert that the function returned the correct job name
        self.assertEqual(job_name, 'solver-123')

        # Assert that the Kubernetes configuration was loaded
        mock_config.load_incluster_config.assert_called()

        # Assert that the secret was read
        mock_core_api.return_value.read_namespaced_secret.assert_called_with("rabbitmq", "default")

        # Assert that the job was created
        mock_batch_api.return_value.create_namespaced_job.assert_called()

class TestCreateSolverJob(unittest.TestCase):
    @patch('k8sHandler.client.V1Job')
    @patch('k8sHandler.client.V1ObjectMeta')
    @patch('k8sHandler.client.V1JobSpec')
    @patch('k8sHandler.client.V1PodTemplateSpec')
    @patch('k8sHandler.client.V1PodSpec')
    @patch('k8sHandler.client.V1Container')
    @patch('k8sHandler.client.V1EnvVar')
    @patch('k8sHandler.client.V1ResourceRequirements')
    def test_create_solver_job(self, mock_V1ResourceRequirements, mock_V1EnvVar, mock_V1Container, mock_V1PodSpec, mock_V1PodTemplateSpec, mock_V1JobSpec, mock_V1ObjectMeta, mock_V1Job):
        # Arrange
        job_name = 'job_name'
        identifier = 'identifier'
        image_prefix = 'image_prefix'
        cpu_request = 'cpu_request'
        memory_request = 'memory_request'
        username = 'username'
        password = 'password'
        expected_result = MagicMock()

        mock_V1Job.return_value = expected_result

        # Act
        result = k8sHandler.create_solver_job(job_name, identifier, image_prefix, cpu_request, memory_request, username, password)

        # Assert
        mock_V1Job.assert_called_once()
        mock_V1ObjectMeta.assert_called_once_with(name=job_name)
        mock_V1JobSpec.assert_called_once()
        mock_V1PodTemplateSpec.assert_called_once()
        mock_V1PodSpec.assert_called_once()
        mock_V1Container.assert_called_once()
        mock_V1EnvVar.assert_called()
        mock_V1ResourceRequirements.assert_called_once_with(requests={"cpu": cpu_request, "memory": memory_request})
        self.assertEqual(result, expected_result)


class TestStopNamespacedJobs(unittest.TestCase):
    @patch('k8sHandler.client.BatchV1Api')
    @patch('k8sHandler.client.CoreV1Api')
    @patch('k8sHandler.config')
    def test_stop_namespaced_jobs(self, mock_config, mock_core_api, mock_batch_api):
        # Arrange
        namespace = 'default'
        mock_job = MagicMock()
        mock_pod = MagicMock()
        mock_batch_api().list_namespaced_job.return_value = MagicMock(items=[mock_job])
        mock_core_api().list_namespaced_pod.return_value = MagicMock(items=[mock_pod])

        # Act
        k8sHandler.stop_namespaced_jobs(namespace)

        # Assert
        mock_config.load_incluster_config.assert_called_once()
        mock_batch_api().list_namespaced_job.assert_called_once_with(namespace=namespace)
        mock_batch_api().delete_namespaced_job.assert_called_once_with(name=mock_job.metadata.name, namespace=namespace)
        mock_core_api().list_namespaced_pod.assert_called_once_with(namespace=namespace)
        mock_core_api().delete_namespaced_pod.assert_called_once_with(name=mock_pod.metadata.name, namespace=namespace)

class TestStopSpecificJob(unittest.TestCase):
    @patch('k8sHandler.client.BatchV1Api')
    @patch('k8sHandler.client.CoreV1Api')
    @patch('k8sHandler.config')
    def test_stop_specific_job(self, mock_config, mock_core_api, mock_batch_api):
        # Arrange
        namespace = 'default'
        identifier = 'identifier'
        mock_job = MagicMock()
        mock_pod = MagicMock()
        mock_job.metadata.name = identifier
        mock_pod.metadata.name = identifier
        mock_batch_api().list_namespaced_job.return_value = MagicMock(items=[mock_job])
        mock_core_api().list_namespaced_pod.return_value = MagicMock(items=[mock_pod])

        # Act
        k8sHandler.stop_specific_job(namespace, identifier)

        # Assert
        mock_config.load_incluster_config.assert_called_once()
        mock_batch_api().list_namespaced_job.assert_called_once_with(namespace=namespace)
        mock_batch_api().delete_namespaced_job.assert_called_once_with(name=mock_job.metadata.name, namespace=namespace)
        mock_core_api().list_namespaced_pod.assert_called_once_with(namespace=namespace)
        mock_core_api().delete_namespaced_pod.assert_called_once_with(name=mock_pod.metadata.name, namespace=namespace)


if __name__ == '__main__':
    unittest.main()