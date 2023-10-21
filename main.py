from typing import Dict, List
import itertools, string, os

#open("log.txt", "w", -1, "utf-8").write("")

def log(val: str):
	print(val)
	#open("log.txt", "a", -1, "utf-8").write(val + "\n")

def log_input(val: str):
	question = val
	val = input(val)
	#open("log.txt", "a", -1, "utf-8").write(question + val + "\n")
	return val

class Grammar :
	Rules: Dict[str,List[str]] = {}
	Symbolic = False

	def addRule(self, rule: str) :
		name = rule.split("->")[0].strip()
		if self.Rules.get(name) is None:
			self.Rules[name] = []
		for rhs in rule.split("->")[1].split("|"):
			self.Rules[name].append(rhs.strip())

	def remove_start_symbol(self) -> Dict[str, List[str]]:
		new_cfg = {}
		new_cfg["S0"] = [next(iter(self.Rules.keys()))] # if starts with S
		new_cfg = {**new_cfg, **self.Rules}
		return new_cfg

	def remove_useless_productions(self) -> Dict[str, List[str]]:
		# Step 1: Identify reachable non-terminals
		reachable_nonterminals = set()
		pending = [next(iter(self.Rules.keys()))]

		if self.Symbolic:
			while pending:
				current = pending.pop()
				print(current)
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
							for product in production.split():
								if all(symbol in reachable_nonterminals or not symbol.isupper() for symbol in product):
									new_productions.append(product)
						if new_productions:
							new_cfg[nonterminal] = new_productions
		else:
			while pending:
				current = pending.pop()
				for production in self.Rules[current]:
					for product in production.split():
						for symbol in product:
							if symbol.isupper() and symbol in reachable_nonterminals:
								reachable_nonterminals.add(symbol)
								pending.append(symbol)
						if product.isupper() and product not in reachable_nonterminals:
							reachable_nonterminals.add(product)
							pending.append(product)
			# Step 2: Identify reachable productions
			new_cfg = {}
			for nonterminal, productions in self.Rules.items():
				new_productions = []
				for production in productions:
					for product in production.split():
						if product.islower():
							new_productions.append(product)
						if product in reachable_nonterminals:
							if production not in new_productions:
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

				if any(c.islower() for c in input_set) and any(c.isupper() for c in input_set):
					combinations = []
					new_cfg[variable] = []
					for comb_length in range(1, len(production) + 1):
						combinations.extend(itertools.combinations(production, comb_length))
					for combo in combinations:
						if lowercase_letters.intersection(combo):
							new_cfg[variable].append(''.join(combo))
				elif all(c.isupper() for c in input_set):
					# If there are only uppercase letters
					new_cfg[variable] = productions
				elif all(c.islower() for c in input_set):
					# If there are only lowercase letters
					new_cfg[variable] = productions
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

		self.Rules = start_sym  = self.remove_start_symbol()        # Done  step 1 page 2

		self.Rules = useless    = self.remove_useless_productions() # Done  step 1 page 1 \
		self.Rules = epsilon    = self.remove_epsilon_productions() # Done  step 2 page 1  } step 2 page 2
		self.Rules = unit_prod  = self.remove_unit_productions()    # TODO  step 3 page 1 /

		self.Rules = terminals  = self.remove_terminals()           # TODO  step 3 page 2
		self.Rules = duplicates = self.remove_duplicate_symbols()   # TODO  step 4 page 2


		log("------------------- Remove Start Symbol --------------------------")
		for non_terminal, productions in start_sym.items() : log( f"{non_terminal} -> { ' | '.join(productions)}")
		log("------------------- Remove Useless Productions -------------------")
		for non_terminal, productions in useless.items()   : log( f"{non_terminal} -> { ' | '.join(productions)}")
		log("------------------- Remove Epsilon Productions -------------------")
		for non_terminal, productions in epsilon.items()   : log( f"{non_terminal} -> { ' | '.join(productions)}")
		#log("------------------- Remove Unit Productions ----------------------")
		#for non_terminal, productions in unit_prod.items() : log( f"{non_terminal} -> { ' | '.join(productions)}")
		#log("------------------- Remove Terminals -----------------------------")
		#for non_terminal, productions in terminals.items() : log( f"{non_terminal} -> { ' | '.join(productions)}")
		#log("------------------- Remove Duplicates ----------------------------")
		#for non_terminal, productions in duplicates.items(): log( f"{non_terminal} -> { ' | '.join(productions)}")


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
for line in open("cfg.txt", "r", -1, "utf-8").readlines():
	cfg.addRule(line.strip())
cfg.Symbolic = False

log("------------------- Context Free Grammar -------------------------")
for non_terminal, productions in cfg.Rules.items(): log( f"{non_terminal} -> { ' | '.join(productions)}")

cnf = cfg.CNF()

#log("------------------- Chomsky Normal Form --------------------------")
#for non_terminal, productions in cnf.items(): log( f"{non_terminal} -> { ' | '.join(productions)}")

run = False
while run:
	log("------------------- Cocke Younger Kasami -------------------------")
	sentence = log_input("Oración a analizar: ")
	if sentence == "":
		os.startfile("log.txt")
		break
	else:
		log("La oración: " + sentence)
		if cfg.CYK(sentence.split()): log("Pertenece a la gramática")
		else: log("NO pertenece a la gramática")