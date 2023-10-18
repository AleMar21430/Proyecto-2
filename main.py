from typing import Dict, List

def remove_useless_productions(cfg: Dict[str,List[str]]):
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


def remove_epsilon_productions(cfg: Dict[str, List[str]]):
	# Step 1: Find nullable variables
	nullable = set()
	for variable, productions in cfg.items():
		if '' or 'ε' in productions:
			nullable.add(variable)

	# Step 2: Remove productions containing nullable variables
	new_cfg = cfg.copy()
	for variable, productions in cfg.items():
		updated_productions = [p for p in productions if all(s not in nullable for s in p)]
		new_cfg[variable] = updated_productions

	# Step 3: Update other productions
	for variable, productions in cfg.items():
		for i in range(len(productions)):
			for j in range(1, len(productions[i]) + 1):
				# Try to find nullable variables
				for k in range(j):
					prefix = productions[i][:k]
					suffix = productions[i][k + 1:]
					if all(s not in nullable for s in prefix) and all(s not in nullable for s in suffix):
						updated_production = prefix + suffix
						if updated_production not in new_cfg[variable]:
							new_cfg[variable].append(updated_production)

	# Remove empty productions
	for variable, productions in new_cfg.items():
		new_cfg[variable] = [p for p in productions if p != '']

	return new_cfg

# MAIN
def cfg_to_cnf(cfg):
	cfg = remove_useless_productions(cfg)  # CORRECT
	cfg = remove_epsilon_productions(cfg)  # TODO: does not eliminate ε,  removes AB BC
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
	'S': ['AB', 'BC', 'AB BC'],
	'A': ['aA', 'a'],
	'B': ['bB', 'bC', 'c', 'ε'],
	'C': ['cC', 'c'],
	'D': ['d']
	
}

#src: https://www.geeksforgeeks.org/simplifying-context-free-grammars/
#src: https://www.geeksforgeeks.org/converting-context-free-grammar-chomsky-normal-form/

cnf_grammar = cfg_to_cnf(cfg)
lines = []
for non_terminal, productions in cnf_grammar.items():
	for production in productions:
		lines.append(f"{non_terminal} -> {production}\n")

lines[-1] = lines[-1][:-1]
with open('cnf.txt', 'w', encoding='utf-8') as file:
	for line in lines:
		file.write(line)