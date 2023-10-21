from typing import Dict, List

class Grammar :
	nonTerminals: Dict[str,List[str]] = {}

	def addRule(self, rule) :
		nt = False
		parse = ""
		name = ""
		for i in range(len(rule)) :
			c = rule[i]
			if c == ' ' :
				if not nt :
					self.nonTerminals[parse] = []
					name = parse
					nt = True
					parse = ""
				elif parse != "" :
					self.nonTerminals[name].append(parse)
					parse = ""
			elif c != '|' and c != '-' and c != '>' : parse += c
		if parse != "" : self.nonTerminals[name].append(parse)

	def remove_useless_productions(self):
		# Step 1: Identify reachable non-terminals
		reachable_nonterminals = set()
		pending = ['S']

		while pending:
			current = pending.pop()
			for production in self.nonTerminals[current]:
				for symbol in production:
					if symbol.isupper() and symbol not in reachable_nonterminals:
						reachable_nonterminals.add(symbol)
						pending.append(symbol)

		# Step 2: Identify reachable productions
		new_cfg = {}
		for nonterminal, productions in self.nonTerminals.items():
			if nonterminal in reachable_nonterminals:
				new_productions = []
				for production in productions:
					if all(symbol in reachable_nonterminals or not symbol.isupper() for symbol in production):
						new_productions.append(production)
				if new_productions:
					new_cfg[nonterminal] = new_productions

		# Step 3: Remove unused non-terminals
		for nonterminal in self.nonTerminals.keys():
			if nonterminal not in reachable_nonterminals:
				new_cfg.pop(nonterminal, None)

		first_item = next(iter(self.nonTerminals.items()))
		new_cfg = {first_item[0]: first_item[1], **new_cfg}
		self.nonTerminals = new_cfg

	def remove_epsilon_productions(self):
		# Step 1: Find nullable variables
		nullable = set()
		for variable, productions in self.nonTerminals.items():
			if '' or 'ε' in productions:
				nullable.add(variable)

		# Step 2: Remove productions containing nullable variables
		new_cfg = self.nonTerminals.copy()
		for variable, productions in self.nonTerminals.items():
			updated_productions = [p for p in productions if all(s not in nullable for s in p)]
			new_cfg[variable] = updated_productions

		# Step 3: Update other productions
		for variable, productions in self.nonTerminals.items():
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

		self.nonTerminals = new_cfg

	def toCNF(self):
		self.remove_useless_productions()
		#self.remove_epsilon_productions()
		return self.nonTerminals

# MAIN
def cfg_to_cnf(cfg: Grammar):
	cfg = cfg.remove_useless_productions()  # CORRECT
	cfg = cfg.remove_epsilon_productions()  # TODO: does not eliminate ε, removes AB BC
	return cfg

cfg = Grammar()
for line in open("test.txt", "r", -1, "utf-8").readlines():
	cfg.addRule(line)

#src: https://www.geeksforgeeks.org/simplifying-context-free-grammars/
#src: https://www.geeksforgeeks.org/converting-context-free-grammar-chomsky-normal-form/

cnf_grammar = cfg.toCNF()
lines = []
for non_terminal, productions in cnf_grammar.items():
	line = f"{non_terminal} -> { ' | '.join(productions)}"
	print(line, end="")
	lines.append(f"{line}\n")