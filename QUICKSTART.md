# arXiv Feed Viewer - Quick Start Guide

## Get Started in 4 Steps

### 1. Install and Configure

```bash
git clone https://github.com/juhanimerilehto/arxiv-feed-viewer.git
cd arxiv-feed-viewer
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your Grok API key:
```bash
cp .env.example .env
```

### 2. Initialize and Fetch Papers

```bash
python scripts/init_db.py
python backend/tasks/daily_fetch.py
```

### 3. Start the Server

```bash
python run_server.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 4. Open Your Browser

Navigate to: **http://127.0.0.1:8000**

You should see the interface with:
- Green phosphor text on black background
- ASCII art header
- Three-column paper layout
- Navigation controls at the bottom

## Explore Papers

- **Navigate**: Use arrow keys or click PREV/NEXT buttons
- **Search**: Type keywords in the search box and click SEARCH
- **Bookmark**: Click the BOOKMARK button to save papers
- **View Bookmarks**: Click the BOOKMARKS button to see saved papers
- **Open PDF**: Click the PDF link to open the paper on arXiv

## API Documentation

Interactive API docs are available at: **http://127.0.0.1:8000/docs**

Endpoints:
- `GET /api/papers` - List all papers
- `GET /api/papers/{id}` - Get single paper with analysis
- `GET /api/papers/search?q=LLM` - Search papers
- `POST /api/bookmarks/` - Add bookmark
- `GET /api/bookmarks/` - List bookmarks

## Fetch More Papers

To fetch papers on demand:

```bash
python backend/tasks/daily_fetch.py
```

To change fetch settings, edit `.env`:

```env
ARXIV_DAYS_BACK=30     # Fetch last 30 days
ARXIV_MAX_RESULTS=50   # Fetch up to 50 papers
```

## Configuration

All settings are in `.env` (copy from `.env.example`):

```env
# API Keys
GROK_API_KEY=your_key_here

# Database
DATABASE_PATH=data/arxiv.db
PDF_STORAGE_PATH=data/pdfs

# arXiv Search Query
ARXIV_SEARCH_QUERY=cat:cs.CR AND (abs:LLM OR abs:"Large Language Model" OR abs:"Generative AI" OR abs:GenAI)
ARXIV_MAX_RESULTS=10
ARXIV_DAYS_BACK=7

# Server
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

## Set Up Daily Automation (Windows)

Run as Administrator:

```powershell
cd scripts
.\setup_task_scheduler.ps1
```

This creates a scheduled task that runs daily at 3:00 AM to fetch new papers.

## Troubleshooting

### Server won't start
- Make sure you activated the virtual environment: `venv\Scripts\activate`
- Check if port 8000 is already in use

### No papers showing
- Run `python backend/tasks/daily_fetch.py` to fetch papers
- Check `logs/daily_fetch.log` for errors
- Verify database exists: `data/arxiv.db`

### Grok analysis not working
- See `GROK_API_FIX.md` for details
- Papers will still be fetched and displayed without analysis
- Verify API key in `.env`

### Search not working
- Make sure database was initialized: `python scripts/init_db.py`
- Re-initialize if needed

## More Information

- **README.md** - Full documentation
- **GROK_API_FIX.md** - Grok API troubleshooting
