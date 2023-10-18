def remove_useless_productions(cfg):
	# Step 1: Identify reachable non-terminals
	reachable_nonterminals = set()
	pending = ['S']

	while pending:
		current = pending.pop()
		for production in cfg[current]:
			for symbol in production:
				if symbol.isupper() and symbol not in reachable_nonterminals:
					reachable_nonterminals.add(symbol)
					pending.append(symbol)

	# Step 2: Identify reachable productions
	new_cfg = {}
	for nonterminal, productions in cfg.items():
		if nonterminal in reachable_nonterminals:
			new_productions = []
			for production in productions:
				if all(symbol in reachable_nonterminals or not symbol.isupper() for symbol in production):
					new_productions.append(production)
			if new_productions:
				new_cfg[nonterminal] = new_productions

	# Step 3: Remove unused non-terminals
	for nonterminal in cfg.keys():
		if nonterminal not in reachable_nonterminals:
			new_cfg.pop(nonterminal, None)

	first_item = next(iter(cfg.items()))
	new_cfg = {first_item[0]: first_item[1], **new_cfg}
	return new_cfg






# MAIN
def cfg_to_cnf(cfg):
	cfg = remove_useless_productions(cfg)
	return cfg

cfg = {
	'S'  : ['NP VP'],
	'VP' : ['VP PP', 'V NP', 'cooks', 'drinks', 'eats', 'cuts'],
	'PP' : ['P NP'],
	'NP' : ['Det N', 'it', 'she'],
	'V'  : ['cooks', 'drinks', 'eats', 'cuts'],
	'P'  : ['in', 'with'],
	'N'  : ['cat', 'dog', 'beer', 'cake', 'juice', 'meat', 'soup', 'fork', 'knife', 'oven', 'spoon'],
	'Det': ['a', 'the']
}

cfg = {
	'S': ['AB', 'BC', 'ABBC'],
	'A': ['aA', 'a'],
	'B': ['bB', 'bC', 'c'],
	'C': ['cC', 'c'],
	'D': ['d']
}

cnf_grammar = cfg_to_cnf(cfg)
for non_terminal, productions in cnf_grammar.items():
	for production in productions:
		print(f"{non_terminal} -> {production}")