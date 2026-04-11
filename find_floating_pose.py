import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re

# 根据“浮体”(floating body)，“非接触式位姿估计”(non-contact / markerless pose estimation)
queries = [
    'all:"pose estimation" AND all:"floating"',
    'all:"pose estimation" AND (all:"non-contact" OR all:contactless)',
    'all:"pose estimation" AND all:uncooperative',
    'all:"pose estimation" AND all:markerless',
    'all:"pose estimation" AND all:"water surface"',
    'all:"pose estimation" AND all:"marine"'
]

papers = {}
# 增加一些可能的相关顶会，包括自动化、机器人方向的 ICRA, IROS 和视觉方向
top_venues_regex = r'(CVPR|ICCV|ECCV|NeurIPS|ICLR|ICRA|IROS|Robotics and Automation|Computer Vision and Pattern Recognition)'

for q in queries:
    query_encoded = urllib.parse.quote(q)
    url = f"http://export.arxiv.org/api/query?search_query={query_encoded}&sortBy=submittedDate&sortOrder=descending&max_results=300"
    
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
            authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
            
            comment_el = entry.find('arxiv:comment', ns)
            journal_ref_el = entry.find('arxiv:journal_ref', ns)
            
            comment = comment_el.text if comment_el is not None else ""
            journal_ref = journal_ref_el.text if journal_ref_el is not None else ""
            
            text_to_search = comment + " " + journal_ref
            match = re.search(top_venues_regex, text_to_search, re.IGNORECASE)
            
            if match:
                v = match.group(1).upper()
                if "ROBOTICS AND AUTOMATION" in v: v = "ICRA"
                if "COMPUTER VISION AND PATTERN RECOGNITION" in v: v = "CVPR"
                
                pdf_link = ""
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf':
                        pdf_link = link.get('href')
                        
                papers[arxiv_id] = {
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'venue': v,
                    'pdf_link': pdf_link,
                    'time': published
                }
    except Exception as e:
        print(f"Error on query {q}: {e}")

s_papers = sorted(papers.values(), key=lambda x: x['time'], reverse=True)

print("FOUND:")
for i, p in enumerate(s_papers[:10], 1):
    print(f"| {p['title']} | {p['year']} | {p['venue']} | N/A | {'Yes' if p['pdf_link'] else 'No'} |")

