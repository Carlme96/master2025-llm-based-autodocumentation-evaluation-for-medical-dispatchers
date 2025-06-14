import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


# TODO: Might be unnecessary when using docker. Check if it is necessary to load the .env file.
def load_env():
	current_dir = os.path.dirname(os.path.abspath(__file__))
	env_file_path = os.path.join(current_dir, ".env")

	if os.path.exists(env_file_path):
		load_dotenv(env_file_path, override=True)
		print("Loaded environment variables")
	else:
		print(f"Error: .env file not found at {env_file_path}")


class ModelSettings(BaseSettings):
	model_config = SettingsConfigDict(extra="ignore")

	model: Optional[str] = None
	base_url: Optional[str] = None
	temperature: Optional[float] = None
	api_key: Optional[str] = None
	api_version: Optional[str] = None
	azure_endpoint: Optional[str] = None
	max_tokens: Optional[int] = None
	model_kwargs: Optional[dict] = None


class EmbeddingModelSettings(BaseSettings):
	model_config = SettingsConfigDict(extra="ignore")
	model: Optional[str] = None
	base_url: Optional[str] = None


class ParseBotSettings(BaseSettings):
	model_config = SettingsConfigDict(extra="ignore")
	agent: ModelSettings
	vision: ModelSettings


class EvaluateBotSettings(BaseSettings):
	model_config = SettingsConfigDict(extra="ignore")
	embedding: EmbeddingModelSettings
	summary: ModelSettings
	comparison: ModelSettings
	evaluate: ModelSettings
	advices: ModelSettings
	fallback: ModelSettings


class SummaryBotSettings(BaseSettings):
	model_config = SettingsConfigDict(extra="ignore")
	embedding: ModelSettings
	describecase: ModelSettings
	summarize: ModelSettings
	vision: ModelSettings


class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=".env", env_nested_delimiter="__", extra="allow"
	)

	parsebot: Optional[ParseBotSettings] = None

	evaluatebot: Optional[EvaluateBotSettings] = None

	summarybot: Optional[SummaryBotSettings] = None

	# Keys
	tavily_api_key: Optional[str] = None
	azure_openai_api_key: Optional[str] = None
	azure_openai_endpoint: Optional[str] = None
	openai_api_version: Optional[str] = None
	langsmith_api_key: Optional[str] = None
