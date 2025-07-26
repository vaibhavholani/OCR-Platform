from app.tally import auto_load_tally_options, load_customer_options

# Auto-detect and load appropriate options
result = auto_load_tally_options(field_id=123)
print(f"Loaded {result['options_count']} options")

# Load customer ledgers specifically  
customer_result = load_customer_options(field_id=124)