from asyncio import sleep
from typing import List
import uuid
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.modules.basedata import BaseData, transcription_ladder
from app.modules.generateReport.GenerateReport import (
	GenerateReport,
	GenerateReportProps,
)
from app.modules.evaluateBot.prompts import (
	EvaluateBotPrompts,
	evaluate_bot_prompts,
	evaluate_bot_prompts_descriptions,
)
from app.modules.summaryBot.prompts import (
	SummaryBotPrompts,
	summary_bot_prompts,
	summary_bot_prompts_description,
)
from app.schemas import (
	GetReportResponse,
)

router = APIRouter(
	prefix="/report",
	tags=["Report"],
	dependencies=[],
	responses={404: {"description": "Not found"}},
)

reportGenerator = GenerateReport()


example_basedata = BaseData(
	transcription=transcription_ladder,
	location="Stavanger, Norway",
	time="06.05.2025 22:45",
	appname="Emergency report and evaluation",
)

example_data: GenerateReportProps = GenerateReportProps(
	evaluateBotPrompts=evaluate_bot_prompts,
	baseData=example_basedata,
	summaryBotPrompts=summary_bot_prompts,
)


async def report_generate_init(props: GenerateReportProps, id: str):
	await reportGenerator.generate(props, id)


class ReportGenerateResponse(BaseModel):
	id: str


@router.post("/report-generate", response_model=ReportGenerateResponse)
async def report_generate(
	background_tasks: BackgroundTasks, data: GenerateReportProps = example_data
):
	id = str(uuid.uuid4())
	background_tasks.add_task(report_generate_init, data, id)
	await sleep(0.5)
	return ReportGenerateResponse(id=id)


class GetReportsResults(BaseModel):
	id: str


@router.get("/get_reports", response_model=List[GetReportsResults])
async def get_reports():
	ids = await reportGenerator.get_reports()
	print(ids)
	return [GetReportsResults(id=id) for id in ids]


@router.get("/get_report/{id}", response_model=GetReportResponse)
async def get_report(id: str):
	result, rawresult = await reportGenerator.get_report(id)

	try:
		finished = len(rawresult.next) == 0
		id = rawresult.config["configurable"]["thread_id"]  # type: ignore
		created_at = rawresult.created_at
	except Exception as e:
		print(f"Error parsing state: {e}")
		return JSONResponse(
			status_code=500,
			content={"message": "Error parsing state", "error": str(e)},
		)
	return GetReportResponse(
		state=result, finished=finished, id=id, created_at=created_at
	)


class ExamplePrompts(BaseModel):
	props: GenerateReportProps
	summaryBotPromptDescriptions: SummaryBotPrompts
	evaluateBotPromptDescriptions: EvaluateBotPrompts


example_prompts = ExamplePrompts(
	props=example_data,
	summaryBotPromptDescriptions=summary_bot_prompts_description,
	evaluateBotPromptDescriptions=evaluate_bot_prompts_descriptions,
)


@router.get("/get-example-prompts", response_model=ExamplePrompts)
def get_example_prompts():
	return example_prompts
