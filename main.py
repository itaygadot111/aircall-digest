#!/usr/bin/env python3
"""
AI Competitive Intelligence Agent for Aircall
Monitors competitors, industry news, and AI developments to create automated digests
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

from src.agent import CompetitiveIntelligenceAgent
from src.config import Config
from src.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description="AI Competitive Intelligence Agent")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--output", default="digest.html", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending notifications")
    parser.add_argument("--force", action="store_true", help="Force run even if recently executed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(verbose=args.verbose)
    
    try:
        # Load configuration
        config = Config.from_file(args.config)
        
        # Initialize agent
        agent = CompetitiveIntelligenceAgent(config, logger, verbose=args.verbose)
        
        # Check if we should run based on last execution time
        if not args.force and not agent.should_run():
            logger.info("Agent was recently executed. Use --force to override.")
            return
        
        # Run the agent
        logger.info("Starting competitive intelligence agent...")
        digest = asyncio.run(agent.run())
        
        # Save digest to file
        agent.save_digest(digest, args.output)
        
        # Send notifications if not dry run
        if not args.dry_run:
            agent.send_notifications(digest)
        
        logger.info(f"Agent completed successfully. Digest saved to {args.output}")
        
    except Exception as e:
        logger.error(f"Agent failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()