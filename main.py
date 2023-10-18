import re

def load_grammar(filename):
	grammar = []
	with open(filename, 'r', encoding='utf-8') as file:
		for line in file:
			line = line.strip()
			#if not line:
			#	continue
			#if re.match(r'^([A-Z])\s*->\s*(([A-Za-z0-9ε|]*\s*)*)$', line):
			non_terminal, productions = line.split('->')
			grammar.append((non_terminal.strip(), productions))
			#else:
			#	print(f"Producción inválida en: '{line}'")
			#	return None
	return grammar

def find_nullable_symbols(grammar):
	nullable = set()
	for production in grammar:
		if 'ε' in production[1]:
			nullable.add(production[0])
	return nullable

def generate_epsilon_free_grammar(grammar, nullable):
	changes = []
	result = {}
	non_terminal = []
	for productions in grammar:
		production = productions[1].strip().split("|")
		new = []
		for product in production:
			if "ε" in product:
				continue
			else:
				for non_terminal in nullable:
					if non_terminal in product:
						modified = product.replace(non_terminal,"")
						if modified != "":
							new.append(product)
							new.append(modified)
			new.append(product)
			non_terminal = set(new)
			new = list(non_terminal)
		new = [s for s in new if s.strip() != ""]
		changes.append(new)
		for i in range (len(changes)):
			products= "|".join(changes[i])
			result[productions[0]] = re.sub(r'\s*\|\s*', ' | ', products).lstrip()
	return result

grammar = load_grammar("gramatica.txt")
if grammar:
	print("---------- Gramática original")
	for productions in grammar:
		print(f"{productions[0]} -> {productions[1]}")

	nullable = find_nullable_symbols(grammar)

	print("---------- Símbolos anulables")
	print(', '.join(nullable))

	epsilon_free_grammar = generate_epsilon_free_grammar(grammar, nullable)

	print("---------- Gramática sin producciones-𝜀")
	for non_terminal, productions in epsilon_free_grammar.items():
		print(f"{non_terminal} -> {productions}")