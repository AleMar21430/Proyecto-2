from typing import Dict, List
import time, os
global Release
Logging = False
def log(val: str):
	print(val)
	if Logging: open("log.txt", "a", -1, "utf-8").write(str(val) + "\n")
def log_input(val: str):
	question = val
	val = input(val)
	if Logging: open("log.txt", "a", -1, "utf-8").write(question + val + "\n")
	return val

class Grammar :
	Nonterminals: List[str] = []
	Terminals: List[str] = []
	Rules: Dict[str,List[str]] = {}

	def addRule(self, rule: str) :
		name = rule.split("->")[0].strip()
		self.Nonterminals.append(name)
		if self.Rules.get(name) is None:
			self.Rules[name] = []
		for rhs in rule.split("->")[1].split("|"):
			self.Rules[name].append(rhs.strip())
			for term in rhs:
				self.Terminals.append(term)

	def remove_epsilon_productions(self) -> Dict[str, List[str]]:
		# Step 1: Remove rhs epsilon
		nullable = []
		for lhs, rhs in self.Rules.items():
			for symbols in rhs:
				if 'ε' in symbols:
					nullable.append(lhs)
		log("------------------- Epsilon Productions --------------------------")
		if len(nullable) == 0:
			log("No Epsilon Productions")
			new_cfg = self.Rules.copy()
		else:
			log([str for str in nullable])
			new_cfg = {}
			free = []
			for lhs, rhs in self.Rules.items():
				new_productions = []
				for production in rhs:
					for non_terminals in nullable:
						if non_terminals in production:
							new_productions.append(production)
							new_productions.append(production.replace(non_terminals,""))
				new_productions.append(production)
				for modificacion in range (len(new_productions)):
					new_productions[modificacion] = new_productions[modificacion].replace("ε","")
				free = new_productions
				new_productions = free
				new_cfg[lhs] = list(set(new_productions))

		new_cfg = {key: sorted(value) for key, value in new_cfg.items()}
		log("------------------- Remove Epsilon Productions -------------------")
		for lhs, rhs in new_cfg.items()   : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_unit_productions(self) -> Dict[str, List[str]]:
		unit_productions = self.Rules.copy()
		new_cfg: Dict[str, List[str]] = {}

		# Step 1: Separate unit and non-unit productions
		for non_terminal in self.Rules:
			unit_productions[non_terminal] = []
			new_cfg[non_terminal] = []
			for production in self.Rules[non_terminal]:
				if len(production) == 1 and production.isupper():
					unit_productions[non_terminal].append(production)
				else:
					new_cfg[non_terminal].append(production)
		log("------------------- Unit Productions -----------------------------")
		no_unit_prod = True
		for lhs, rhs in unit_productions.items() :
			if rhs != []:
				log( f"{lhs} -> { ' | '.join(rhs)}")
			else :
				no_unit_prod = False
		if no_unit_prod: log("No Unit Productions")

		# Step 2: Find all reachable non-terminals for each non-terminal
		for _ in range(len(self.Rules)):
			for non_terminal in self.Rules:
				new_units = []
				for unit in unit_productions[non_terminal]:
					new_units.extend(unit_productions[unit])
				unit_productions[non_terminal].extend(new_units)
				unit_productions[non_terminal] = list(set(unit_productions[non_terminal]))

		# Step 3: Add all reachable productions to each non-terminal
		for non_terminal in self.Rules:
			new_productions = []
			for unit in unit_productions[non_terminal]:
				new_productions.extend(new_cfg[unit])
			new_cfg[non_terminal].extend(new_productions)
			new_cfg[non_terminal] = list(set(new_cfg[non_terminal]))

		new_cfg = {key: sorted(value) for key, value in new_cfg.items()}
		log("------------------- Remove Unit Productions ----------------------")
		for lhs, rhs in new_cfg.items() : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_useless_productions(self) -> Dict[str, List[str]]:
		# Step 1: Identify reachable non-terminals
		reachable_rhs = set()
		pending = [next(iter(self.Rules.keys()))]
		while pending:
			current = pending.pop()
			if self.Rules.get(current):
				for production in self.Rules[current]:
					for product in production.split():
						for symbol in product:
							if symbol.islower():
								if symbol in reachable_rhs:
									reachable_rhs.add(symbol)
									pending.append(symbol)
						if product.isupper():
							if product not in reachable_rhs:
								reachable_rhs.add(product)
								pending.append(product)
						else:
							for non_t in self.Nonterminals:
								if non_t in product:
									reachable_rhs.add(non_t)

		log("------------------- Reachable Non Terminals ----------------------")
		if len(reachable_rhs) == 0:log("No Reachable Terminals")
		else: log([str for str in reachable_rhs])
		# Step 2: Identify reachable productions
		new_cfg = {}
		for lhs, rhs in self.Rules.items():
			new_productions = []
			for production in rhs:
				for product in production.split():
					if product.islower():
						new_productions.append(product)
					if product in reachable_rhs:
						if production not in new_productions:
							new_productions.append(production)
					for non_t in self.Nonterminals:
						if non_t in product:
							if production not in new_productions:
								new_productions.append(production)
			if new_productions:
				new_cfg[lhs] = new_productions

		# Step 3: Remove unused non-terminals
		log("------------------- Useless Productions --------------------------")
		useless = []
		for lhs in self.Rules.keys():
			if lhs not in reachable_rhs:
				if lhs != self.Start_Rule[0]:
					new_cfg.pop(lhs, None)
					useless.append(lhs)

		if len(useless) == 0: log("No Useless Productions")
		else: log(useless)

		new_cfg = {self.Start_Rule[0]: self.Start_Rule[1], **new_cfg}

		new_cfg = {key: sorted(value) for key, value in new_cfg.items()}
		log("------------------- Remove Useless Productions -------------------")
		for lhs, rhs in new_cfg.items()   : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_terminals(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		new_cfg = {key: sorted(value) for key, value in new_cfg.items()}
		log("------------------- Remove Terminals -----------------------------")
		for lhs, rhs in new_cfg.items() : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_duplicate_symbols(self) -> Dict[str, List[str]]:
		new_cfg = self.Rules.copy()
		new_cfg = {key: sorted(value) for key, value in new_cfg.items()}
		log("------------------- Remove Duplicates ----------------------------")
		for lhs, rhs in new_cfg.items(): log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def remove_start_symbol(self) -> Dict[str, List[str]]:
		new_cfg = {"S0": [self.Start_Rule[0]], **self.Rules.copy()}

		new_cfg = {key: sorted(value) for key, value in new_cfg.items()}
		log("------------------- Replace Start Symbol -------------------------")
		for lhs, rhs in new_cfg.items() : log( f"{lhs} -> { ' | '.join(rhs)}")
		return new_cfg

	def CNF(self) -> Dict[str, List[str]]:
		self.Start_Rule = next(iter(self.Rules.items()))
		# page 1: https://www.geeksforgeeks.org/simplifying-context-free-grammars/
		# page 2: https://www.geeksforgeeks.org/converting-context-free-grammar-chomsky-normal-form/
		log("------------------- Context Free Grammar -------------------------")
		for lhs, rhs in self.Rules.items(): log( f"{lhs} -> { ' | '.join(rhs)}")

		# CFG Simplificacion

		self.Rules = self.remove_epsilon_productions() # DONE  step 2 page 1  \
		self.Rules = self.remove_unit_productions()    # TODO  step 3 page 1   } step 2 page 2
		self.Rules = self.remove_useless_productions() # DONE  step 1 page 1  /

		# CNF Conversion

		self.Rules = self.remove_terminals()           # TODO  step 3 page 2
		self.Rules = self.remove_duplicate_symbols()   # TODO  step 4 page 2
		self.Rules = self.remove_start_symbol()        # Done  step 1 page 2

		log("------------------- Chomsky Normal Form --------------------------")
		for lhs, rhs in self.Rules.items(): log( f"{lhs} -> { ' | '.join(rhs)}")

	def CYK(self, words: List[str]):
		cyk = {}
		for lhs, rhs in self.Rules.items():
			cyk[lhs] = [production.split() for production in rhs]
		log("------------------- CYK Internal Dict ----------------------------")
		for lhs, rhs in cyk.items(): log( f"{lhs} -> {rhs}")

		word_count = len(words)
		Parse_Tree = [[set([]) for j in range(word_count)] for i in range(word_count)]
	
		for i in range(0, word_count):
			for lhs, rhs in cyk.items():
				for production in rhs:
					if len(production) == 1:
						if production[0] == words[i]:
							Parse_Tree[i][i].add(lhs)
			for j in range(i, -1, -1):
				for k in range(j, i + 1):
					for lhs, rhs in cyk.items():
						for production in rhs:
							if len(production) == 2:
								try:
									if production[0] in Parse_Tree[j][k]:
										if production[1] in Parse_Tree[k + 1][i]:
											Parse_Tree[j][i].add(lhs)
								except: pass

		log("------------------- Cocke Younger Kasami Result ------------------")
		if len(Parse_Tree[0][word_count-1]) != 0:
			log(f"La oración || {' '.join(words)} || SI pertenece a la gramática✅")
		else:
			log(f"La oración || {' '.join(words)} || NO pertenece a la gramática⛔")
		log("------------------------------------------------------------------")

Logging = False
Hardcoded = True
Multicheck = True
Convert_to_CNF = True
Hardcoded_Sentence = "a dog cooks with a cat"

if Logging: open("log.txt", "w", -1, "utf-8").write("")
cfg = Grammar()
for line in open("cnf.txt", "r", -1, "utf-8").readlines():
	cfg.addRule(line.strip())
if Convert_to_CNF: cfg.CNF()
if Multicheck:
	while Multicheck:
		if Hardcoded:
			sentence = Hardcoded_Sentence
			Multicheck = False
		else:
			sentence = log_input("Oración a analizar: ")
			if sentence == "": Multicheck = False
else:
	if Hardcoded: sentence = Hardcoded_Sentence
	else: sentence = log_input("Oración a analizar: ")
#sentence = "(id*id)+id"

# S -> NP VP
# NP VP = DET N VP
# Det N VP = a dog VP
# a dog VP = a dog VP PP
# a dog VP PP = a dog cooks PP
# a dog cooks PP = a dog cooks P NP
# a dog cooks P NP = a dog cooks with NP
# a dog cooks with NP = a dog cooks with DET N
# a dog cooks with DET N = a dog cooks with a cat

cfg.CYK(sentence.split())
if Logging: os.startfile("log.txt")