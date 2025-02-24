from scholarly import scholarly
import json
from typing import Dict, List, Optional
import time

class ScholarScraper:
    def __init__(self):
        """Initialize the ScholarScraper."""
        pass

    def search_professor(self, name: str) -> Optional[Dict]:
        """
        Search for a professor on Google Scholar and return their profile information.
        
        Args:
            name (str): The name of the professor to search for
            
        Returns:
            Optional[Dict]: Dictionary containing professor's information or None if not found
        """
        try:
            # Search for the professor
            search_query = scholarly.search_author(name)
            # Get the first result (most relevant)
            author = next(search_query)
            # Fill in all available author data
            author = scholarly.fill(author)
            return author
        except StopIteration:
            print(f"No results found for professor: {name}")
            return None
        except Exception as e:
            print(f"An error occurred while searching for {name}: {str(e)}")
            return None

    def determine_publication_type(self, pub_data: Dict) -> str:
        """
        Determine the type of publication based on available information.
        
        Args:
            pub_data (Dict): Publication data
            
        Returns:
            str: Type of publication
        """
        bib = pub_data.get('bib', {})
        venue = bib.get('venue', '').lower()
        journal = bib.get('journal', '').lower()
        
        # Check for conference indicators
        if any(word in venue for word in ['conference', 'conf', 'proceedings', 'proc']):
            return 'Conference Paper'
        elif any(word in journal for word in ['conference', 'conf', 'proceedings', 'proc']):
            return 'Conference Paper'
            
        # Check for journal/article indicators
        elif journal or any(word in venue for word in ['journal', 'transactions']):
            return 'Journal Article'
            
        # Check for book indicators
        elif any(word in venue for word in ['book', 'chapter']):
            return 'Book/Book Chapter'
            
        # Check for thesis/dissertation
        elif any(word in venue for word in ['thesis', 'dissertation']):
            return 'Thesis/Dissertation'
            
        # Default case
        return 'Other'

    def process_publication(self, pub) -> Optional[Dict]:
        """
        Process a single publication and return its information.
        
        Args:
            pub: Publication data from scholarly
            
        Returns:
            Optional[Dict]: Processed publication information or None if error
        """
        try:
            # Fill in complete publication data
            filled_pub = scholarly.fill(pub)
            pub_type = self.determine_publication_type(filled_pub)
            bib = filled_pub.get('bib', {})
            
            publication_info = {
                'title': bib.get('title', ''),
                'year': bib.get('pub_year', ''),
                'authors': bib.get('author', ''),
                'journal': bib.get('journal', ''),
                'citations': filled_pub.get('num_citations', 0),
                'url': filled_pub.get('pub_url', ''),
                'type': pub_type,
                'venue': bib.get('venue', ''),
                # Additional information
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
            return publication_info
        except Exception as e:
            print(f"Error processing publication: {str(e)}")
            return None

    def iterate_publications(self, author_data: Dict):
        """
        Generator function to iterate through publications one at a time.
        
        Args:
            author_data (Dict): The author data returned from search_professor
            
        Yields:
            Dict: Publication information
        """
        if not author_data or 'publications' not in author_data:
            return

        for pub in author_data['publications']:
            pub_info = self.process_publication(pub)
            if pub_info:
                yield pub_info
            time.sleep(0.5)  # Add small delay to avoid overwhelming the API

def format_citations_per_year(cites_per_year: Dict) -> str:
    """Format citations per year into a readable string."""
    if not cites_per_year:
        return "No yearly citation data available"
    
    years = sorted(cites_per_year.keys())
    result = []
    for year in years:
        result.append(f"{year}: {cites_per_year[year]}")
    return ", ".join(result)

def main():
    """Main function to demonstrate usage."""
    scraper = ScholarScraper()
    
    # Example usage
    professor_name = input("Enter professor name: ")
    
    # Search for professor
    author_data = scraper.search_professor(professor_name)
    
    if author_data:
        print("\n" + "="*80)
        print("SCHOLAR PROFILE")
        print("="*80)
        print(f"Name: {author_data.get('name', 'N/A')}")
        print(f"Affiliation: {author_data.get('affiliation', 'N/A')}")
        print(f"Total Citations: {author_data.get('citedby', 0)}")
        print(f"h-index: {author_data.get('hindex', 'N/A')}")
        print(f"i10-index: {author_data.get('i10index', 'N/A')}")
        print(f"Research Interests: {', '.join(author_data.get('interests', []))}")
        print(f"Profile URL: {author_data.get('url_picture', 'N/A')}")
        print("\nFetching publications (press Ctrl+C to stop)...")
        
        try:
            for i, pub in enumerate(scraper.iterate_publications(author_data), 1):
                print("\n" + "="*80)
                print(f"PUBLICATION #{i}")
                print("="*80)
                
                # Basic Information
                print(f"\nTITLE: {pub['title']}")
                print(f"TYPE: {pub['type']}")
                print(f"YEAR: {pub['year']}")
                
                # Authors
                print("\nAUTHORS:")
                authors = pub['authors'].split(" and ") if isinstance(pub['authors'], str) else pub['authors']
                for idx, author in enumerate(authors, 1):
                    print(f"  {idx}. {author}")
                
                # Publication Venue
                print("\nPUBLICATION DETAILS:")
                venue = pub['venue'] or pub['journal']
                if venue:
                    print(f"  Venue/Journal: {venue}")
                if pub['volume']:
                    print(f"  Volume: {pub['volume']}")
                if pub['issue']:
                    print(f"  Issue: {pub['issue']}")
                if pub['pages']:
                    print(f"  Pages: {pub['pages']}")
                if pub['publisher']:
                    print(f"  Publisher: {pub['publisher']}")
                
                # Impact Metrics
                print("\nIMPACT METRICS:")
                print(f"  Total Citations: {pub['citations']}")
                print(f"  Google Scholar Rank: {pub['gsrank'] if pub['gsrank'] is not None else 'N/A'}")
                print("  Citations per year:")
                for year, count in sorted(pub['citations_per_year'].items()):
                    print(f"    {year}: {count}")
                
                # Abstract
                print("\nABSTRACT:")
                print(f"  {pub['abstract'][:500]}..." if len(pub['abstract']) > 500 else f"  {pub['abstract']}")
                
                # Additional Information
                print("\nADDITIONAL INFORMATION:")
                if pub['keywords']:
                    print(f"  Keywords: {', '.join(pub['keywords'])}")
                if pub['doi']:
                    print(f"  DOI: {pub['doi']}")
                if pub['eprint']:
                    print(f"  ePrint: {pub['eprint']}")
                print(f"  URL: {pub['url']}")
                    
        except KeyboardInterrupt:
            print("\n\nStopped by user.")
            
if __name__ == "__main__":
    main() 