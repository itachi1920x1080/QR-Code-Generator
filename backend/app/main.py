# main.py
from fastapi import FastAPI,Query
from fastapi.responses import  StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.services.qr_generator import create_qr_code
app =FastAPI(title="QR Code Generator API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials =True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message":"សួស្តី! នេះជា QR Code Generator API"}
@app.get("/api/generate")
def generate_qr_api(text:str= Query(...,description="អត្ថបទ ឬ Link ដែលចង់បំប្លែងជា QR Code"),type:str="text"):
    try:
        if not text:
            raise ValueError("Text or Link cannot be empty")
        buffer = create_qr_code(text)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}