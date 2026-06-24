# main.py
from fastapi import FastAPI, Query, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.services.qr_generator import create_qr_code

app = FastAPI(title="QR Code Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "សួស្តី! នេះជា QR Code Generator API"}

# ១. ប្តូរពី @app.get ទៅជា @app.post ដើម្បីអាចទទួល File ពី Frontend បាន
@app.post("/api/generate")
async def generate_qr_api(
    text: str = Form(...),
    type: str = Form("text"),
    fg_color: str = Form("#000000"),
    bg_color: str = Form("#ffffff"),
    space: int = Form(4),    # ទទួលយកតម្លៃ Space (គែម)
    size: int = Form(768),   # ទទួលយកតម្លៃទំហំ (Size)
    logo: Optional[UploadFile] = File(None)
):
    try:
        if not text:
            return {"error": "Text or Link cannot be empty"}
        
        logo_bytes = await logo.read() if logo else None
        
        # បញ្ជូនទិន្នន័យថ្មីទៅកាន់មុខងារ
        buffer = create_qr_code(
            data=text, 
            fg_color=fg_color, 
            bg_color=bg_color, 
            logo_bytes=logo_bytes,
            space=space,
            size=size
        )
        return StreamingResponse(buffer, media_type="image/png")
        
    except Exception as e:
        return {"error": str(e)}