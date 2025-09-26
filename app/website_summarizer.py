"""
Generic Website Summarizer
A flexible tool for analyzing and summarizing crawled website data from any domain.
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PageInfo:
    """Information about a single page"""
    url: str
    title: str
    text: str
    content_type: str
    status: int
    fetched_at: str
    word_count: int = 0
    page_type: str = "unknown"
    
    def __post_init__(self):
        self.word_count = len(self.text.split()) if self.text else 0


@dataclass
class WebsiteAnalysis:
    """Complete analysis of a website"""
    domain: str
    total_pages: int
    page_types: Dict[str, int]
    main_content: str
    key_information: Dict[str, Any]
    contact_info: Dict[str, str]
    navigation_structure: List[str]
    content_summary: str = ""


class ContentExtractor:
    """Extracts structured information from page content"""
    
    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, str]:
        """Extract contact information from text"""
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone extraction (various formats)
        phone_patterns = [
            r'\b(?:\+39|0039)?\s?(?:\d{2,4})\s?(?:\d{6,8})\b',  # Italian format
            r'\b(?:\+\d{1,3})?\s?\(?(?:\d{3})\)?\s?(?:\d{3})\s?(?:\d{4})\b',  # International
            r'\b\d{3}[\.-]?\d{3}[\.-]?\d{4}\b'  # US format
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0].strip()
                break
        
        # Address extraction (basic)
        address_keywords = ['via', 'corso', 'piazza', 'viale', 'strada', 'street', 'avenue', 'road']
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in address_keywords):
                if len(line.strip()) < 100:  # Reasonable address length
                    contact_info['address'] = line.strip()
                    break
        
        return contact_info
    
    @staticmethod
    def classify_page_type(url: str, title: str, text: str) -> str:
        """Classify the type of page based on URL, title, and content"""
        url_lower = url.lower()
        title_lower = title.lower()
        text_lower = text.lower()
        
        # Check URL patterns first
        if any(pattern in url_lower for pattern in ['home', 'index', '/', 'homepage']):
            if url_lower.endswith('/') or 'index' in url_lower or 'home' in url_lower:
                return 'homepage'
        
        if any(pattern in url_lower for pattern in ['about', 'chi-siamo', 'about-us', 'storia']):
            return 'about'
        
        if any(pattern in url_lower for pattern in ['contact', 'contatti', 'contatto']):
            return 'contact'
        
        if any(pattern in url_lower for pattern in ['menu', 'carta', 'servizi', 'products']):
            return 'menu/services'
        
        if any(pattern in url_lower for pattern in ['gallery', 'galleria', 'foto', 'images']):
            return 'gallery'
        
        if any(pattern in url_lower for pattern in ['news', 'blog', 'articoli', 'notizie']):
            return 'news/blog'
        
        if any(pattern in url_lower for pattern in ['privacy', 'cookie', 'terms', 'legal']):
            return 'legal'
        
        # Check title and content patterns
        if any(keyword in title_lower for keyword in ['home', 'benvenuti', 'welcome']):
            return 'homepage'
        
        if any(keyword in title_lower + ' ' + text_lower for keyword in ['about', 'storia', 'chi siamo']):
            return 'about'
        
        return 'content'
    
    @staticmethod
    def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word not in ['questo', 'quella', 'essere', 'avere', 'fare', 'dire', 'andare', 'potere', 'dovere', 'volere']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_phrases]]


class WebsiteSummarizer:
    """Main class for analyzing and summarizing website crawl data"""
    
    def __init__(self, use_ai_summary: bool = False):
        self.use_ai_summary = use_ai_summary
        self.summarizer = None
        
        if use_ai_summary:
            try:
                from transformers import pipeline
                self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
                logger.info("BART summarizer loaded successfully")
            except ImportError:
                logger.warning("transformers not available, falling back to extractive summary")
                self.use_ai_summary = False
    
    def load_crawl_data(self, file_path: str) -> List[PageInfo]:
        """Load crawl data from JSON file"""
        pages = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        page = PageInfo(
                            url=data.get('url', ''),
                            title=data.get('title', ''),
                            text=data.get('text', ''),
                            content_type=data.get('content_type', ''),
                            status=data.get('status', 0),
                            fetched_at=data.get('fetched_at', '')
                        )
                        
                        # Classify page type
                        page.page_type = ContentExtractor.classify_page_type(
                            page.url, page.title, page.text
                        )
                        
                        pages.append(page)
                        
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON on line {line_num}")
                        continue
                        
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return []
        
        logger.info(f"Loaded {len(pages)} pages from {file_path}")
        return pages
    
    def analyze_website(self, pages: List[PageInfo]) -> WebsiteAnalysis:
        """Perform complete analysis of website pages"""
        if not pages:
            return None
        
        # Extract domain
        domain = urlparse(pages[0].url).netloc
        
        # Count page types
        page_types = {}
        for page in pages:
            page_types[page.page_type] = page_types.get(page.page_type, 0) + 1
        
        # Find homepage and main content
        homepage = next((p for p in pages if p.page_type == 'homepage'), None)
        about_page = next((p for p in pages if p.page_type == 'about'), None)
        
        main_content = ""
        if homepage:
            main_content += f"HOMEPAGE: {homepage.text}\n\n"
        if about_page:
            main_content += f"ABOUT: {about_page.text}\n\n"
        
        # Extract contact information
        all_text = " ".join([p.text for p in pages])
        contact_info = ContentExtractor.extract_contact_info(all_text)
        
        # Extract navigation structure
        navigation = list(set([p.page_type for p in pages if p.page_type != 'unknown']))
        
        # Extract key information
        key_info = {
            'total_words': sum(p.word_count for p in pages),
            'largest_page': max(pages, key=lambda p: p.word_count),
            'last_updated': max(pages, key=lambda p: p.fetched_at).fetched_at,
            'successful_pages': len([p for p in pages if p.status == 200]),
            'key_phrases': ContentExtractor.extract_key_phrases(all_text)
        }
        
        # Generate content summary
        content_summary = self._generate_summary(main_content) if main_content else "No main content found"
        
        return WebsiteAnalysis(
            domain=domain,
            total_pages=len(pages),
            page_types=page_types,
            main_content=main_content[:1000] + "..." if len(main_content) > 1000 else main_content,
            key_information=key_info,
            contact_info=contact_info,
            navigation_structure=navigation,
            content_summary=content_summary
        )
    
    def _generate_summary(self, text: str) -> str:
        """Generate summary using AI or extractive methods"""
        if not text.strip():
            return "No content to summarize"
        
        if self.use_ai_summary and self.summarizer and len(text) > 100:
            try:
                # Truncate if too long for BART
                max_length = 1024
                if len(text) > max_length:
                    text = text[:max_length]
                
                summary = self.summarizer(text, max_length=150, min_length=30, do_sample=False)
                return summary[0]['summary_text']
            except Exception as e:
                logger.warning(f"AI summarization failed: {e}")
        
        # Fallback to extractive summary
        sentences = text.split('. ')
        if len(sentences) <= 3:
            return text
        
        # Return first few sentences as summary
        return '. '.join(sentences[:3]) + '.'
    
    def generate_report(self, analysis: WebsiteAnalysis) -> str:
        """Generate a human-readable report"""
        report = []
        report.append("=" * 80)
        report.append(f"ANALISI SITO WEB: {analysis.domain}")
        report.append("=" * 80)
        
        report.append(f"\n📊 STATISTICHE GENERALI:")
        report.append(f"   • Pagine totali: {analysis.total_pages}")
        report.append(f"   • Pagine analizzate con successo: {analysis.key_information['successful_pages']}")
        report.append(f"   • Parole totali: {analysis.key_information['total_words']:,}")
        report.append(f"   • Ultimo aggiornamento: {analysis.key_information['last_updated']}")
        
        report.append(f"\n📄 TIPOLOGIE DI PAGINE:")
        for page_type, count in sorted(analysis.page_types.items()):
            report.append(f"   • {page_type.title()}: {count} pagine")
        
        if analysis.contact_info:
            report.append(f"\n📞 INFORMAZIONI DI CONTATTO:")
            for key, value in analysis.contact_info.items():
                report.append(f"   • {key.title()}: {value}")
        
        report.append(f"\n🧭 STRUTTURA NAVIGAZIONE:")
        report.append(f"   {' → '.join(analysis.navigation_structure)}")
        
        if analysis.key_information.get('key_phrases'):
            report.append(f"\n🔑 PAROLE CHIAVE PRINCIPALI:")
            phrases = analysis.key_information['key_phrases'][:8]
            report.append(f"   {', '.join(phrases)}")
        
        report.append(f"\n📝 RIASSUNTO CONTENUTO:")
        report.append(f"   {analysis.content_summary}")
        
        report.append(f"\n📈 PAGINA PIÙ ESTESA:")
        largest = analysis.key_information['largest_page']
        report.append(f"   • {largest.title} ({largest.word_count} parole)")
        report.append(f"   • URL: {largest.url}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def save_analysis(self, analysis: WebsiteAnalysis, output_file: str):
        """Save analysis to JSON file"""
        analysis_dict = {
            'domain': analysis.domain,
            'total_pages': analysis.total_pages,
            'page_types': analysis.page_types,
            'contact_info': analysis.contact_info,
            'navigation_structure': analysis.navigation_structure,
            'content_summary': analysis.content_summary,
            'key_information': {
                k: v for k, v in analysis.key_information.items() 
                if k != 'largest_page'  # Skip non-serializable object
            },
            'analysis_date': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis saved to {output_file}")


def main():
    """Example usage"""
    # Initialize summarizer
    summarizer = WebsiteSummarizer(use_ai_summary=True)
    
    # Load and analyze crawl data
    pages = summarizer.load_crawl_data('data/acquapazza_crawl.json')
    
    if pages:
        analysis = summarizer.analyze_website(pages)
        
        # Generate and print report
        report = summarizer.generate_report(analysis)
        print(report)
        
        # Save analysis
        summarizer.save_analysis(analysis, 'data/website_analysis.json')
    else:
        print("No pages found to analyze")


if __name__ == "__main__":
    main()