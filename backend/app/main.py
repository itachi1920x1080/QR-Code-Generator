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
    # ២. ប្រើប្រាស់ Form(...) ជំនួស Query(...)
    text: str = Form(..., description="អត្ថបទ ឬ Link ដែលចង់បំប្លែងជា QR Code"),
    type: str = Form("text"),
    fg_color: str = Form("black", description="ពណ៌ផ្ទៃខាងមុខ"),
    bg_color: str = Form("white", description="ពណ៌ផ្ទៃខាងក្រោយ"),
    logo: Optional[UploadFile] = File(None, description="រូបភាព Logo នៅកណ្តាល")
):
    try:
        if not text:
            return {"error": "Text or Link cannot be empty"}
        
        # ៣. អានទិន្នន័យរូបភាព (ប្រសិនបើអ្នកប្រើប្រាស់មាន Upload Logo)
        logo_bytes = await logo.read() if logo else None
        
        # ៤. បញ្ជូនទិន្នន័យទាំងអស់ទៅកាន់មុខងារបង្កើត QR
        buffer = create_qr_code(
            data=text, 
            fg_color=fg_color, 
            bg_color=bg_color, 
            logo_bytes=logo_bytes
        )
        return StreamingResponse(buffer, media_type="image/png")
        
    except Exception as e:
        return {"error": str(e)}