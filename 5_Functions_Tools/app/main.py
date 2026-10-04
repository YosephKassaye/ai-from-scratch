from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from enum import Enum
import io


load_dotenv()

app = FastAPI(
    title="AI Learning API",
    description="Learning FastAPI and OpenAI API",
    version="1.0.0"
)

client = OpenAI()

