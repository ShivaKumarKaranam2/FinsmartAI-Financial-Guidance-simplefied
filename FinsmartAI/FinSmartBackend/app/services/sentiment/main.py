"""
Market News Engine - Main Entry Point
Command-line interface for running the sentiment analysis
"""

import argparse
import json
import sys
import logging
from typing import Optional

from .news_engine import MarketNewsEngine
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_analysis(
    api_key: Optional[str] = None,
    limit: int = 20,
    include_all_articles: bool = False,
    output_file: Optional[str] = None,
    symbols: Optional[str] = None,
    search: Optional[str] = None
) -> dict:
    """
    Run the complete market sentiment analysis
    
    Args:
        api_key: Marketaux API key (uses default if not provided)
        limit: Number of articles to fetch
        include_all_articles: Include all articles in output
        output_file: File path to save JSON output
        symbols: Filter by stock symbols (comma-separated)
        search: Search term for filtering articles
        
    Returns:
        Analysis result dictionary
    """
    # Initialize engine
    engine = MarketNewsEngine(api_key=api_key)
    
    # Build kwargs for API call
    kwargs = {}
    if symbols:
        kwargs['symbols'] = symbols
    if search:
        kwargs['search'] = search
    
    # Run analysis
    result = engine.run(
        limit=limit,
        include_all_articles=include_all_articles,
        **kwargs
    )
    
    # Output handling
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to: {output_file}")
    
    return result


def main():
    """Command-line interface entry point"""
    parser = argparse.ArgumentParser(
        description='Market News Engine - Indian Market Sentiment Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m market_sentiment
  python -m market_sentiment --limit 10
  python -m market_sentiment --symbols RELIANCE.NS,TCS.NS
  python -m market_sentiment --output results.json
        """
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Marketaux API key (optional, uses default if not provided)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Number of articles to fetch (default: 20)'
    )
    
    parser.add_argument(
        '--symbols',
        type=str,
        help='Filter by stock symbols (comma-separated, e.g., RELIANCE.NS,TCS.NS)'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        help='Search term for filtering articles'
    )
    
    parser.add_argument(
        '--include-all',
        action='store_true',
        help='Include all articles in the output'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path for JSON results'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        default=True,
        help='Pretty print JSON output (default: True)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress logging output'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    try:
        # Run analysis
        result = run_analysis(
            api_key=args.api_key,
            limit=args.limit,
            include_all_articles=args.include_all,
            output_file=args.output,
            symbols=args.symbols,
            search=args.search
        )
        
        # Print to stdout if no output file specified
        if not args.output:
            if args.pretty:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(result, ensure_ascii=False))
        
        # Return success
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        print(json.dumps({
            "error": True,
            "message": str(e)
        }, indent=2), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
