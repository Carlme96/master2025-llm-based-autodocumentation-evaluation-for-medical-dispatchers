from typing import Optional
from pydantic import BaseModel

from app.modules.basedata import BaseData


from .prompts import EvaluateBotPrompts


class FetchedDocs(BaseModel):
	"""
	FetchedDocs model for the EvaluateBot module.

	Attributes:
		content (str): Content of the fetched document.
		chapter (str): Chapter of the fetched document.
	"""

	content: str
	chapter: str


class Evaluation(BaseModel):
	"""
	Evaluation model for the EvaluateBot module.
	The evaluation is the final result of the evaluation agent.

	Attributes:
		summary (str): Summary of the evaluation.
		evaluation (str): Evaluation result.
		alternate_action (str): Alternate action suggested by the LLM.
		score (str): Score of the evaluation. Bad, Ok, Good.
	"""

	summary: str
	evaluation: str
	alternate_action: str
	score: str


class Advice(BaseModel):
	"""
	Advice model for the EvaluateBot module.
	Populated by an LLM with the criterias and advice numbers from a chapter in the norwegian index.

	Attributes:
		criterias (list[str]): List of criterias
		advices (set[int]): Set of advice numbers, corresponding to the criterias.
	"""

	criterias: list[str]
	advices: set[int]


class Summary(BaseModel):
	"""
	Summary model for the EvaluateBot module.
	A summary contains information about the situation, usually passed to an LLM for context.

	Attributes:
		condition (str): The condition of the patient. Whats wrong?
		observations (str): Observations reported by the caller.
		cause (str): The cause of the condition. What happened?
		callers_actions (str): What the caller is doing. What is its role?
	"""

	condition: str
	observations: str
	cause: str
	callers_actions: str


class Section(BaseModel):
	"""
	Section model for the EvaluateBot module.
	A section represents a part of the conversation in the evaluation process, and is being evaluated.

	Attributes:
		id (int): Unique identifier for the section, used for tracking.
		earlier_transcriptions (list[str]): The entire transcription of the conversation up to (but not including) this point.
		transcriptions (list[str]): The transcription of the conversation in this section.
		evaluation (Optional[Evaluation]): The evaluation of the section, None until generated. Will always be generated.
		summary (Optional[Summary]): The summary of the section, None until generated. Only generated if situation is established.
		fetched_docs (list[FetchedDocs]): List of fetched documents related to the section. Will only be populated if RAG is used.
		best_doc (str): The chosen document fetched for this section by the pairwise ranking. Will only be filled if situation is established.
		advice (Optional[Advice]): The advice for the section, None until generated. Only generated if situation is established.
	"""

	id: int
	earlier_transcriptions: list[str] = []
	transcriptions: list[str] = []
	evaluation: Optional[Evaluation] = None
	summary: Optional[Summary] = None
	fetched_docs: list[FetchedDocs] = []
	best_doc: str = ""
	advice: Optional[Advice] = None
	result: Optional[str] = None
	resultDetailed: Optional[str] = None


class EvaluateBotState(BaseModel):
	evaluate_idx: int = 0
	sections: list[Section] = []

	situation_established: bool = False
	unconcious_not_breathing: bool = False
	is_child: bool = False


class GraphState(BaseModel):
	"""
	Graph state for the EvaluateBot module.

	Attributes:
		evaluate_idx (int): Index of the current section being evaluated.
		sections (list[Section]): List of sections in the evaluation.
		situation_established (bool): Flag indicating if the situation is established.
		unconcious_not_breathing (bool): Flag indicating if the patient is unconscious and not breathing.
		is_child (bool): Flag indicating if the patient is a child.
		evaluateBotPrompts (EvaluateBotPrompts): All prompts for the EvaluateBot.
		evaluateBotResult (Optional[str]): Simple result of the evaluation in Markdown format.
		evaluateBotResultDetailed (Optional[str]): Detailed result of the evaluation in Markdown format.
	"""

	evaluateBotPrompts: EvaluateBotPrompts

	baseDataEvaluateBot: BaseData

	evaluateBotState: EvaluateBotState
