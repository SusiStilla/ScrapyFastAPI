"""
Enhanced Website Summarizer with Configuration Support
Supports BART summarization and configurable website analysis
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from app.website_summarizer import WebsiteSummarizer, PageInfo, WebsiteAnalysis, ContentExtractor
import logging

logger = logging.getLogger(__name__)


class ConfigurableWebsiteSummarizer(WebsiteSummarizer):
    """Enhanced website summarizer with configuration support"""
    
    def __init__(self, config_path: str = None, use_ai_summary: bool = False, website_type: str = None):
        super().__init__(use_ai_summary)
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.website_type = website_type
        
        # Initialize BART summarizer if requested and available
        if use_ai_summary:
            self._init_bart_summarizer()
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'summarizer_config.yaml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using default settings.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'analysis': {
                'min_word_count': 10,
                'max_summary_length': 200,
                'min_summary_length': 50,
                'key_phrases_count': 10
            },
            'website_types': {
                'generic': {
                    'priority_pages': ['homepage', 'about', 'contact'],
                    'key_fields': ['name', 'description', 'contact_info']
                }
            }
        }
    
    def _init_bart_summarizer(self):
        """Initialize BART summarizer with proper error handling"""
        try:
            # Use MCP Hugging Face server if available
            if hasattr(self, '_use_mcp_summarization'):
                logger.info("Using MCP Hugging Face server for summarization")
                return
            
            # Fallback to local transformers
            from transformers import pipeline
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            logger.info("BART summarizer loaded successfully")
            
        except ImportError:
            logger.warning("transformers library not available")
            self.use_ai_summary = False
        except Exception as e:
            logger.error(f"Failed to initialize BART: {e}")
            self.use_ai_summary = False
    
    def classify_page_type(self, url: str, title: str, text: str) -> str:
        """Enhanced page classification using configuration"""
        if 'page_classification' not in self.config:
            return super().classify_page_type(url, title, text)
        
        url_lower = url.lower()
        title_lower = title.lower()
        text_lower = text.lower()
        
        classification_rules = self.config['page_classification']
        
        for page_type, rules in classification_rules.items():
            # Check URL patterns
            if 'url_patterns' in rules:
                if any(pattern in url_lower for pattern in rules['url_patterns']):
                    return page_type
            
            # Check title patterns
            if 'title_patterns' in rules:
                if any(pattern in title_lower for pattern in rules['title_patterns']):
                    return page_type
            
            # Check content patterns
            if 'content_patterns' in rules:
                if any(pattern in text_lower for pattern in rules['content_patterns']):
                    return page_type
        
        return 'content'
    
    def extract_website_specific_info(self, pages: List[PageInfo]) -> Dict[str, Any]:
        """Extract information specific to website type"""
        if not self.website_type or self.website_type not in self.config.get('website_types', {}):
            return {}
        
        website_config = self.config['website_types'][self.website_type]
        extracted_info = {}
        
        # Combine all text for pattern matching
        all_text = " ".join([p.text for p in pages])
        
        # Extract key fields based on configuration
        for field in website_config.get('key_fields', []):
            if field in website_config.get('content_patterns', {}):
                patterns = website_config['content_patterns'][field]
                for pattern in patterns:
                    import re
                    matches = re.findall(pattern, all_text, re.IGNORECASE)
                    if matches:
                        extracted_info[field] = matches[:3]  # Limit to first 3 matches
                        break
        
        return extracted_info
    
    def generate_enhanced_summary(self, text: str, context: str = "") -> str:
        """Generate summary with optional context"""
        if not text.strip():
            return "No content to summarize"
        
        # Prepare input for summarization
        input_text = text
        if context:
            input_text = f"Context: {context}\n\nContent: {text}"
        
        if self.use_ai_summary and self.summarizer:
            try:
                # Use MCP HF server if available
                summary = self._summarize_with_mcp(input_text)
                if summary:
                    return summary
                
                # Fallback to local BART
                return self._summarize_with_bart(input_text)
                
            except Exception as e:
                logger.warning(f"AI summarization failed: {e}")
        
        # Fallback to extractive summary
        return self._extractive_summary(text)
    
    def _summarize_with_mcp(self, text: str) -> Optional[str]:
        """Summarize using MCP Hugging Face server"""
        # This would integrate with the MCP HF server
        # For now, return None to fallback to local BART
        return None
    
    def _summarize_with_bart(self, text: str) -> str:
        """Summarize using local BART model"""
        max_length = self.config['analysis'].get('max_summary_length', 200)
        min_length = self.config['analysis'].get('min_summary_length', 50)
        
        # Truncate if too long for BART
        if len(text) > 1024:
            text = text[:1024]
        
        summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    
    def _extractive_summary(self, text: str) -> str:
        """Create extractive summary as fallback"""
        sentences = text.split('. ')
        if len(sentences) <= 3:
            return text
        
        # Return first few sentences as summary
        return '. '.join(sentences[:3]) + '.'
    
    def analyze_website(self, pages: List[PageInfo]) -> WebsiteAnalysis:
        """Enhanced website analysis with configuration support"""
        analysis = super().analyze_website(pages)
        
        if not analysis:
            return None
        
        # Add website-specific information
        specific_info = self.extract_website_specific_info(pages)
        analysis.key_information.update({'website_specific': specific_info})
        
        # Enhanced content summary with context
        context = f"Website type: {self.website_type or 'generic'}, Domain: {analysis.domain}"
        if analysis.main_content:
            analysis.content_summary = self.generate_enhanced_summary(
                analysis.main_content, context
            )
        
        return analysis
    
    def generate_enhanced_report(self, analysis: WebsiteAnalysis) -> str:
        """Generate enhanced report with website-specific information"""
        report = super().generate_report(analysis)
        
        # Add website-specific information if available
        specific_info = analysis.key_information.get('website_specific', {})
        if specific_info:
            additional_info = ["\n🎯 INFORMAZIONI SPECIFICHE:"]
            for field, values in specific_info.items():
                if isinstance(values, list):
                    additional_info.append(f"   • {field.replace('_', ' ').title()}: {', '.join(values)}")
                else:
                    additional_info.append(f"   • {field.replace('_', ' ').title()}: {values}")
            
            # Insert before the final separator
            report = report.replace("\n" + "=" * 80, "\n".join(additional_info) + "\n" + "=" * 80)
        
        return report


def create_summarizer(website_type: str = None, use_ai: bool = True, config_path: str = None) -> ConfigurableWebsiteSummarizer:
    """Factory function to create configured summarizer"""
    return ConfigurableWebsiteSummarizer(
        config_path=config_path,
        use_ai_summary=use_ai,
        website_type=website_type
    )


def analyze_crawl_file(file_path: str, website_type: str = None, output_path: str = None) -> str:
    """Analyze a crawl file and return the report"""
    
    # Create summarizer
    summarizer = create_summarizer(website_type=website_type, use_ai=True)
    
    # Load and analyze
    pages = summarizer.load_crawl_data(file_path)
    if not pages:
        return "No pages found to analyze"
    
    analysis = summarizer.analyze_website(pages)
    
    # Generate report
    report = summarizer.generate_enhanced_report(analysis)
    
    # Save analysis if output path provided
    if output_path:
        summarizer.save_analysis(analysis, output_path)
    
    return report


if __name__ == "__main__":
    # Example usage
    import sys
    
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'data/acquapazza_crawl.json'
    website_type = sys.argv[2] if len(sys.argv) > 2 else 'restaurant'
    
    report = analyze_crawl_file(file_path, website_type)
    print(report)