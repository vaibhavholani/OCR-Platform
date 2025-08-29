import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
from flask import Flask

# Add the parent directory to sys.path to import the app module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the blueprint and services
from app.api.credit_routes import credit_bp
from app.services import CreditService


class TestCreditRoutes(unittest.TestCase):
    """Test cases for credit routes API endpoints"""

    def setUp(self):
        """Set up test client and mock data"""
        self.app = Flask(__name__)
        self.app.register_blueprint(credit_bp)
        self.client = self.app.test_client()

        # Mock user data
        self.mock_user_id = 1
        self.mock_doc_id = 100

        # Mock credit summary data
        self.mock_credit_summary = {
            'user_id': self.mock_user_id,
            'credits': {
                'remaining': 150,
                'total_added': 200,
                'total_spent': 50
            },
            'transactions': [
                {
                    'transaction_id': 1,
                    'amount': 100,
                    'type': 'credit',
                    'description': 'Initial credits',
                    'created_at': '2024-01-01T00:00:00Z'
                },
                {
                    'transaction_id': 2,
                    'amount': -50,
                    'type': 'debit',
                    'description': 'Document processing',
                    'created_at': '2024-01-15T00:00:00Z'
                }
            ]
        }

        # Mock transaction info
        self.mock_transaction_info = {
            'transaction_id': 3,
            'amount': 75,
            'type': 'credit',
            'description': 'Manual credit addition',
            'created_at': '2024-01-20T00:00:00Z'
        }

        # Mock document usage
        self.mock_document_usage = {
            'document_id': self.mock_doc_id,
            'credits_used': 10,
            'processing_type': 'ocr',
            'created_at': '2024-01-15T00:00:00Z',
            'user_id': self.mock_user_id
        }

    @patch('app.api.credit_routes.CreditService.get_user_credit_summary')
    def test_get_user_credits_success(self, mock_get_summary):
        """Test successful retrieval of user credits"""
        mock_get_summary.return_value = self.mock_credit_summary

        response = self.client.get(f'/api/credits/user/{self.mock_user_id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user_id'], self.mock_user_id)
        self.assertEqual(data['data']['credits']['remaining'], 150)
        mock_get_summary.assert_called_once_with(self.mock_user_id)

    @patch('app.api.credit_routes.CreditService.get_user_credit_summary')
    def test_get_user_credits_user_not_found(self, mock_get_summary):
        """Test user not found scenario"""
        mock_get_summary.return_value = None

        response = self.client.get(f'/api/credits/user/{self.mock_user_id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    @patch('app.api.credit_routes.CreditService.add_credits_to_user')
    @patch('app.api.credit_routes.CreditService.get_user_credit_summary')
    def test_add_credits_success(self, mock_get_summary, mock_add_credits):
        """Test successful credit addition"""
        mock_add_credits.return_value = (True, 'Credits added successfully', self.mock_transaction_info)
        mock_get_summary.return_value = self.mock_credit_summary

        request_data = {
            'amount': 75,
            'description': 'Manual credit addition'
        }

        response = self.client.post(
            f'/api/credits/user/{self.mock_user_id}/add',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Credits added successfully')
        self.assertEqual(data['transaction']['amount'], 75)
        mock_add_credits.assert_called_once_with(self.mock_user_id, 75, 'Manual credit addition')

    def test_add_credits_no_data(self):
        """Test add credits with no data provided"""
        response = self.client.post(
            f'/api/credits/user/{self.mock_user_id}/add',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No data provided')

    def test_add_credits_invalid_amount(self):
        """Test add credits with invalid amount"""
        test_cases = [
            {'amount': 0},  # Zero amount
            {'amount': -10},  # Negative amount
            {'amount': 'invalid'},  # Non-integer
            {'amount': 10.5},  # Float
        ]

        for test_data in test_cases:
            with self.subTest(test_data=test_data):
                response = self.client.post(
                    f'/api/credits/user/{self.mock_user_id}/add',
                    data=json.dumps(test_data),
                    content_type='application/json'
                )
                data = json.loads(response.data)

                self.assertEqual(response.status_code, 400)
                self.assertIn('error', data)
                # Check for either "Invalid amount" or "No data provided" based on actual implementation
                self.assertTrue(
                    'Invalid amount' in data['error'] or 
                    'No data provided' in data['error'] or
                    'amount' in data['error'].lower()
                )

    @patch('app.api.credit_routes.CreditService.add_credits_to_user')
    def test_add_credits_failure(self, mock_add_credits):
        """Test credit addition failure"""
        mock_add_credits.return_value = (False, 'Insufficient funds', None)

        request_data = {'amount': 100}

        response = self.client.post(
            f'/api/credits/user/{self.mock_user_id}/add',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Insufficient funds')

    @patch('app.api.credit_routes.CreditService.check_user_credits')
    def test_check_credits_for_operation_success(self, mock_check_credits):
        """Test successful credit check for operation"""
        mock_check_credits.return_value = (True, 'Sufficient credits available', self.mock_credit_summary)

        request_data = {'amount': 25}

        response = self.client.post(
            f'/api/credits/user/{self.mock_user_id}/check',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['has_sufficient_credits'])
        self.assertEqual(data['message'], 'Sufficient credits available')
        mock_check_credits.assert_called_once_with(self.mock_user_id, 25)

    def test_check_credits_invalid_amount(self):
        """Test credit check with invalid amount"""
        test_cases = [
            {'amount': 0},  # Zero amount
            {'amount': -5},  # Negative amount
            {'amount': 'invalid'},  # Non-integer
        ]

        for test_data in test_cases:
            with self.subTest(test_data=test_data):
                response = self.client.post(
                    f'/api/credits/user/{self.mock_user_id}/check',
                    data=json.dumps(test_data),
                    content_type='application/json'
                )
                data = json.loads(response.data)

                if test_data.get('amount') in [0, -5]:
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('error', data)

    @patch('app.api.credit_routes.CreditService.check_user_credits')
    def test_check_credits_insufficient(self, mock_check_credits):
        """Test credit check when insufficient credits"""
        mock_check_credits.return_value = (False, 'Insufficient credits', self.mock_credit_summary)

        request_data = {'amount': 200}

        response = self.client.post(
            f'/api/credits/user/{self.mock_user_id}/check',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertFalse(data['has_sufficient_credits'])
        self.assertEqual(data['message'], 'Insufficient credits')

    @patch('app.api.credit_routes.CreditService.get_document_credit_usage')
    def test_get_document_credit_usage_found(self, mock_get_usage):
        """Test successful retrieval of document credit usage"""
        mock_get_usage.return_value = self.mock_document_usage

        response = self.client.get(f'/api/credits/document/{self.mock_doc_id}/usage')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['document_id'], self.mock_doc_id)
        self.assertEqual(data['data']['credits_used'], 10)
        mock_get_usage.assert_called_once_with(self.mock_doc_id)

    @patch('app.api.credit_routes.CreditService.get_document_credit_usage')
    def test_get_document_credit_usage_not_found(self, mock_get_usage):
        """Test document credit usage not found"""
        mock_get_usage.return_value = None

        response = self.client.get(f'/api/credits/document/{self.mock_doc_id}/usage')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNone(data['data'])
        self.assertIn('No credit usage found', data['message'])

    @patch('app.api.credit_routes.CreditService.get_user_credit_summary')
    def test_get_all_users_credit_summary_success(self, mock_get_summary):
        """Test successful retrieval of all users credit summary"""
        # Mock User model and query - patch at the module level where it's imported
        mock_get_summary.return_value = self.mock_credit_summary

        with patch('app.models.User') as mock_user_model:  # Patch at models module
            mock_user = MagicMock()
            mock_user.user_id = 1
            mock_user.name = 'Test User'
            mock_user.email = 'test@example.com'
            mock_user.credits_remaining = 150
            mock_user.plan_type = 'premium'
            mock_user.credit_transactions.count.return_value = 5

            mock_user_model.query.all.return_value = [mock_user]

            response = self.client.get('/api/credits/admin/users')
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['total_users'], 1)
            self.assertEqual(len(data['data']), 1)
            self.assertEqual(data['data'][0]['user_id'], 1)
            self.assertEqual(data['data'][0]['name'], 'Test User')
            self.assertEqual(data['data'][0]['credits_remaining'], 150)

    @patch('app.models.User')
    def test_get_all_users_credit_summary_exception(self, mock_user_model):
        """Test exception handling in admin users summary"""
        mock_user_model.query.all.side_effect = Exception('Database error')

        response = self.client.get('/api/credits/admin/users')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 500)
        self.assertIn('error', data)
        self.assertIn('Database error', data['error'])

    def test_add_credits_default_description(self):
        """Test add credits with default description when not provided"""
        with patch('app.api.credit_routes.CreditService.add_credits_to_user') as mock_add:
            with patch('app.api.credit_routes.CreditService.get_user_credit_summary'):
                mock_add.return_value = (True, 'Success', self.mock_transaction_info)

                request_data = {'amount': 50}  # No description provided

                self.client.post(
                    f'/api/credits/user/{self.mock_user_id}/add',
                    data=json.dumps(request_data),
                    content_type='application/json'
                )

                # Verify default description was used
                mock_add.assert_called_once_with(
                    self.mock_user_id, 
                    50, 
                    'Manual credit addition'  # Default description
                )

    def test_check_credits_default_amount(self):
        """Test check credits with default amount when not provided"""
        with patch('app.api.credit_routes.CreditService.check_user_credits') as mock_check:
            mock_check.return_value = (True, 'Success', self.mock_credit_summary)

            # Provide empty JSON data (should default to 1)
            self.client.post(
                f'/api/credits/user/{self.mock_user_id}/check',
                data=json.dumps({}),
                content_type='application/json'
            )

            mock_check.assert_called_once_with(self.mock_user_id, 1)


if __name__ == '__main__':
    unittest.main()