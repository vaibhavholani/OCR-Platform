import json
from flask import Flask
import sys, os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.api.ocr_routes import map_select_field_value


class MockOption:
    def __init__(self, value, label):
        self.option_value = value
        self.option_label = label


def load_options(json_path):
    with open(json_path, "r", encoding="utf-8") as fh:
        labels = json.load(fh)
    return [MockOption(label, label) for label in labels]


def _load_env_into_app(app):
    """Load GEMINI_API_KEY from repository .env into Flask app config if present."""
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    if k.strip() == 'GEMINI_API_KEY':
                        app.config['GEMINI_API_KEY'] = v.strip()


TEST_DEFINITIONS = {
    'exact': {'input': 'AAMRAPALI CREATION', 'expect': 'in_options'},
    'typo': {'input': 'AAMRAPLI CREATION', 'expect': 'in_options'},
    'no_match': {'input': 'qwertyuiopasdfgh', 'expect': 'none'},
    'case_insensitive': {'input': 'ambika sarees pvt ltd', 'expect': 'in_options'},
    'parenthesis': {'input': 'AMBIKA SAREES PVT LTD', 'expect': 'in_options'},
    'lowercase_city': {'input': 'ambika sarees kolkata', 'expect': 'in_options'},
    'punctuation': {'input': 'AMBIKA SAREES PVT LTD.', 'expect': 'in_options'},
    'ampersand_and': {'input': 'A.M AND SONS', 'expect': 'in_options'},
    'apostrophe': {'input': "QUEENS EMPORIUM", 'expect': 'in_options'},
    'missing_periods': {'input': 'AASHIRVAD SAREES PVT LTD', 'expect': 'in_options'},
    'extra_whitespace': {'input': '  AMBIKA   SAREES   PVT   LTD  ', 'expect': 'in_options'},
    'similar_zanvar': {'input': 'ZANVAR SAREES', 'expect': 'in_options'},
    'mixed_case': {'input': 'Maha Laxmi Textile', 'expect': 'in_options'},
}


def run_test(test_type):
    if test_type not in TEST_DEFINITIONS:
        print(f"Unknown test type: {test_type}")
        return

    cfg = TEST_DEFINITIONS[test_type]
    app = Flask(__name__)
    _load_env_into_app(app)
    # suppress noisy LLM/ocr route error logs during tests so output stays clean
    logging.getLogger('app.api.ocr_routes').setLevel(logging.CRITICAL)
    logging.getLogger('ocr_routes').setLevel(logging.CRITICAL)
    options = load_options(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'supplier_and_party_names.json')))

    with app.app_context():
        ocr_value = cfg['input']
        mapped = map_select_field_value(ocr_value, options, 'supplier_name')

        # Determine pass/fail based on expectation type (only 'in_options' or 'none')
        if cfg['expect'] == 'none':
            passed = (mapped is None)
        elif cfg['expect'] == 'in_options':
            option_values = [opt.option_value for opt in options]
            passed = (mapped in option_values)
        else:
            print(f"{test_type}: Unknown expectation '{cfg['expect']}' (allowed: 'in_options', 'none')")
            return

        status = 'PASSED' if passed else 'FAILED'
        # Unified two-line output requested by user
        print(f"{test_type}: {status}")
        print(f"Given query:{ocr_value} matches to :{mapped}")


def main():
    print("Running parameterized map_select_field tests...")
    try:
        for t in TEST_DEFINITIONS.keys():
            run_test(t)
        print("All tests completed")
    except Exception as e:
        print("An unexpected error occurred while running tests:", e)
        raise


if __name__ == '__main__':
    main()



