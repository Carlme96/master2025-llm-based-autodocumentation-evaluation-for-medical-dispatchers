from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.utils import UPLOAD_FOLDER
from fastapi.middleware.cors import CORSMiddleware

from .routers import (
	generateReport,
)
from .config import load_env

# load environment variables from .env file in the root directory
load_env()


def cleanup_temp_files():
	import os

	# remove all files in the temp directory
	for file in os.listdir(UPLOAD_FOLDER):
		os.remove(os.path.join(UPLOAD_FOLDER, file))

	print("Cleaned up image files")


@asynccontextmanager
async def lifespan(app: FastAPI):
	yield cleanup_temp_files()


app = FastAPI(lifespan=lifespan)

origins = ["*"]
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(generateReport.router)


# Root route
@app.get("/")
def read_root():
	return {"Hello": "World"}
