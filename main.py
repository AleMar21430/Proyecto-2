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
		log("------------------- Remove Start Symbol --------------------------")
		for lhs, rhs in new_cfg.items() : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_terminals(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		# Initialize a counter for creating unique non-terminal symbols
		lhs_counter = 0

		# Iterate through each production rule
		for lhs, rhs in self.Rules.items():
			new_right_symbols = []
			for productions in rhs:
				for production in productions.split():
					if not production.islower():
						new_rhs = []
						i = 0
						while i < len(production):
							if production[i].islower():
								lhs = f'NONTERM{lhs_counter}'
								lhs_counter += 1
								new_cfg[lhs] = [production[i]]
								new_rhs.append(lhs)
							else: new_rhs.append(production[i])
							i += 1
						new_right_symbols.append("".join(new_rhs))
					else: new_right_symbols = rhs
			
			new_cfg[lhs] = new_right_symbols
		log("------------------- Remove Terminals -----------------------------")
		for lhs, rhs in new_cfg.items() : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_useless_productions(self) -> Dict[str, List[str]]:
		# Step 1: Identify reachable non-terminals
		reachable_rhs = set()
		pending = [next(iter(self.Rules.keys()))]
		while pending:
			current = pending.pop()
			for production in self.Rules[current]:
				for product in production.split():
					for symbol in product:
						if symbol.islower() and symbol in reachable_rhs:
							reachable_rhs.add(symbol)
							pending.append(symbol)
							print(symbol)
					if product.isupper() and product not in reachable_rhs:
						reachable_rhs.add(product)
						pending.append(product)

		print(reachable_rhs)

		# Step 2: Identify reachable productions
		new_cfg = {}
		for nonterminal, productions in self.Rules.items():
			new_productions = []
			for production in productions:
				for product in production.split():
					if product.islower():
						new_productions.append(product)
					if product in reachable_rhs:
						if production not in new_productions:
							new_productions.append(production)
			if new_productions:
				new_cfg[nonterminal] = new_productions

		# Step 3: Remove unused non-terminals
		for lhs in self.Rules.keys():
			if lhs not in reachable_rhs:
				new_cfg.pop(lhs, None)

		first_item = next(iter(self.Rules.items()))
		new_cfg = {first_item[0]: first_item[1], **new_cfg}
		log("------------------- Remove Useless Productions -------------------")
		for lhs, rhs in new_cfg.items()   : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_epsilon_productions(self) -> Dict[str, List[str]]:
		# Step 1: Find nullable variables
		nullable = set()
		changed = True
		while changed:
			changed = False
			for variable, rhs in self.Rules.items():
				if variable in nullable:
					continue
				for production in rhs:
					if all(symbol in nullable for symbol in production):
						nullable.add(variable)
						changed = True
		nullable = list(nullable)

		# Step 2: Remove rhs containing nullable variables
		new_cfg = self.Rules.copy()
		for variable, rhs in self.Rules.items():
			updated_rhs = [p for p in rhs if all(s not in nullable for s in p)]
			new_cfg[variable] = updated_rhs

		# Step 3: Remove empty rhs
		for variable, rhs in new_cfg.items():
			new_cfg[variable] = [p for p in rhs if p != 'ε']
			new_cfg[variable] = [item for item in new_cfg[variable] if item.strip() != ""]

		# Step 4: Update other rhs
		for variable, rhs in new_cfg.items():
			combinations = []
			for production in rhs:
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
					new_cfg[variable] = rhs
				elif all(c.islower() for c in input_set):
					# If there are only lowercase letters
					new_cfg[variable] = rhs
				new_cfg[variable].sort()
		log("------------------- Remove Epsilon Productions -------------------")
		for lhs, rhs in new_cfg.items()   : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_unit_productions(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		log("------------------- Remove Unit Productions ----------------------")
		for lhs, rhs in new_cfg.items() : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_duplicate_symbols(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		log("------------------- Remove Duplicates ----------------------------")
		for lhs, rhs in new_cfg.items(): log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def CNF(self) -> Dict[str, List[str]]:
		# page 1: https://www.geeksforgeeks.org/simplifying-context-free-grammars/
		# page 2: https://www.geeksforgeeks.org/converting-context-free-grammar-chomsky-normal-form/

		self.Rules = self.remove_start_symbol()        # Done  step 1 page 2
		self.Rules = self.remove_terminals()           # Done~ step 3 page 2           TODO creates but does not replace, use test.txt

		self.Rules = self.remove_useless_productions() # Done  step 1 page 1 \
		self.Rules = self.remove_epsilon_productions() # Done  step 2 page 1  } step 2 page 2
		self.Rules = self.remove_unit_productions()    # TODO  step 3 page 1 /

		self.Rules = self.remove_duplicate_symbols()   # TODO  step 4 page 2
		return self.Rules

	def CYK(self, words: List[str]) -> bool:
		word_count = len(words)
		T = [[set([]) for j in range(word_count)] for i in range(word_count)]
	
		for i in range(0, word_count):
			for lhs, rhs in self.Rules.items():
				for production in rhs:
					if len(production) == 1 and production[0] == words[i]: T[i][i].add(lhs)
			for j in range(i, -1, -1):
				for k in range(j, i + 1):
					for lhs, rhs in self.Rules.items():
						for production in rhs:
							if len(production) == 2 and production[0] in T[j][k] and production[1] in T[k + 1][i]: T[j][i].add(lhs)

		if len(T[0][word_count-1]) != 0: return True
		else: return False

cfg = Grammar()
for line in open("cfg.txt", "r", -1, "utf-8").readlines(): # ALL SYMBOlS MUST BE UPPERCASE
	cfg.addRule(line.strip())

log("------------------- Context Free Grammar -------------------------")
for lhs, rhs in cfg.Rules.items(): log( f"{lhs} -> { ' | '.join(rhs)}")

cnf = cfg.CNF()

#log("------------------- Chomsky Normal Form --------------------------")
#for lhs, rhs in cnf.items(): log( f"{lhs} -> { ' | '.join(rhs)}")

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