from pydantic import BaseModel
from typing import List, Optional
from app.modules.generateReport.GenerateReport import GraphState


class ImageSchema(BaseModel):
	image: str
	description: Optional[str] = None

	class Config:
		orm_mode = True


class BaseDataSchema(BaseModel):
	transcription: str
	location: str
	appname: str
	time: str
	images: List[ImageSchema] = []

	class Config:
		orm_mode = True


class SummaryBotPromptsSchema(BaseModel):
	transcription_prompt: str
	intention_prompt: str
	describe_case_prompt: str
	describe_image_prompt: str
	generate_summary_prompt: str

	class Config:
		orm_mode = True


class EvaluateBotPromptsSchema(BaseModel):
	summarize_section_prompt: str
	evaluate_section_prompt: str
	evaluate_section_not_breathing_prompt: str
	pairwise_prompt: str
	extract_advices_prompt: str

	class Config:
		orm_mode = True


class GetReportResponse(BaseModel):
	state: GraphState
	finished: bool
	id: str
	created_at: Optional[str] = None

	class Config:
		orm_mode = True
