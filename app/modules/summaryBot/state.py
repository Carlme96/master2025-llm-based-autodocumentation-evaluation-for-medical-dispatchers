from typing import Optional
from pydantic import BaseModel

from app.modules.basedata import BaseData, ImageDescription
from .prompts import SummaryBotPrompts


class SummaryBotState(BaseModel):
	case_description: str = ""
	steps: list[str] = []
	summaryBotResult: Optional[str] = None


class GraphState(BaseModel):
	summaryBotState: SummaryBotState
	imageDescriptions: list[ImageDescription] = []
	summaryBotPrompts: SummaryBotPrompts
	baseDataSummaryBot: BaseData
