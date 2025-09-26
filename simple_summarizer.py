#!/usr/bin/env python3
"""
Simple Website Summarizer
Quick analysis of any crawled website - no configuration needed.

Usage:
    python simple_summarizer.py <crawl_file.json>
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse
import re


def simple_analysis(crawl_file: str):
    """Perform a simple analysis of crawled website data"""
    
    # Load data
    pages = []
    try:
        with open(crawl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    pages.append(json.loads(line))
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    if not pages:
        print("No pages found in the file")
        return
    
    # Basic analysis
    domain = urlparse(pages[0]['url']).netloc
    total_pages = len(pages)
    total_words = sum(len(page.get('text', '').split()) for page in pages)
    
    # Find main pages
    homepage = None
    contact_page = None
    largest_page = max(pages, key=lambda p: len(p.get('text', '')))
    
    for page in pages:
        url = page['url'].lower()
        if url.endswith('/') or 'home' in url or 'index' in url:
            if not homepage or len(page.get('text', '')) > len(homepage.get('text', '')):
                homepage = page
        
        if 'contact' in url or 'contatti' in url:
            contact_page = page
    
    # Extract contact info
    all_text = ' '.join([p.get('text', '') for p in pages])
    
    # Find email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', all_text)
    email = email_match.group(0) if email_match else "Non trovata"
    
    # Find phone
    phone_match = re.search(r'(?:\+39|0)?\s?(?:\d{2,4})\s?(?:\d{6,8})', all_text)
    phone = phone_match.group(0).strip() if phone_match else "Non trovato"
    
    # Generate report
    print("=" * 60)
    print(f"ANALISI SEMPLICE SITO: {domain}")
    print("=" * 60)
    
    print(f"\n📊 STATISTICHE:")
    print(f"   • Pagine totali: {total_pages}")
    print(f"   • Parole totali: {total_words:,}")
    
    print(f"\n📞 CONTATTI:")
    print(f"   • Email: {email}")
    print(f"   • Telefono: {phone}")
    
    if homepage:
        print(f"\n🏠 HOMEPAGE:")
        # Extract first meaningful paragraph
        text = homepage.get('text', '')
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
        if paragraphs:
            print(f"   {paragraphs[0][:200]}...")
    
    print(f"\n📄 PAGINA PIÙ GRANDE:")
    print(f"   • {largest_page.get('title', 'Senza titolo')}")
    print(f"   • {len(largest_page.get('text', '').split())} parole")
    
    # Simple categorization
    page_types = {'Gallery': 0, 'Menu': 0, 'Contatti': 0, 'Altro': 0}
    
    for page in pages:
        url = page['url'].lower()
        if 'gallery' in url or 'foto' in url or 'images' in url:
            page_types['Gallery'] += 1
        elif 'menu' in url or 'carta' in url or 'servizi' in url:
            page_types['Menu'] += 1
        elif 'contact' in url or 'contatti' in url:
            page_types['Contatti'] += 1
        else:
            page_types['Altro'] += 1
    
    print(f"\n📋 TIPOLOGIE PAGINE:")
    for ptype, count in page_types.items():
        if count > 0:
            print(f"   • {ptype}: {count}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simple_summarizer.py <crawl_file.json>")
        sys.exit(1)
    
    crawl_file = sys.argv[1]
    if not Path(crawl_file).exists():
        print(f"File not found: {crawl_file}")
        sys.exit(1)
    
    simple_analysis(crawl_file)