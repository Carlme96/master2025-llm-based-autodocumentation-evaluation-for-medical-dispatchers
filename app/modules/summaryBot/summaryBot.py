from app.dependencies import get_settings
from app.modules.basedata import ImageDescription
from .state import GraphState
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class SummaryBot:
	def __init__(self) -> None:
		settings = get_settings().summarybot
		if not settings:
			raise Exception(
				"Missing Parsebot settings in config, is the environment variable set?"
			)
		self.settings = settings
		self.graph = self._create_graph()

	def describe_case(self, state: GraphState):
		print("\n---Describe Case---\n")
		"""
		
		"""
		llm = init_chat_model(**self.settings.describecase.model_dump())

		prompt = PromptTemplate.from_template(
			state.summaryBotPrompts.describe_case_prompt
		)

		chain = prompt | llm | StrOutputParser()

		retries = 0
		result = ""
		while retries <= 3:
			try:
				result = chain.invoke(
					{
						"transcription": state.baseDataSummaryBot.transcription,
						"transcription_prompt": state.summaryBotPrompts.transcription_prompt,
						"location": state.baseDataSummaryBot.location,
						"intention": state.summaryBotPrompts.intention_prompt,
						"appname": state.baseDataSummaryBot.appname,
						"incidencetime": state.baseDataSummaryBot.time,
					}
				)
				if result:
					break
			except Exception as e:
				print(f"Error describing case: {e}")
				retries += 1
				continue

		if retries > 3:
			result = "Error describing case"

		state.summaryBotState.steps.append("Describe Case")
		state.summaryBotState.case_description = result
		return state

	def should_describe_image(self, state: GraphState):
		print("\n---SHOULD DESCRIBE---\n")
		state.summaryBotState.steps.append("Should describe")

		if len(state.baseDataSummaryBot.images) > 0:
			return True
		return False

	def describe_images(self, state: GraphState):
		image_descriptions = [
			ImageDescription(
				image=image, description=self._describe_image(image, state)
			)
			for image in state.baseDataSummaryBot.images
		]
		state.summaryBotState.steps.append("Describe Images")
		state.imageDescriptions = image_descriptions
		return state

	def _describe_image(self, image: str, state: GraphState):
		vision_model = init_chat_model(**self.settings.vision.model_dump())

		prompt = ChatPromptTemplate.from_messages(
			[
				("system", state.summaryBotPrompts.describe_image_prompt),
				("user", [{"type": "image_url", "image_url": {"url": "{image}"}}]),
			]
		)

		chain = prompt | vision_model | StrOutputParser()

		result = ""
		retries = 0
		while retries <= 3:
			try:
				result = chain.invoke(
					{
						"image": image,
						"case_description": state.summaryBotState.case_description,
					}
				)
				if result:
					break
			except Exception as e:
				print(f"Error describing image: {e}")
				retries += 1
				continue

		if retries > 3:
			result = "Error describing image"

		return result

	def generate_summary(self, state: GraphState):
		llm = init_chat_model(**self.settings.summarize.model_dump())

		prompt = PromptTemplate.from_template(
			state.summaryBotPrompts.generate_summary_prompt
		)
		chain = prompt | llm | StrOutputParser()
		result = chain.invoke(
			{
				"transcription": state.baseDataSummaryBot.transcription,
				"transcription_prompt": state.summaryBotPrompts.transcription_prompt,
				"location": state.baseDataSummaryBot.location,
				"intention": state.summaryBotPrompts.intention_prompt,
				"appname": state.baseDataSummaryBot.appname,
				"incidencetime": state.baseDataSummaryBot.time,
				"image_descriptions": [
					image.model_dump_json() for image in state.imageDescriptions
				],
			}
		)

		state.summaryBotState.steps.append("Generate Summary")
		state.summaryBotState.summaryBotResult = result

		return state

	def _create_graph(self):
		graph = StateGraph(GraphState)

		graph.add_node("describe_case", self.describe_case)
		graph.add_node("describe_images", self.describe_images)
		graph.add_node("generate_summary", self.generate_summary)

		graph.add_edge(START, "describe_case")

		graph.add_conditional_edges(
			"describe_case",
			self.should_describe_image,
			{True: "describe_images", False: "generate_summary"},
		)

		graph.add_edge("describe_images", "generate_summary")

		graph.add_edge("generate_summary", END)

		return graph.compile()
