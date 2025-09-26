#!/usr/bin/env python3
"""
Website Analysis Tool
Generic script to analyze and summarize any crawled website data.

Usage:
    python analyze_website.py <crawl_file> [website_type] [options]

Examples:
    python analyze_website.py data/acquapazza_crawl.json restaurant
    python analyze_website.py data/company_crawl.json corporate --output reports/analysis.json
    python analyze_website.py data/shop_crawl.json ecommerce --no-ai
"""

import argparse
import sys
import os
from pathlib import Path

# Add the app directory to path
sys.path.append(str(Path(__file__).parent))

from app.enhanced_summarizer import analyze_crawl_file, create_summarizer


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and summarize crawled website data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Website Types:
  restaurant    - Restaurants, pizzerias, cafes
  ecommerce     - Online shops, retail websites
  corporate     - Company websites, services
  portfolio     - Personal portfolios, creative sites
  generic       - Any other type of website

Examples:
  %(prog)s data/restaurant.json restaurant
  %(prog)s data/company.json corporate --output analysis.json
  %(prog)s data/site.json --no-ai --verbose
        """
    )
    
    parser.add_argument(
        'crawl_file',
        help='Path to the JSON crawl file'
    )
    
    parser.add_argument(
        'website_type',
        nargs='?',
        default='generic',
        choices=['restaurant', 'ecommerce', 'corporate', 'portfolio', 'generic'],
        help='Type of website (default: generic)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for JSON analysis'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI summarization (faster, simpler summaries)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'both'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    import logging
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    
    # Check if crawl file exists
    if not os.path.exists(args.crawl_file):
        print(f"Error: Crawl file not found: {args.crawl_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create summarizer
        summarizer = create_summarizer(
            website_type=args.website_type,
            use_ai=not args.no_ai,
            config_path=args.config
        )
        
        if args.verbose:
            print(f"Analyzing: {args.crawl_file}")
            print(f"Website type: {args.website_type}")
            print(f"AI summarization: {'enabled' if not args.no_ai else 'disabled'}")
            print("-" * 50)
        
        # Load and analyze
        pages = summarizer.load_crawl_data(args.crawl_file)
        if not pages:
            print("No pages found to analyze", file=sys.stderr)
            sys.exit(1)
        
        analysis = summarizer.analyze_website(pages)
        
        # Generate outputs based on format
        if args.format in ['text', 'both']:
            report = summarizer.generate_enhanced_report(analysis)
            print(report)
        
        if args.format in ['json', 'both']:
            output_file = args.output or f"{Path(args.crawl_file).stem}_analysis.json"
            summarizer.save_analysis(analysis, output_file)
            
            if args.format == 'json':
                print(f"Analysis saved to: {output_file}")
        
        # Save additional output file if specified
        if args.output and args.format != 'json':
            summarizer.save_analysis(analysis, args.output)
            if args.verbose:
                print(f"Analysis also saved to: {args.output}")
    
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def quick_analyze(crawl_file: str, website_type: str = 'generic') -> None:
    """Quick analysis function for interactive use"""
    try:
        report = analyze_crawl_file(crawl_file, website_type)
        print(report)
    except Exception as e:
        print(f"Analysis failed: {e}")


if __name__ == "__main__":
    main()