from typing import Dict, List
import itertools
import string

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

	def find_nullable_variables(self):
		nullable = set()
		changed = True

		while changed:
			changed = False
			for variable, productions in self.nonTerminals.items():
				if variable in nullable:
					continue

				for production in productions:
					if all(symbol in nullable for symbol in production):
						nullable.add(variable)
						changed = True

		return list(nullable)

	def remove_useless_productions(self):
		# Step 1: Identify reachable non-terminals
		reachable_nonterminals = set()
		pending = [next(iter(self.nonTerminals.keys()))]

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
		return new_cfg

	def remove_epsilon_productions(self):
		# Step 1: Find nullable variables
		nullable = self.find_nullable_variables()

		# Step 2: Remove productions containing nullable variables
		new_cfg = self.nonTerminals.copy()
		for variable, productions in self.nonTerminals.items():
			updated_productions = [p for p in productions if all(s not in nullable for s in p)]
			new_cfg[variable] = updated_productions

		# Step 3: Remove empty productions
		for variable, productions in new_cfg.items():
			new_cfg[variable] = [p for p in productions if p != 'ε']
			new_cfg[variable] = [item for item in new_cfg[variable] if item.strip() != ""]

		# Step 4: Update other productions
		for variable, productions in new_cfg.items():
			combinations = []
			for production in productions:
				lowercase_letters = set(string.ascii_lowercase)
				input_set = set(production)

				if not lowercase_letters.intersection(input_set):
				# If there are no lowercase letters
					combinations = [''.join(comb) for comb in itertools.permutations(production)]
					new_cfg[variable] = combinations
				else:
					combinations = []
					new_cfg[variable] = []
					for comb_length in range(1, len(production) + 1):
						combinations.extend(itertools.combinations(production, comb_length))
					for combo in combinations:
						if lowercase_letters.intersection(combo):
							new_cfg[variable].append(''.join(combo))
				new_cfg[variable].sort()
		return new_cfg

	def toCNF(self):
		self.nonTerminals = self.remove_useless_productions() # Done
		self.nonTerminals = self.remove_epsilon_productions() # Done?
		self.nonTerminals = self.remove_useless_productions() # TODO
		self.nonTerminals = self.remove_useless_productions() # TODO
		self.nonTerminals = self.remove_useless_productions() # TODO
		self.nonTerminals = self.remove_useless_productions() # TODO
		return self.nonTerminals

cfg = Grammar()
for line in open("test.txt", "r", -1, "utf-8").readlines():
	cfg.addRule(line.strip())

#src: https://www.geeksforgeeks.org/simplifying-context-free-grammars/
#src: https://www.geeksforgeeks.org/converting-context-free-grammar-chomsky-normal-form/

cnf_grammar = cfg.toCNF()
lines = []
for non_terminal, productions in cnf_grammar.items():
	line = f"{non_terminal} -> { ' | '.join(productions)}"
	print(line)
	lines.append(f"{line}\n")