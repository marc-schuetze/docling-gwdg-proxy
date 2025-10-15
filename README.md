# Docling GWDG Proxy

Proxy service that translates between Open WebUI's docling-serve API format and GWDG's docling API.

## What It Does

Open WebUI expects a docling-serve compatible API. GWDG provides a docling API with a different format. This proxy bridges the gap:

```
Open WebUI → Proxy → GWDG Docling API
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- GWDG API key ([request here](https://kisski.gwdg.de/en/leistungen/2-02-llm-service))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/docling-gwdg-proxy.git
cd docling-gwdg-proxy
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your GWDG_API_KEY
```

3. Start the service:
```bash
docker compose up -d
```

4. Test:
```bash
curl http://localhost:5001/health
```

## Configuration

### Environment Variables

- `GWDG_API_KEY` (required): Your GWDG API key
- `GWDG_API_URL` (optional): GWDG API endpoint (default: https://chat-ai.academiccloud.de/v1/documents/convert)

### Open WebUI Integration

In Open WebUI settings:
1. Go to Settings → Documents
2. Set Docling URL: `http://docling-proxy:5001` (or your host:port)
3. Save

## API Endpoints

### `POST /v1/convert/file`

Converts documents from Open WebUI format to GWDG format.

**Request:**
- Multipart form data with file upload
- Field name: `files`

**Response:**
```json
{
  "document": {
    "md_content": "# Converted markdown content...",
    "json_content": {},
    "html_content": "",
    "text_content": "",
    "doctags_content": ""
  },
  "status": "success",
  "processing_time": 0.0,
  "errors": []
}
```

### `GET /health`

Health check endpoint.

### `GET /`

Service status and configuration info.

## Development

Run locally without Docker:

```bash
cd app
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r ../requirements.txt
export GWDG_API_KEY=your_key_here
python proxy.py
```

## Architecture

The proxy:
1. Receives multipart file upload from Open WebUI
2. Extracts file content and metadata
3. Forwards file to GWDG API with Bearer authentication
4. Receives markdown response from GWDG
5. Transforms to docling-serve compatible format
6. Returns to Open WebUI

## Requirements

- Python 3.12+
- FastAPI
- httpx
- See `requirements.txt` for full list

## License

MIT

## Credits

- [Docling](https://github.com/docling-project/docling) by IBM Research
- [GWDG](https://gwdg.de) for hosting the docling service
- [Open WebUI](https://github.com/open-webui/open-webui)