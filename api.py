from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from scholarly import scholarly
import time
import os

app = FastAPI(
    title="Scholar Scraper API",
    description="API for searching Google Scholar profiles and publications",
    version="1.0.0"
)

# Add CORS middleware with more specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React default port
        "http://localhost:8000",     # Local development
        "https://*.render.com",      # Render.com domains
        "https://*.vercel.app"       # Vercel domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScholarProfile(BaseModel):
    name: str
    affiliation: Optional[str] = None
    total_citations: int = 0
    h_index: Optional[int] = None
    i10_index: Optional[int] = None
    interests: List[str] = []
    profile_url: Optional[str] = None
    publications: List[Dict] = []

class ScholarScraper:
    def determine_publication_type(self, pub_data: Dict) -> str:
        bib = pub_data.get('bib', {})
        venue = bib.get('venue', '').lower()
        journal = bib.get('journal', '').lower()
        
        if any(word in venue for word in ['conference', 'conf', 'proceedings', 'proc']):
            return 'Conference Paper'
        elif any(word in journal for word in ['conference', 'conf', 'proceedings', 'proc']):
            return 'Conference Paper'
        elif journal or any(word in venue for word in ['journal', 'transactions']):
            return 'Journal Article'
        elif any(word in venue for word in ['book', 'chapter']):
            return 'Book/Book Chapter'
        elif any(word in venue for word in ['thesis', 'dissertation']):
            return 'Thesis/Dissertation'
        return 'Other'

    def process_publication(self, pub) -> Optional[Dict]:
        try:
            filled_pub = scholarly.fill(pub)
            pub_type = self.determine_publication_type(filled_pub)
            bib = filled_pub.get('bib', {})
            
            return {
                'title': bib.get('title', ''),
                'year': bib.get('pub_year', ''),
                'authors': bib.get('author', ''),
                'journal': bib.get('journal', ''),
                'citations': filled_pub.get('num_citations', 0),
                'url': filled_pub.get('pub_url', ''),
                'type': pub_type,
                'venue': bib.get('venue', ''),
                'abstract': bib.get('abstract', 'No abstract available'),
                'keywords': bib.get('keywords', []),
                'doi': bib.get('doi', ''),
                'volume': bib.get('volume', ''),
                'issue': bib.get('number', ''),
                'pages': bib.get('pages', ''),
                'publisher': bib.get('publisher', ''),
                'citations_per_year': filled_pub.get('cites_per_year', {}),
                'gsrank': filled_pub.get('gsrank', None),
                'eprint': bib.get('eprint', ''),
            }
        except Exception as e:
            print(f"Error processing publication: {str(e)}")
            return None

scraper = ScholarScraper()

@app.get("/")
async def root():
    return {
        "message": "Welcome to Scholar Scraper API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/search/{professor_name}", response_model=ScholarProfile)
async def search_professor(professor_name: str, max_publications: Optional[int] = None):
    try:
        # Search for the professor
        search_query = scholarly.search_author(professor_name)
        author = next(search_query)
        author = scholarly.fill(author)
        
        # Process publications
        publications = []
        try:
            for i, pub in enumerate(author.get('publications', [])):
                if max_publications and i >= max_publications:
                    break
                    
                pub_info = scraper.process_publication(pub)
                if pub_info:
                    publications.append(pub_info)
                time.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            print(f"Error processing publications: {str(e)}")
        
        return ScholarProfile(
            name=author.get('name', ''),
            affiliation=author.get('affiliation', ''),
            total_citations=author.get('citedby', 0),
            h_index=author.get('hindex'),
            i10_index=author.get('i10index'),
            interests=author.get('interests', []),
            profile_url=author.get('url_picture', ''),
            publications=publications
        )
        
    except StopIteration:
        raise HTTPException(status_code=404, detail=f"No results found for professor: {professor_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint for monitoring
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 