import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re

# Refined queries targeting "Floating Body / Spacecraft / AUV / Uncooperative Target" and "Non-contact / Vision-based / Markerless 6D Pose Estimation"
base_queries = [
    'all:"pose estimation" AND all:uncooperative',
    'all:"pose estimation" AND all:spacecraft',
    'all:"pose estimation" AND all:satellite',
    'all:"pose estimation" AND all:debris',
    'all:"pose estimation" AND all:AUV',
    'all:"pose estimation" AND all:USV',
    'all:"pose estimation" AND all:underwater',
    'all:"pose estimation" AND all:vessel',
    'all:"pose estimation" AND all:floating'
]

top_venues_regex = r'(CVPR|ICCV|ECCV|NeurIPS|ICLR|ICRA|IROS|Robotics and Automation|Computer Vision)'
papers = {}

for q in base_queries:
    query_encoded = urllib.parse.quote(q)
    url = f"http://export.arxiv.org/api/query?search_query={query_encoded}&sortBy=submittedDate&sortOrder=descending&max_results=100"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode('utf-8')
            
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        for entry in root.findall('atom:entry', ns):
            arxiv_id_el = entry.find('atom:id', ns)
            if arxiv_id_el is None: continue
            arxiv_id = arxiv_id_el.text
            if arxiv_id in papers: continue
            
            published_el = entry.find('atom:published', ns)
            if published_el is None: continue
            published = published_el.text
            year = int(published[:4])
            if year < 2023: continue
                
            title = entry.find('atom:title', ns).text.replace('\n', ' ').strip()
            summary = entry.find('atom:summary', ns).text.replace('\n', ' ').strip()
            authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
            
            comment_el = entry.find('arxiv:comment', ns)
            journal_ref_el = entry.find('arxiv:journal_ref', ns)
            comment = comment_el.text if comment_el is not None else ""
            journal_ref = journal_ref_el.text if journal_ref_el is not None else ""
            text_to_search = comment + " " + journal_ref
            
            match = re.search(top_venues_regex, text_to_search, re.IGNORECASE)
            if match:
                venue_matched = match.group(1).upper()
                if "ROBOTICS AND AUTOMATION" in venue_matched: venue_matched = "ICRA"
                if "COMPUTER VISION" in venue_matched: venue_matched = "CVPR/ICCV/ECCV" # approximation
                
                # Relevance scoring based on title and abstract keywords
                score = 0
                search_text = (title + " " + summary).lower()
                
                if any(x in search_text for x in ["uncooperative", "spacecraft", "satellite", "debris", "auv", "usv", "vessel", "floating"]): score += 10
                if any(x in search_text for x in ["non-contact", "contactless", "markerless", "vision", "camera", "lidar", "visual"]): score += 5
                if any(x in search_text for x in ["6d", "6-dof", "6dof"]): score += 5
                
                # Only keep papers that mention both the target type and the estimation method
                if score >= 15:
                    pdf_link = ""
                    for link in entry.findall('atom:link', ns):
                        if link.get('title') == 'pdf':
                            pdf_link = link.get('href')
                            
                    papers[arxiv_id] = {
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'venue': venue_matched,
                        'pdf_link': pdf_link,
                        'time': published,
                        'score': score
                    }
    except Exception as e:
        print(f"Error on query {q}: {e}")

# Sort primarily by score (relevance), secondarily by date
s_papers = sorted(papers.values(), key=lambda x: (x['score'], x['time']), reverse=True)

print("RANKED_PAPERS_START:")
for p in s_papers[:5]:
    print(f"| {p['title']} | {p['year']} | {p['venue']} | N/A | {'Yes' if p['pdf_link'] else 'No'} | Score: {p['score']} |")

