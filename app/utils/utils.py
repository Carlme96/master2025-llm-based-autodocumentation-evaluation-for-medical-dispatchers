import io
import pymupdf
from typing import Union
from docx import Document
from fastapi import UploadFile

import cv2
import base64
import numpy as np
import os


UPLOAD_FOLDER = os.path.join(os.getcwd(), "image_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


async def resizeAndSaveImg(
	image: UploadFile, max_h: int = 500, max_w: int = 500
) -> str:
	print("resizeAndSaveImg")

	contents = await image.read()
	nparr = np.frombuffer(contents, dtype=np.uint8)
	img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

	if img is None:
		raise ValueError(f"Failed to decode image: {image.filename}")

	h, w = img.shape[:2]
	ratio = w / h

	print("image shape", h, w)

	# Don't resize if the image is already within limits
	if h <= max_h and w <= max_w:
		temp_path = os.path.join(UPLOAD_FOLDER, image.filename)
		with open(temp_path, "wb") as f:
			f.write(contents)
		return temp_path  # Return original saved file path

	# Compute new dimensions while maintaining aspect ratio
	new_w, new_h = max_w, max_h
	if ratio > 1:  # Landscape image
		new_h = np.round(max_w / ratio).astype(int)
	elif ratio < 1:  # Portrait image
		new_w = np.round(ratio * max_h).astype(int)

	# Resize the image
	scaled_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

	print("resized image down to ", new_w, new_h)
	# Save the resized image to a temporary file
	temp_path = os.path.join(UPLOAD_FOLDER, image.filename)
	cv2.imwrite(temp_path, scaled_img)

	return temp_path  # Return the path to the saved resized image


# 672x672 Supported in New in LLaVA 1.6:
async def resizeAndDecodeImg(image: UploadFile, max_h: int = 500, max_w: int = 500):
	contents = await image.read()
	nparr = np.frombuffer(contents, dtype=np.uint8)
	img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	h, w = img.shape[:2]

	ratio = w / h

	# Dont resize if image is already smaller than the max
	if h <= max_h and w <= max_w:
		_, encoded_img = cv2.imencode(".PNG", img)
		return f"data:image/png;base64,{base64.b64encode(encoded_img).decode('utf-8')}"
	interp = cv2.INTER_AREA

	new_w = max_w
	new_h = max_h
	# Horizontal image
	if ratio > 1:
		new_h = np.round(max_w / ratio).astype(int)

	# Vertical image
	if ratio < 1:
		new_w = np.round(ratio * max_h).astype(int)

	scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp)
	_, encoded_img = cv2.imencode(".PNG", scaled_img)
	return f"data:image/png;base64,{base64.b64encode(encoded_img).decode('utf-8')}"


class TextLoader:
	def __init__(self, file: UploadFile) -> None:
		self.file = file

	async def load(self) -> Union[str]:
		if self.file.content_type == "application/pdf":
			return await self._load_pdf()
		elif self.file.content_type == "text/plain":
			return await self._load_text()
		elif self.file.content_type == "text/csv":
			return await self._load_text()
		elif (
			self.file.content_type
			== "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
		):
			return await self.load_doc()
		else:
			raise ValueError(f"Invalid file type: {self.file.content_type}")

	async def _load_pdf(self) -> None:
		contents = await self.file.read()  # Await the read operation
		doc = pymupdf.open(stream=contents, filetype="pdf")
		text = ""
		for page_num in range(doc.page_count):
			page = doc.load_page(page_num)
			text += page.get_text("text")
		return text

	async def _load_text(self) -> str:
		contents = await self.file.read()
		return contents.decode("utf-8")

	async def load_doc(self) -> str:
		contents = await self.file.read()
		doc = Document(io.BytesIO(contents))
		text = ""
		for para in doc.paragraphs:
			text += para.text
		return text


class ImageLoader:
	def __init__(self, images: list[UploadFile]) -> None:
		self.images = images

	async def load(self) -> list[str]:
		decoded_imgs = [await resizeAndDecodeImg(img) for img in self.images]
		return decoded_imgs
