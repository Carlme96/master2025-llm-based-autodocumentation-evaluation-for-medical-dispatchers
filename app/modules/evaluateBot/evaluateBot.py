from langgraph.graph import StateGraph, START, END
from langchain.embeddings import init_embeddings
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from app.dependencies import get_settings
from app.ragStuff.utils import get_start_card
from .state import GraphState, Section, Evaluation, Summary, FetchedDocs, Advice
from langchain.prompts import PromptTemplate
from langchain.chat_models import init_chat_model
import re

VECTOR_STORE_PATH_CONCAT = "ragStuff/VectorStores/Concat_Chapter_FAISS"
VECTOR_STORE_PATH_SUMMMARY = "ragStuff/VectorStores/Summary_Chapter_FAISS"


def extract_numbers(resp):
	numbers = set()
	for item in resp:
		# Extract the trailing part after the last ' | '
		parts = item.rsplit("|", 1)
		if len(parts) < 2:
			continue
		code = parts[1].strip()

		# Find all numeric segments using regex and convert them to integers
		matches = re.findall(r"\d+", code)
		for match in matches:
			numbers.add(int(match))

	return numbers


class EvaluateBot:
	"""
	EvaluateBot Agent for evaluating the converation.

	It splits the conversation into sections, and evaluates each section based on the norwegian index.

	The result is a simple and detailed markdown document, accessible in the returned state.
	"""

	def __init__(self) -> None:
		settings = get_settings().evaluatebot
		if not settings:
			raise Exception(
				"Missing evaluatebot settings in config, is the environment variable set?"
			)
		self.settings = settings
		self.graph = self._create_graph()

	def split_sections(self, state: GraphState):
		"""
		The first step in the evaluation process.
		Splits the conversation into sections based on an educated guess on the advice given by the dispatcher.

		The dispatcher is marked "0" in the transcription, and the caller is marked "1".

		Explanation:
			- Collect all transcripts after the previous dispatcher-transcript.
			- If a transcript is from the dispatcher:
				- If there multiple lines from the dispatcher in a row, then also add them to the section.
				- Add all the lines from the caller, until but not including the next line from the dispatcher.
				- Only stop at a line from the caller, and only if there are at least 3 lines in the section.

		Note:
			- A section will contain all "1" after the last "0" of the previous section. This means that the first "1"'s in a section is the same as the last "1"'s in the previous section.
		"""

		sections: list[Section] = []
		id = 0
		section = Section(id=id)

		earlier = []  # The last 1s of the previous section
		has_advice = False
		last_advice = False

		for idx, transcript in enumerate(state.baseDataEvaluateBot.transcription):
			# When we reach the first "0"
			if transcript[0] == "0" and has_advice is False and last_advice is False:
				has_advice = True

			# Reaching a "1" after the first "0" and we have > 2 lines, we have the last "0" of this section.
			if (
				transcript[0] == "1"
				and len(section.transcriptions) > 2
				and last_advice is False
				and has_advice is True
			):
				last_advice = True

			# If we have the last "0" and this line is "1"
			if last_advice is True and transcript[0] == "1":
				earlier.append(transcript)

			# If we have the last "0" and this line is "0"
			if last_advice is True and transcript[0] == "0":
				sections.append(section)

				# Extend earlier transcriptions with current, for the next section
				earlier_transcriptions = section.earlier_transcriptions.copy()
				earlier_transcriptions.extend(section.transcriptions)
				id += 1
				section = Section(
					id=id,
					earlier_transcriptions=earlier_transcriptions,
					transcriptions=earlier,  # The last "1"s of the previous section is the first "1"s of this section
				)
				earlier = []
				last_advice = False
				has_advice = False
			section.transcriptions.append(transcript)

		if len(section.transcriptions) > 0:
			sections.append(section)

		state.evaluateBotState.sections = sections

		return state

	def should_summarize(self, state: GraphState):
		"""
		Used for conditional edge in the graph.
		"""
		if self.is_finished(state):
			return "finished"
		if state.evaluateBotState.situation_established:
			return "situation_established"
		return "situation_not_established"

	def establish_situation(self, state: GraphState):
		llm = init_chat_model(**self.settings.evaluate.model_dump())

		prompt = PromptTemplate.from_template(
			state.evaluateBotPrompts.establish_situation_prompt
		)

		chain = prompt | llm | StrOutputParser()
		section = state.evaluateBotState.sections[state.evaluateBotState.evaluate_idx]

		start_card = get_start_card()

		fin = False
		fallback = False
		try_count = 0
		while not fin:
			print("=" * 16)
			try:
				result = chain.invoke(
					{
						"current_transcription": section.transcriptions,
						"earlier_transcriptions": section.earlier_transcriptions,
						"start_card": start_card,
					}
				)
				cleaned_response = re.sub(
					r"<think>.*?</think>", "", result, flags=re.DOTALL
				).strip()
				parsed_response = JsonOutputParser().parse(cleaned_response)
				state.evaluateBotState.unconcious_not_breathing = parsed_response[
					"unconcious_not_breathing"
				]

				if parsed_response["unconcious_not_breathing"] is True:
					state.evaluateBotState.situation_established = True
				else:
					state.evaluateBotState.situation_established = parsed_response[
						"situation_established"
					]

				state.evaluateBotState.is_child = parsed_response["is_child"]
				state.evaluateBotState.sections[
					state.evaluateBotState.evaluate_idx
				].evaluation = Evaluation(**parsed_response)

				fin = True
			except Exception as e:
				try_count += 1
				if try_count > 3 and fallback is False:
					fallback = True
					print("Falling back to fallback model")
					llm = init_chat_model(**self.settings.fallback.model_dump())
					chain = prompt | llm | StrOutputParser()
					try_count = 0
				if try_count > 3 and fallback is True:
					raise ValueError(
						"Failed to parse response after 3 attempts with fallback model"
					)
				print("Invalid response!")
				print(e)
				print("=" * 32)

		return state

	def is_finished(self, state: GraphState):
		if state.evaluateBotState.evaluate_idx == len(state.evaluateBotState.sections):
			return True
		return False

	def is_unconcious_not_breathing(self, state: GraphState):
		return state.evaluateBotState.unconcious_not_breathing

	def summarize_section(self, state: GraphState):
		llm = init_chat_model(**self.settings.summary.model_dump())

		prompt = PromptTemplate.from_template(
			state.evaluateBotPrompts.summarize_section_prompt
		)

		chain = prompt | llm | StrOutputParser()
		fin = False
		earlier_summary = ""
		print("-" * 16)
		print(
			"Processing section: ",
			state.evaluateBotState.evaluate_idx + 1,
			"/",
			len(state.evaluateBotState.sections),
		)
		for text in state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].transcriptions:
			print(text)
		print("Summarizing...")

		earlier_transcriptions = state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].earlier_transcriptions

		if state.evaluateBotState.evaluate_idx > 0:
			early_summary_tmp = state.evaluateBotState.sections[
				state.evaluateBotState.evaluate_idx - 1
			].summary
			if early_summary_tmp is not None:
				earlier_summary = early_summary_tmp.model_dump_json()

		try_count = 0
		fallback = False
		while not fin:
			try:
				raw_summary = chain.invoke(
					{
						"current_transcription": state.evaluateBotState.sections[
							state.evaluateBotState.evaluate_idx
						].transcriptions,
						"earlier_summary": earlier_summary,
						"earlier_transcriptions": earlier_transcriptions,
					},
				)

				# think_content = re.findall(
				# r"<think>(.*?)</think>", raw_summary, flags=re.DOTALL
				# )
				summary = re.sub(
					r"<think>.*?</think>", "", raw_summary, flags=re.DOTALL
				).strip()

				summary_json = JsonOutputParser().parse(summary)
				# print(summary_json)
				summary_obj = Summary(**summary_json)
				state.evaluateBotState.unconcious_not_breathing = summary_json[
					"unconcious_not_breathing"
				]
				state.evaluateBotState.sections[
					state.evaluateBotState.evaluate_idx
				].summary = summary_obj
				fin = True
			except Exception as e:
				try_count += 1
				if try_count > 3 and fallback is False:
					fallback = True
					print("Falling back to fallback model")
					llm = init_chat_model(**self.settings.fallback.model_dump())
					chain = prompt | llm | StrOutputParser()
					try_count = 0
				if try_count > 3 and fallback is True:
					raise ValueError(
						"Failed to parse response after 3 attempts with fallback model"
					)
				print("Invalid response!")
				print(e)
				print("=" * 32)

		return state

	def fetch_docs(self, state: GraphState):
		embed_model = init_embeddings(**self.settings.embedding.model_dump())
		if not isinstance(embed_model, Embeddings):
			raise TypeError("Embeddings model is of wrong instance type")

		vectorstore_QA = FAISS.load_local(
			folder_path=VECTOR_STORE_PATH_SUMMMARY,
			embeddings=embed_model,
			allow_dangerous_deserialization=True,
		)  # noqa: F821

		summary = state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].summary
		if summary is None:
			raise ValueError(
				"Missing summary in fetch docs, this is not supposed to happen."
			)

		print("Fetching docs...")
		query_embedding = embed_model.embed_query(summary.model_dump_json())

		results = vectorstore_QA.similarity_search_by_vector(query_embedding, k=5)

		response: list[FetchedDocs] = []
		for result in results:
			content = result.page_content
			chapter = result.metadata["chapter"]
			print(chapter)

			response.append(FetchedDocs(**{"content": content, "chapter": chapter}))

		state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].fetched_docs = response

		return state

	def pairwise_reranking(self, state: GraphState):
		llm = init_chat_model(**self.settings.comparison.model_dump())
		print(self.settings.comparison.model_dump_json())
		prompt = PromptTemplate.from_template(state.evaluateBotPrompts.pairwise_prompt)

		chain = prompt | llm | StrOutputParser()

		summary = state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].summary
		if summary is None:
			raise ValueError(
				"Missing summary in pairwise reranking, this is not supposed to happen."
			)
		current = state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].fetched_docs
		current_section = state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		]
		titles = [x.chapter[0:2] for x in current]
		# print(titles)
		# print(summary)
		folder_path = "ragStuff/LabelWork/"
		documents = []
		document = ""
		collect = False
		for i, ch in enumerate(titles):
			with open(folder_path + ch + ".md", "r", encoding="utf-8") as f:
				for line in f:
					if line[0:2] == "# ":
						document += line
					if line == "## CRITERIA\n":
						collect = True
					elif line[0:4] == "### ":
						collect = False
					if collect is True:
						document += line

				documents.append(document)
				document = ""

		winner = len(documents) - 1
		i = len(documents) - 2
		try_count = 0
		fallback = False
		while i >= 0:
			try:
				# print("="*16)
				print(
					f"🥊 SHOWDOWN ROUND {i}! {current[winner].chapter} VS. {current[i].chapter}! 🥊"
				)
				# print("-"*16)
				# print("🧠 The judge is deciding!!!")
				result = chain.invoke(
					{
						"summary": summary,
						"doc1": documents[winner],
						"doc2": documents[i],
						"current_transcription": current_section.transcriptions,
						"earlier_transcriptions": current_section.earlier_transcriptions,
					}
				)
				think_content = re.findall(
					r"<think>(.*?)</think>", result, flags=re.DOTALL
				)
				cleaned_response = re.sub(
					r"<think>.*?</think>", "", result, flags=re.DOTALL
				).strip()
				relevant = JsonOutputParser().parse(cleaned_response)
				score = int(relevant["score"])
				# print("*"*16)
				# print("Reason:")
				# print(relevant['reason'])
				if score == 1:
					winner = winner
				elif score == 0:
					winner = i
				else:
					raise ValueError(f"Invalid response from model: {cleaned_response}")
				if len(think_content) > 0:
					print(think_content[0])
				# print("-"*16)
				print(
					f"🏅 And the winner of round {i} is {current[winner].chapter}!! 🏅"
				)
				i -= 1
			except Exception as e:
				try_count += 1
				if try_count > 3 and fallback is False:
					fallback = True
					print("Falling back to fallback model")
					llm = init_chat_model(**self.settings.fallback.model_dump())
					chain = prompt | llm | StrOutputParser()
					try_count = 0
				if try_count > 3 and fallback is True:
					raise ValueError(
						"Failed to parse response after 3 attempts with fallback model"
					)
				print("Invalid response!")
				print(e)
				print("=" * 32)

		state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].best_doc = documents[winner]
		return state

	def get_best_doc_not_breathing(self, state: GraphState):
		if state.evaluateBotState.is_child is False:
			state.evaluateBotState.sections[
				state.evaluateBotState.evaluate_idx
			].best_doc = "# 01 Unconscious adult - not breathing normally"
			state.evaluateBotState.sections[
				state.evaluateBotState.evaluate_idx
			].advice = Advice(
				criterias=["Unconscious adult, not breathing normally"], advices={1}
			)
		else:
			state.evaluateBotState.sections[
				state.evaluateBotState.evaluate_idx
			].best_doc = (
				"# 02 Unconscious newborn / infant / child - not breathing normally"
			)
			state.evaluateBotState.sections[
				state.evaluateBotState.evaluate_idx
			].advice = Advice(
				criterias=["Unconscious child, not breathing normally"],
				advices={1, 2, 3},
			)

		return state

	def get_advices(self, state: GraphState):
		llm = init_chat_model(**self.settings.advices.model_dump())

		prompt = PromptTemplate.from_template(
			state.evaluateBotPrompts.extract_advices_prompt
		)

		chain = prompt | llm | StrOutputParser()

		print("Extracting advices...")
		section = state.evaluateBotState.sections[state.evaluateBotState.evaluate_idx]
		summary = section.summary
		if summary is None:
			raise ValueError(
				"Missing summary in get advices, this is not supposed to happen."
			)

		document = section.best_doc
		fin = False
		fallback = False
		try_count = 0

		while not fin:
			try:
				raw_advice = chain.invoke(
					{
						"summary": summary.model_dump_json(),
						"document": document,
						"current_transcription": section.transcriptions,
						"earlier_transcriptions": section.earlier_transcriptions,
					}
				)
				# think_content = re.findall(
				# r"<think>(.*?)</think>", raw_advice, flags=re.DOTALL
				# )
				advice = re.sub(
					r"<think>.*?</think>", "", raw_advice, flags=re.DOTALL
				).strip()
				advice_json = JsonOutputParser().parse(advice)
				advice_numbers = extract_numbers(advice_json["criterias"])
				advice_obj = Advice(
					criterias=advice_json["criterias"], advices=advice_numbers
				)
				section.advice = advice_obj
				# print("-"*16)
				# print("Criterias: ")
				# for criteria in advice_obj.criterias:
				# print(criteria)
				# print("Advices: " + str(advice_obj.advices))
				# print("-"*16)
				# if len(think_content) > 0:
				# print("Think: \n", think_content[0])
				fin = True
			except Exception as e:
				try_count += 1
				if try_count > 3 and fallback is False:
					fallback = True
					print("Falling back to fallback model")
					llm = init_chat_model(**self.settings.fallback.model_dump())
					chain = prompt | llm | StrOutputParser()
					try_count = 0
				if try_count > 3 and fallback is True:
					raise ValueError(
						"Failed to parse response after 3 attempts with fallback model"
					)
				print("Invalid response!")
				print(e)
				print("=" * 32)

		state.evaluateBotState.sections[state.evaluateBotState.evaluate_idx] = section

		return state

	def evaluate(self, state: GraphState):
		llm = init_chat_model(**self.settings.evaluate.model_dump())

		if state.evaluateBotState.unconcious_not_breathing is True:
			prompt = PromptTemplate.from_template(
				state.evaluateBotPrompts.evaluate_section_not_breathing_prompt
			)
		else:
			prompt = PromptTemplate.from_template(
				state.evaluateBotPrompts.evaluate_section_prompt
			)
		chain = prompt | llm | StrOutputParser()
		section = state.evaluateBotState.sections[state.evaluateBotState.evaluate_idx]
		# print("="*16)
		print("Evaluating...")
		transcription = section.transcriptions
		earlier_transcriptions = section.earlier_transcriptions

		summary = ""
		if state.evaluateBotState.evaluate_idx > 0:
			summary_tmp = state.evaluateBotState.sections[
				state.evaluateBotState.evaluate_idx - 1
			].summary
			if summary_tmp is not None:
				summary = summary_tmp.model_dump_json()

		best_doc = section.best_doc
		title = best_doc[2:4]
		folder_path = "ragStuff/LabelWork/"
		advices = ""
		related_questions = ""
		emergency_response = ""
		collecting = ""
		if section.advice is not None:
			with open(folder_path + title + ".md", "r", encoding="utf-8") as f:
				for line in f:
					if (
						line[0:10] == "### Advice"
						and int(line[11:13].strip(".")) in section.advice.advices
					):
						collecting = "advices"
					elif (
						line[0:23].upper() == "## SITUATIONAL GUIDANCE"
						or line[0:21].upper() == "## EMERGENCY RESPONSE"
					):
						collecting = "emergency_response"
					elif line[0:20].upper() == "## RELATED QUESTIONS":
						collecting = "related_questions"
					elif line[0] == "#" and collecting == "advices":
						collecting = ""
					elif line[0:3] == "## ":
						collecting = ""

					if collecting == "advices":
						advices += line
					if collecting == "emergency_response":
						emergency_response += line
					if collecting == "related_questions":
						related_questions += line

		fin = False
		fallback = False
		try_count = 0
		while not fin:
			try:
				raw_evaluation = chain.invoke(
					{
						"current_transcription": transcription,
						"earlier_transcriptions": earlier_transcriptions,
						"summary": summary,
						"advices": advices,
						"related_questions": related_questions,
						"emergency_response": emergency_response,
					}
				)
				# think_content = re.findall(
				# r"<think>(.*?)</think>", raw_evaluation, flags=re.DOTALL
				# )
				evaluation = re.sub(
					r"<think>.*?</think>", "", raw_evaluation, flags=re.DOTALL
				).strip()

				evaluation_json = JsonOutputParser().parse(evaluation)
				evaluation_obj = Evaluation(**evaluation_json)
				section.evaluation = evaluation_obj
				# print("-"*16)
				# print("Evaluation: ")
				# print("*Evaluation*: " + evaluation_obj.evaluation)
				# print("*Alternative*: " + evaluation_obj.alternate_action)
				# print("*Summary*: " + evaluation_obj.summary)
				# print("*Score*:" + str(evaluation_obj.score) + "/10")
				fin = True
			except Exception as e:
				try_count += 1
				if try_count > 3 and fallback is False:
					fallback = True
					print("Falling back to fallback model")
					llm = init_chat_model(**self.settings.fallback.model_dump())
					chain = prompt | llm | StrOutputParser()
					try_count = 0
				if try_count > 3 and fallback is True:
					raise ValueError(
						"Failed to parse response after 3 attempts with fallback model"
					)
				print("Invalid response!")
				print(e)
				print("=" * 32)

		state.evaluateBotState.sections[state.evaluateBotState.evaluate_idx] = section

		return state

	def generate_markdown(self, state: GraphState):
		doc = ""

		section = state.evaluateBotState.sections[state.evaluateBotState.evaluate_idx]

		doc += "\n## Transcription segment:\n"
		for j in section.transcriptions:
			doc += "- " + j + "\n"

		if section.evaluation is not None:
			doc += "## Evaluation: \n"
			doc += "- **Summary:** " + section.evaluation.summary + "\n"
			doc += "- **Evaluation:** " + section.evaluation.evaluation + "\n"
			doc += "- **Alternative:** " + section.evaluation.alternate_action + "\n"

		try:
			best_doc = section.best_doc.split("\n")[0][2:]
			if len(best_doc) > 0:
				doc += f"\n\n**Chosen chapter:** {best_doc}\n\n"
		except Exception:
			pass

		doc += "---\n"

		state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].result = doc

		return state

	def generate_markdown_detailed(self, state: GraphState):
		doc = ""

		section = state.evaluateBotState.sections[state.evaluateBotState.evaluate_idx]

		doc += f"# Id: {section.id}"
		doc += "\n## Transcription segment:\n"
		for j in section.transcriptions:
			doc += "- " + j + "\n"

		if section.summary is not None:
			doc += "## Summary:\n"
			doc += "- **Condition:** " + section.summary.condition + "\n"
			doc += "- **Observations:** " + section.summary.observations + "\n"
			doc += "- **Cause:** " + section.summary.cause + "\n"
			doc += "- **Callers actions:** " + section.summary.callers_actions + "\n"

		if section.evaluation is not None:
			doc += "## Evaluation: \n"
			doc += "- **Summary:** " + section.evaluation.summary + "\n"
			doc += "- **Evaluation:** " + section.evaluation.evaluation + "\n"
			doc += "- **Alternative:** " + section.evaluation.alternate_action + "\n"
			doc += "\n**score:** " + section.evaluation.score + "\n\n"

		try:
			best_doc = section.best_doc.split("\n")[0][2:]
			if len(best_doc) > 0:
				doc += "\n## Documents: \n"
				if len(section.fetched_docs) > 0:
					doc += "### Fetched documents: "
					doc += f"{[int(x.chapter[0:2]) for x in section.fetched_docs]}"[
						1:-1
					]
				doc += f"\n\n**Chosen document:** {best_doc}\n\n"
		except Exception:
			pass

		if section.advice:
			doc += "## Advices\n"
			doc += "### Criterias:\n"
			for advice in section.advice.criterias:
				doc += f"- {advice}\n"

			doc += "\n**Advices:** " + str(section.advice.advices).strip("{}") + "\n\n"

			doc += "---\n"

		state.evaluateBotState.sections[
			state.evaluateBotState.evaluate_idx
		].resultDetailed = doc

		state.evaluateBotState.evaluate_idx += 1
		return state

	def _create_graph(self):
		graph = StateGraph(GraphState)

		graph.add_node("split_sections", self.split_sections)
		graph.add_node("establish_situation", self.establish_situation)

		graph.add_node("summarize_section", self.summarize_section)
		graph.add_node("fetch_docs", self.fetch_docs)
		graph.add_node("pairwise_reranking", self.pairwise_reranking)
		graph.add_node("get_advices", self.get_advices)
		graph.add_node("evaluate", self.evaluate)
		graph.add_node("get_best_doc_not_breathing", self.get_best_doc_not_breathing)

		graph.add_node("generate_markdown", self.generate_markdown)
		graph.add_node("generate_markdown_detailed", self.generate_markdown_detailed)

		graph.add_edge(START, "split_sections")
		graph.add_edge("split_sections", "establish_situation")

		graph.add_edge("establish_situation", "generate_markdown")

		graph.add_edge("generate_markdown", "generate_markdown_detailed")

		graph.add_conditional_edges(
			"summarize_section",
			self.is_unconcious_not_breathing,
			{True: "get_best_doc_not_breathing", False: "fetch_docs"},
		)

		graph.add_edge("fetch_docs", "pairwise_reranking")
		graph.add_edge("pairwise_reranking", "get_advices")
		graph.add_edge("get_advices", "evaluate")

		graph.add_edge("get_best_doc_not_breathing", "evaluate")

		graph.add_edge("evaluate", "generate_markdown")

		graph.add_conditional_edges(
			"generate_markdown_detailed",
			self.should_summarize,
			{
				"situation_not_established": "establish_situation",
				"situation_established": "summarize_section",
				"finished": END,
			},
		)

		return graph.compile()
