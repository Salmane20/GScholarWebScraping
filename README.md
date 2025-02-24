# Google Scholar API

This API allows you to fetch academic information from Google Scholar, including professor profiles, publications, and citation metrics.

## Features

- Search for professor profiles
- Retrieve academic metrics (citations, h-index, i10-index)
- Get detailed publication information
- Automatic publication type classification
- Rate limiting to avoid Google Scholar blocks

## Setup

1. Clone this repository:
```bash
git clone <your-repo-url>
cd GScholarWebScraping
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

Start the API server:
```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

## Deployment to Render.com (Free Hosting)

1. Create a [Render.com](https://render.com) account

2. Click "New +" and select "Web Service"

3. Connect your GitHub repository

4. Fill in the deployment information:
   - Name: `scholar-api` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

5. Click "Create Web Service"

Your API will be deployed and available at `https://your-app-name.onrender.com`

## API Endpoints

### 1. Root Endpoint
- URL: `/`
- Method: `GET`
- Description: Welcome message and API status check
- Response: `{"message": "Welcome to Scholar Scraper API"}`

### 2. Search Professor
- URL: `/search/{professor_name}`
- Method: `GET`
- Parameters:
  - `professor_name` (path parameter): Name of the professor to search
  - `max_publications` (query parameter, optional): Limit the number of publications returned
- Response: JSON object containing:
  - Professor's name
  - Affiliation
  - Total citations
  - H-index
  - i10-index
  - Research interests
  - Profile URL
  - List of publications

### 3. Health Check
- URL: `/health`
- Method: `GET`
- Description: Service health status
- Response: `{"status": "healthy"}`

Example request:
```bash
curl http://localhost:8000/search/John%20Doe?max_publications=10
```

## Response Format

```json
{
    "name": "John Doe",
    "affiliation": "Example University",
    "total_citations": 1000,
    "h_index": 20,
    "i10_index": 30,
    "interests": ["Machine Learning", "AI"],
    "profile_url": "https://scholar.google.com/...",
    "publications": [
        {
            "title": "Example Paper",
            "year": "2023",
            "authors": "John Doe, Jane Smith",
            "journal": "Example Journal",
            "citations": 50,
            "url": "https://...",
            "type": "Journal Article",
            "venue": "Example Conference",
            "abstract": "Paper abstract...",
            "keywords": ["AI", "ML"],
            "doi": "10.1234/example",
            "citations_per_year": {"2023": 10, "2022": 20}
        }
        // ... more publications
    ]
}
```

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Successful request
- 404: Professor not found
- 500: Server error

## Rate Limiting

The API includes built-in rate limiting to avoid being blocked by Google Scholar. There's a 0.5-second delay between processing each publication.

## Interactive API Documentation

FastAPI provides automatic interactive API documentation. After starting the server, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes

- The API uses the `scholarly` library which scrapes Google Scholar. Be mindful of usage limits.
- For production use, consider implementing additional rate limiting and error handling.
- Google Scholar may occasionally block requests if too many are made in a short time.
- The free tier on Render.com may have some limitations:
  - Cold starts after 15 minutes of inactivity
  - Limited monthly runtime
  - Slower response times compared to paid tiers