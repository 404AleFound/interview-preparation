import urllib.request
import json
import time

url = "https://api.semanticscholar.org/graph/v1/paper/search?query=6d+pose+estimation&year=2023-2026&limit=100&fields=title,authors,year,venue,citationCount,externalIds,openAccessPdf"

try:
    print("Fetching from Semantic Scholar...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        papers = data.get('data', [])
        
        top_venues = ['cvpr', 'iccv', 'eccv', 'neurips', 'iclr', 'icra', 'iros', 'computer vision and pattern recognition', 'european conference on computer vision', 'international conference on computer vision', 'nips']
        
        filtered = []
        for p in papers:
            v_name = (p.get('venue') or '').lower()
            if any(tv in v_name for tv in top_venues) or v_name.upper() in ['CVPR', 'ICCV', 'ECCV', 'NEURIPS', 'ICLR', 'ICRA', 'IROS', 'NIPS']:
                filtered.append(p)
        
        filtered.sort(key=lambda x: x.get('citationCount') or 0, reverse=True)
        
        for i, p in enumerate(filtered[:10], 1):
            authors = ", ".join([a.get('name', '') for a in p.get('authors', [])[:3]]) + (" et al." if len(p.get('authors', [])) > 3 else "")
            pdf = "✓" if p.get('openAccessPdf') else (f"✓ arXiv" if 'ArXiv' in (p.get('externalIds') or {}) else "✗")
            title = p.get('title', '').replace('\n', ' ')
            venue = p.get('venue', 'Unknown')
            year = p.get('year', '')
            cites = p.get('citationCount', 0)
            arxiv_id = (p.get('externalIds') or {}).get('ArXiv', '')
            pdf_link = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else (p.get('openAccessPdf') or {}).get('url', '')
            print(f"| {title} | {year} | {venue} | {cites} | {'Yes' if pdf_link else 'No'} |")

except Exception as e:
    print(f"Semantic Scholar Error: {e}")
    # Fallback to arXiv
    print("Falling back to arXiv API...")
    import xml.etree.ElementTree as ET
    import re
    
    arxiv_url = "http://export.arxiv.org/api/query?search_query=all:%226d+pose+estimation%22&sortBy=submittedDate&sortOrder=descending&max_results=300"
    try:
        req = urllib.request.Request(arxiv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode('utf-8')
            
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        papers = []
        top_venues = r'(CVPR|ICCV|ECCV|NeurIPS|ICLR|ICRA|IROS)'
        
        for entry in root.findall('atom:entry', ns):
            published = entry.find('atom:published', ns).text
            year = int(published[:4])
            if year < 2023:
                continue
                
            title = entry.find('atom:title', ns).text.replace('\n', ' ').strip()
            authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
            
            comment_el = entry.find('arxiv:comment', ns)
            journal_ref_el = entry.find('arxiv:journal_ref', ns)
            
            comment = comment_el.text if comment_el is not None else ""
            journal_ref = journal_ref_el.text if journal_ref_el is not None else ""
            
            text_to_search = comment + " " + journal_ref
            match = re.search(top_venues, text_to_search, re.IGNORECASE)
            
            if match:
                venue = match.group(1).upper()
                pdf_link = ""
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf':
                        pdf_link = link.get('href')
                        
                papers.append({
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'venue': venue,
                    'pdf_link': pdf_link
                })
        
        for i, p in enumerate(papers[:10], 1):
            authors = ", ".join(p['authors'][:3]) + (" et al." if len(p['authors']) > 3 else "")
            print(f"| {p['title']} | {p['year']} | {p['venue']} | N/A | {'Yes' if p['pdf_link'] else 'No'} |")

    except Exception as e2:
        print(f"arXiv Error: {e2}")

