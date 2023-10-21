from typing import Dict, List
import itertools
import string

open("log.txt", "w", -1, "utf-8").write("")

def log(val: str):
	print(val)
	open("log.txt", "a", -1, "utf-8").write(val + "\n")

def log_input(val: str):
	question = val
	val = input(val)
	open("log.txt", "a", -1, "utf-8").write(question + val + "\n")
	return val

class Grammar :
	Rules: Dict[str,List[str]] = {}

	def addRule(self, rule) :
		nt = False
		parse = ""
		name = ""
		for i in range(len(rule)) :
			c = rule[i]
			if c == ' ' :
				if not nt :
					self.Rules[parse] = []
					name = parse
					nt = True
					parse = ""
				elif parse != "" :
					self.Rules[name].append(parse)
					parse = ""
			elif c != '|' and c != '-' and c != '>' : parse += c
		if parse != "" : self.Rules[name].append(parse)

	def remove_start_symbol(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		return new_cfg

	def remove_useless_productions(self) -> Dict[str, List[str]]:
		# Step 1: Identify reachable non-terminals
		reachable_nonterminals = set()
		pending = [next(iter(self.Rules.keys()))]

		while pending:
			current = pending.pop()
			for production in self.Rules[current]:
				for symbol in production:
					if symbol.isupper() and symbol not in reachable_nonterminals:
						reachable_nonterminals.add(symbol)
						pending.append(symbol)

		# Step 2: Identify reachable productions
		new_cfg = {}
		for nonterminal, productions in self.Rules.items():
			if nonterminal in reachable_nonterminals:
				new_productions = []
				for production in productions:
					if all(symbol in reachable_nonterminals or not symbol.isupper() for symbol in production):
						new_productions.append(production)
				if new_productions:
					new_cfg[nonterminal] = new_productions

		# Step 3: Remove unused non-terminals
		for nonterminal in self.Rules.keys():
			if nonterminal not in reachable_nonterminals:
				new_cfg.pop(nonterminal, None)

		first_item = next(iter(self.Rules.items()))
		new_cfg = {first_item[0]: first_item[1], **new_cfg}
		return new_cfg

	def remove_epsilon_productions(self) -> Dict[str, List[str]]:
		# Step 1: Find nullable variables
		nullable = set()
		changed = True

		while changed:
			changed = False
			for variable, productions in self.Rules.items():
				if variable in nullable:
					continue

				for production in productions:
					if all(symbol in nullable for symbol in production):
						nullable.add(variable)
						changed = True

		nullable = list(nullable)

		# Step 2: Remove productions containing nullable variables
		new_cfg = self.Rules.copy()
		for variable, productions in self.Rules.items():
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

	def remove_unit_productions(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		return new_cfg

	def remove_terminals(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		return new_cfg

	def remove_duplicate_symbols(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		return new_cfg

	def CNF(self) -> Dict[str, List[str]]:
		# page 1: https://www.geeksforgeeks.org/simplifying-context-free-grammars/
		# page 2: https://www.geeksforgeeks.org/converting-context-free-grammar-chomsky-normal-form/

		self.Rules = start_sym  = self.remove_start_symbol()        # TODO  step 1 page 2

		self.Rules = useless    = self.remove_useless_productions() # Done  step 1 page 1 \
		self.Rules = epsilon    = self.remove_epsilon_productions() # Done? step 2 page 1  } step 2 page 2
		self.Rules = unit_prod  = self.remove_unit_productions()    # TODO  step 3 page 1 /

		self.Rules = terminals  = self.remove_terminals()           # TODO  step 3 page 2
		self.Rules = duplicates = self.remove_duplicate_symbols()   # TODO  step 4 page 2


		log("------------------- Remove Start Symbol --------------------------")
		for non_terminal, productions in start_sym.items() : log( f"{non_terminal} -> { ' | '.join(productions)}")
		log("------------------- Remove Useless Productions -------------------")
		for non_terminal, productions in useless.items()   : log( f"{non_terminal} -> { ' | '.join(productions)}")
		log("------------------- Remove Epsilon Productions -------------------")
		for non_terminal, productions in epsilon.items()   : log( f"{non_terminal} -> { ' | '.join(productions)}")
		log("------------------- Remove Unit Productions ----------------------")
		for non_terminal, productions in unit_prod.items() : log( f"{non_terminal} -> { ' | '.join(productions)}")
		log("------------------- Remove Terminals -----------------------------")
		for non_terminal, productions in terminals.items() : log( f"{non_terminal} -> { ' | '.join(productions)}")
		log("------------------- Remove Duplicates ----------------------------")
		for non_terminal, productions in duplicates.items(): log( f"{non_terminal} -> { ' | '.join(productions)}")


		return self.Rules

	def CYK(self, words: List[str]) -> bool:
		# page 1: https://www.geeksforgeeks.org/cocke-younger-kasami-cyk-algorithm/

		word_count = len(words)
		T = [[set([]) for j in range(word_count)] for i in range(word_count)]
	
		for i in range(0, word_count):
			for lhs, rule in self.Rules.items():
				for rhs in rule:
					if len(rhs) == 1 and rhs[0] == words[i]: T[i][i].add(lhs)
			for j in range(i, -1, -1):
				for k in range(j, i + 1):
					for lhs, rule in self.Rules.items():
						for rhs in rule:
							if len(rhs) == 2 and rhs[0] in T[j][k] and rhs[1] in T[k + 1][i]: T[j][i].add(lhs)

		if len(T[0][word_count-1]) != 0: return True
		else: return False

cfg = Grammar()
for line in open("test.txt", "r", -1, "utf-8").readlines():
	cfg.addRule(line.strip())


log("------------------- Context Free Grammar -------------------------")
for non_terminal, productions in cfg.Rules.items(): log( f"{non_terminal} -> { ' | '.join(productions)}")

cnf = cfg.CNF()

log("------------------- Chomsky Normal Form --------------------------")
for non_terminal, productions in cnf.items(): log( f"{non_terminal} -> { ' | '.join(productions)}")

run = True
while run:
	log("------------------- Cocke Younger Kasami -------------------------")
	sentence = log_input("Oración a analizar: ")
	if sentence == "":
		break
	else:
		log("La oración: " + sentence)
		if cfg.CYK(sentence.split()): log("Pertenece a la gramática")
		else: log("NO pertenece a la gramática")