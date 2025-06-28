"""
Logging Configuration for QuantConnect BTC Trading Algorithm
Provides enhanced logging setup with colors and proper formatting
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import colorlog

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_colors: bool = True
) -> logging.Logger:
    """
    Setup logging configuration for the trading algorithm
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, logs only to console.
        enable_colors: Whether to enable colored console output
    
    Returns:
        Configured logger instance
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    if enable_colors:
        # Colored formatter for console
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    else:
        # Standard formatter for console
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        
        # File formatter (no colors)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_algorithm_logger(name: str = "BTCAlgorithm") -> logging.Logger:
    """
    Get a logger instance for the algorithm
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class AlgorithmLoggerMixin:
    """Mixin class to add logging capabilities to algorithm classes"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_algorithm_logger(self.__class__.__name__)
    
    def log_trade(self, action: str, symbol: str, quantity: float, price: float, **kwargs):
        """Log trading actions with structured format"""
        extra_info = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
        message = f"TRADE - {action} | Symbol: {symbol} | Qty: {quantity} | Price: {price:.4f}"
        if extra_info:
            message += f" | {extra_info}"
        self.logger.info(message)
    
    def log_signal(self, signal_type: str, symbol: str, indicators: dict, **kwargs):
        """Log trading signals with indicator values"""
        indicator_info = " | ".join([f"{k}: {v:.4f}" if isinstance(v, (int, float)) else f"{k}: {v}" 
                                   for k, v in indicators.items()])
        extra_info = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
        
        message = f"SIGNAL - {signal_type} | Symbol: {symbol} | {indicator_info}"
        if extra_info:
            message += f" | {extra_info}"
        self.logger.info(message)
    
    def log_risk_event(self, event_type: str, symbol: str, details: dict):
        """Log risk management events"""
        details_info = " | ".join([f"{k}: {v}" for k, v in details.items()])
        message = f"RISK - {event_type} | Symbol: {symbol} | {details_info}"
        self.logger.warning(message)
    
    def log_performance(self, metrics: dict):
        """Log performance metrics"""
        metrics_info = " | ".join([f"{k}: {v}" for k, v in metrics.items()])
        message = f"PERFORMANCE | {metrics_info}"
        self.logger.info(message)
