from typing import Optional
from pydantic import BaseModel
from app.modules.basedata import BaseData, ImageDescription
from app.modules.evaluateBot.evaluateBot import EvaluateBot
from app.modules.evaluateBot.prompts import EvaluateBotPrompts
from app.modules.evaluateBot.state import EvaluateBotState
from app.modules.summaryBot.prompts import SummaryBotPrompts
from app.modules.summaryBot.state import SummaryBotState
from app.modules.summaryBot.summaryBot import SummaryBot
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.database import conn, aioconn


class GenerateReportProps(BaseModel):
	baseData: BaseData
	evaluateBotPrompts: EvaluateBotPrompts
	summaryBotPrompts: SummaryBotPrompts


class GraphState(BaseModel):
	# Pairwise RAG
	evaluateBotPrompts: EvaluateBotPrompts
	evaluateBotState: EvaluateBotState

	# Summary BOT
	summaryBotState: SummaryBotState
	summaryBotPrompts: SummaryBotPrompts
	imageDescriptions: list[ImageDescription] = []

	# BaseData
	baseDataEvaluateBot: BaseData
	baseDataSummaryBot: BaseData


class GenerateReport:
	def __init__(self) -> None:
		self.graph: Optional[CompiledStateGraph] = None

	async def generate(self, props: GenerateReportProps, id: str):
		if not self.graph:
			self.graph = await self._create_graph()

		state = GraphState(
			evaluateBotPrompts=props.evaluateBotPrompts,
			summaryBotPrompts=props.summaryBotPrompts,
			imageDescriptions=[],
			baseDataEvaluateBot=props.baseData,
			baseDataSummaryBot=props.baseData,
			evaluateBotState=EvaluateBotState(),
			summaryBotState=SummaryBotState(),
		)

		config = RunnableConfig(
			{"configurable": {"thread_id": id}, "recursion_limit": 1000}
		)  # noqa: F821
		await self.graph.ainvoke(state, config)

	async def get_reports(self) -> list[str]:
		if not self.graph:
			self.graph = await self._create_graph()

		db = conn.execute("SELECT DISTINCT thread_id FROM checkpoints;")
		return [id[0] for id in db.fetchall()]

	async def get_report(self, id: str):
		if not self.graph:
			self.graph = await self._create_graph()

		config = RunnableConfig({"configurable": {"thread_id": id}})
		eval_config = None
		summary_config = None
		async for snapshot in self.graph.aget_state_history(config):
			if len(snapshot.tasks) > 0:
				for task in snapshot.tasks:
					if task.state:
						try:
							current_config = task.state["configurable"]
							if current_config["checkpoint_ns"][0:12] == "evaluate_bot":
								eval_config = task.state
							elif current_config["checkpoint_ns"][0:11] == "summary_bot":
								summary_config = task.state
						except Exception:
							continue
		rawresult = await self.graph.aget_state(config)
		result = GraphState(**rawresult.values)
		if eval_config:
			try:
				eval_result = await self.graph.aget_state(eval_config)
				result.evaluateBotState = eval_result.values["evaluateBotState"]
			except Exception:
				pass

		if summary_config:
			try:
				summary_result = await self.graph.aget_state(summary_config)
				result.summaryBotState = summary_result.values["summaryBotState"]
				result.imageDescriptions = summary_result.values["imageDescriptions"]
			except Exception:
				pass

		return result, rawresult

	async def _create_graph(self):
		graph = StateGraph(GraphState)

		graph.add_node("evaluate_bot", EvaluateBot().graph)
		graph.add_node("summary_bot", SummaryBot().graph)

		graph.add_edge(START, "evaluate_bot")
		graph.add_edge(START, "summary_bot")

		graph.add_edge("evaluate_bot", END)
		graph.add_edge("summary_bot", END)

		checkpointer = AsyncSqliteSaver(conn=aioconn)

		return graph.compile(checkpointer=checkpointer)
