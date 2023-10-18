def remove_epsilon(cfg):
	# Remove ε-productions
	pass

def remove_unit(cfg):
	# Remove unit productions
	pass

def remove_useless(cfg):
	# Remove useless symbols
	pass

def eliminate_long_productions(cfg):
	# Eliminate productions with more than two symbols
	pass

def eliminate_chain_productions(cfg):
	# Eliminate chain productions
	pass

def add_new_start_symbol(cfg):
	# Add a new start symbol
	pass

def cfg_to_cnf(cfg):
	remove_epsilon(cfg)
	remove_unit(cfg)
	remove_useless(cfg)
	eliminate_long_productions(cfg)
	eliminate_chain_productions(cfg)
	add_new_start_symbol(cfg)
	return cfg

# Example CFG
cfg = {
	'S': ['aSb', ''],
	'A': ['aAb', 'c']
}

cnf_grammar = cfg_to_cnf(cfg)
for non_terminal, productions in cnf_grammar.items():
	for production in productions:
		print(f"{non_terminal} -> {production}")