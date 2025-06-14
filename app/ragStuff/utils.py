def get_start_card():
	"""
	Get the start card from the norwegian index.
	Returns:
		str: The start card in markdown format.
	"""
	start_card = ""
	with open("ragStuff/startkort.md", "r", encoding="utf-8") as f:
		for line in f:
			start_card += line
	return start_card
