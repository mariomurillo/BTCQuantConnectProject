#!/usr/bin/env python3
"""
QuantConnect BTC Trading Algorithm Project
Main entry point for local testing and development

Author: Trading Algorithm Project
Date: 2025
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.config_manager import ConfigManager
from utils.logging_config import setup_logging
from algorithms.btc_intraday_strategy import BTCIntradayStrategy

def main():
    """Main entry point for local algorithm testing"""
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting BTC QuantConnect Algorithm Project")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        algorithm_config = config_manager.get_algorithm_config()
        
        logger.info(f"Loaded configuration: {algorithm_config}")
        logger.info("Algorithm ready for QuantConnect deployment")
        
        # Note: Actual algorithm execution happens in QuantConnect environment
        # This is for local testing and validation only
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
