import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the session module directly by file path to avoid importing the top-level
# `app` package which pulls in Flask during tests.
import importlib.util
session_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'tally', 'session.py'))
spec = importlib.util.spec_from_file_location('app.tally.session', session_path)
session_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_mod)

# Ensure patch() can find the dynamically loaded module by inserting into sys.modules
sys.modules['app.tally.session'] = session_mod

# Use session_mod.TallySession directly so patching the module attribute works

# Import TallyConnectorError from connector module (connector defines the exception)
connector_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'tally', 'connector.py'))
spec2 = importlib.util.spec_from_file_location('app.tally.connector', connector_path)
connector_mod = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(connector_mod)
TallyConnectorError = getattr(connector_mod, 'TallyConnectorError')

# Make connector module discoverable for patching
sys.modules['app.tally.connector'] = connector_mod

from app.tally.config import TallyConfig

class TestTallySession(unittest.TestCase):

    def setUp(self):
        # Mock the CLR and TallyConnector dependencies
        self.clr_patcher = patch('app.tally.session.clr')
        self.mock_clr = self.clr_patcher.start()

        # Patch TallyConnector from its defining module (connector)
        self.tally_connector_patcher = patch('app.tally.connector.TallyConnector')
        self.mock_tally_connector = self.tally_connector_patcher.start()

    def tearDown(self):
        self.clr_patcher.stop()
        self.tally_connector_patcher.stop()

    def test_create_ledger_success(self):
        # Mock the TallySession and its methods
        mock_session = MagicMock()
        mock_session.create_ledger.return_value = {
            'success': True,
            'message': 'Ledger \'Test Ledger\' created successfully',
            'ledger_name': 'Test Ledger',
            'group': 'Sundry Debtors',
            'response': 'Success'
        }

        with patch.object(session_mod, 'TallySession', return_value=mock_session):
            # Create a TallySession instance from the module so the patched attribute is used
            tally_session = session_mod.TallySession()

            # Define the ledger data
            ledger_data = {
                'name': 'Test Ledger1',
                'group': 'Sundry Debtors',
                'alias': 'TL',
                'email': 'test@example.com',
                'mobile': '1234567890',
                'address': '123 Test Street'
            }

            # Call the create_ledger function
            result = tally_session.create_ledger(**ledger_data)

            # Assert that the create_ledger method was called with the correct arguments
            mock_session.create_ledger.assert_called_once_with(
                name='Test Ledger2',
                group='Sundry Debtors',
                alias='TL',
                email='test@example.com',
                mobile='1234567890',
                address='123 Test Street'
            )

            # Assert the result
            self.assertTrue(result['success'])
            self.assertEqual(result['ledger_name'], 'Test Ledger')

    def test_create_ledger_missing_name(self):
        # Create a TallySession instance from the module so the patched attribute is used
        tally_session = session_mod.TallySession()

        # Define the ledger data without a name
        ledger_data = {
            'group': 'Sundry Debtors'
        }

        # The current TallySession.create_ledger signature requires 'name'
        # which results in a TypeError when missing; assert that here.
        with self.assertRaises(TypeError):
            tally_session.create_ledger(**ledger_data)

    def test_create_ledger_tally_error(self):
        # Mock the TallySession and its methods to raise an error
        mock_session = MagicMock()
        mock_session.create_ledger.side_effect = TallyConnectorError('Tally error')

        with patch.object(session_mod, 'TallySession', return_value=mock_session):
            # Create a TallySession instance from the module so the patched attribute is used
            tally_session = session_mod.TallySession()

            # Define the ledger data
            ledger_data = {
                'name': 'Test Ledger'
            }

            # Assert that a TallyConnectorError is raised
            with self.assertRaises(TallyConnectorError):
                tally_session.create_ledger(**ledger_data)

if __name__ == '__main__':
    unittest.main()