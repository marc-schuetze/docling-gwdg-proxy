#!/usr/bin/env python3
"""
Docling GWDG Proxy
Forwards file uploads from Open WebUI to GWDG docling API

Copyright (c) 2025 Marc Schütze / ZKM | Karlsruhe
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import os
import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

GWDG_API_URL = os.getenv("GWDG_API_URL", "https://chat-ai.academiccloud.de/v1/documents/convert")
GWDG_API_KEY = os.getenv("GWDG_API_KEY", "")

if not GWDG_API_KEY:
    print("WARNING: GWDG_API_KEY not set")

app = FastAPI(title="Docling GWDG Proxy")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/v1/convert/file")
async def convert_file(
    files: UploadFile = File(...),
    image_export_mode: Optional[str] = Form(None),
    do_picture_description: Optional[str] = Form(None),
    picture_description_api: Optional[str] = Form(None),
    do_ocr: Optional[str] = Form(None),
    force_ocr: Optional[str] = Form(None),
    pdf_backend: Optional[str] = Form(None),
    table_mode: Optional[str] = Form(None),
    pipeline: Optional[str] = Form(None),
):
    if not GWDG_API_KEY:
        raise HTTPException(status_code=500, detail="GWDG_API_KEY not configured")
    
    print(f"\n📥 Received: {files.filename} ({files.content_type})")
    
    try:
        file_content = await files.read()
        print(f"   Size: {len(file_content)} bytes")
        
        gwdg_files = {
            'document': (files.filename, file_content, files.content_type)
        }
        
        params = {'response_type': 'markdown'}
        headers = {
            'Authorization': f'Bearer {GWDG_API_KEY}',
            'accept': 'application/json'
        }
        
        print(f"🚀 Forwarding to GWDG...")
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                GWDG_API_URL,
                files=gwdg_files,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            gwdg_data = response.json()
        
        print(f"✅ Success")
        
        docling_response = {
            "document": {
                "md_content": gwdg_data.get("markdown", ""),
                "json_content": {},
                "html_content": "",
                "text_content": "",
                "doctags_content": ""
            },
            "status": "success",
            "processing_time": 0.0,
            "timings": {},
            "errors": []
        }
        
        return JSONResponse(content=docling_response)
    
    except httpx.HTTPStatusError as e:
        error_msg = f"GWDG API error: {e.response.status_code}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=e.response.status_code, detail=error_msg)
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/")
async def root():
    return {
        "name": "Docling GWDG Proxy",
        "status": "ready",
        "gwdg_configured": bool(GWDG_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Docling GWDG Proxy")
    print(f"GWDG API Key: {'configured' if GWDG_API_KEY else 'missing'}")
    uvicorn.run("proxy:app", host="0.0.0.0", port=5001, reload=True)
