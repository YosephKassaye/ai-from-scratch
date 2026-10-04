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

class CustomerDecision(BaseModel):
    customer_name: str
    risk_level: str
    approved: bool
    
class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class LoanRequest(BaseModel):
    customer_name: str
    income: float
    credit_score: int
    debt: float

class PersonInfo(BaseModel):
    name: str
    company: str
    email: str

class LoanDecision(BaseModel):
    customer_name: str
    risk_level: RiskLevel
    approved: bool
    reason: str

class PersonInfo(BaseModel):
    name: str
    company: str
    email: str

from typing import Literal


class ClassificationResult(BaseModel):
    category: Literal[
        "Billing",
        "Technical",
        "Account",
        "Other"
    ]
    reason: str

@app.post("/customer_decision")
def customer_decision(decision: CustomerDecision):
    prompt = f"""
    Customer Name: {decision.customer_name}
    Risk Level: {decision.risk_level}
    Approved: {decision.approved}

    Please provide a brief summary of the customer's decision.
    """

    response = client.responses.parse(
        model="gpt-5",
        input=prompt
    )
    result = response.output_parsed
    print("OpenAI Response:", result)
    return {
            "customer_name": decision.customer_name,
            "risk_level": decision.risk_level,
            "approved": decision.approved,
            "summary": response.output_text
        }    
    

@app.post("/loan-decision", response_model=LoanDecision)
def loan_decision(request: LoanRequest):

    response = client.responses.parse(
        model="gpt-6-luna",
        instructions="""
        Evaluate the application conservatively.

        Consider:
        - Income
        - Credit score
        - Existing debt
        """,
        input=f"""
        Customer: {request.customer_name}
        Income: {request.income}
        Credit Score: {request.credit_score}
        Debt: {request.debt}
        """,
        text_format=LoanDecision
    )

    return response.output_parsed

class MessageRequest(BaseModel):
    message: str


class MeetingRequest(BaseModel):
    notes: str

@app.post("/classify", response_model=ClassificationResult)
def classify(request: MessageRequest):

    response = client.responses.parse(
        model="gpt-6-luna",
        instructions="""
        Classify the customer message.

        Available categories:
        Billing
        Technical
        Account
        Other
        """,
        input=request.message,
        text_format=ClassificationResult
    )

    return response.output_parsed

@app.post("/person_info", response_model=PersonInfo)
def get_person_info(request: MessageRequest):
    
    response = client.responses.parse(
    model="gpt-6-luna",
    instructions="Extract the requested information from the user's text.",
    input=request.message,
    text_format=PersonInfo
    )

    return response.output_parsed


class ActionItem(BaseModel):
    task: str
    owner: str
    due_date: str | None = None


class MeetingSummary(BaseModel):
    summary: str
    decisions: list[str]
    action_items: list[ActionItem]
    
@app.post("/meeting_summary", response_model=MeetingSummary)
def meeting_summary(request: MeetingRequest):
    response = client.responses.parse(
    model="gpt-6-luna",
    instructions="""
    Analyze the meeting notes.

    Extract:
    - Summary
    - Decisions
    - Action items
    """,
    input=request.notes,
    text_format=MeetingSummary
  )

    return response.output_parsed

# Sample input 
# {
#   "notes": "User login feature completed and handed over to QA for testing.\nQA identified two medium-priority bugs requiring fixes.\nMinor UI improvements were discussed and approved.\nMarketing team finalized the launch plan draft.\nProduct screenshots to be provided by Wednesday.\nSystem testing scheduled to begin next Monday.\nCustomer beta invitation postponed by three days for additional validation.\nCurrent project timeline remains on schedule.\nRisk identified: potential delays if critical defects are discovered during testing.\nConcern raised regarding resource availability due to upcoming team vacations.\n\nAction Items\n\nFix QA-reported bugs.\nDeliver approved product screenshots.\nPrepare system test plan.\nUpdate project status dashboard."
# }

class SupportTicketResult(BaseModel):
    category: str
    priority: Literal["Low", "Medium", "High", "Critical"]
    summary: str
    requires_human: bool
    
@app.post("/support_ticket", response_model=SupportTicketResult)
def support_ticket(request: MessageRequest):

    response = client.responses.parse(
    model="gpt-6-luna",
    input=request.message,
    text_format=SupportTicketResult
    )

    return response.output_parsed

# Request coming from your React/client application
class DocumentRequest(BaseModel):
    document: str


# Structured response you want from OpenAI
class DocumentAnalysis(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    risks: list[str]
    recommendations: list[str]


@app.post("/analyze-document", response_model=DocumentAnalysis)
def analyze_document(request: DocumentRequest):

    try:
        response = client.responses.parse(
            model="gpt-6-luna",
            instructions="""
            Analyze the provided document.

            Return:
            - A concise title
            - A clear summary
            - The main key points
            - Any risks or concerns
            - Practical recommendations
            """,
            input=request.document,
            text_format=DocumentAnalysis
        )

        return response.output_parsed

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/analyze-document_pdf", response_model=DocumentAnalysis)
async def analyze_document(
    file: UploadFile = File(...)
):

    try:

        # -----------------------------
        # 1. Read uploaded file
        # -----------------------------
        contents = await file.read()

        # -----------------------------
        # 2. Extract text
        # -----------------------------
        if file.content_type == "application/pdf":

            pdf = PdfReader(io.BytesIO(contents))

            document_text = ""

            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    document_text += text + "\n"

        elif file.content_type == "text/plain":

            document_text = contents.decode("utf-8")

        else:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are currently supported."
            )

        # -----------------------------
        # 3. Validate extracted text
        # -----------------------------
        if not document_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the uploaded document."
            )

        # -----------------------------
        # 4. Send document to OpenAI
        # -----------------------------
        response = client.responses.parse(
            model="gpt-6-luna",
            instructions="""
            Analyze the uploaded document.

            Return:
            - A concise title
            - A clear summary
            - Important key points
            - Risks or concerns
            - Practical recommendations
            """,
            input=document_text,
            text_format=DocumentAnalysis
        )

        # -----------------------------
        # 5. Return structured result
        # -----------------------------
        return response.output_parsed

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )