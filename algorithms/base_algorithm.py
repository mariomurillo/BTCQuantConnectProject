"""
Base Algorithm Class for QuantConnect Trading Algorithms
Provides common functionality and structure for all trading algorithms
"""

from AlgorithmImports import *
from datetime import timedelta
from typing import Dict, Any, Optional, List
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config_manager import ConfigManager
from utils.logging_config import AlgorithmLoggerMixin

class BaseAlgorithm(QCAlgorithm, AlgorithmLoggerMixin):
    """
    Base class for QuantConnect trading algorithms
    Provides common functionality, configuration management, and logging
    """
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.algorithm_config = {}
        self.risk_config = {}
        self.backtest_config = {}
        
        # Trading state
        self.positions = {}
        self.entry_prices = {}
        self.entry_times = {}
        self.trade_count = 0
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        
        # Performance tracking
        self.performance_metrics = {}
        self.trade_log = []
        
    def Initialize(self):
        """Initialize the algorithm - to be overridden by child classes"""
        # Load configurations
        self.load_configurations()
        
        # Set basic algorithm parameters
        self.setup_algorithm_parameters()
        
        # Initialize logging
        self.setup_logging()
        
        self.logger.info("Base algorithm initialized")
    
    def load_configurations(self):
        """Load all configuration files"""
        try:
            self.algorithm_config = self.config_manager.get_algorithm_config()
            self.risk_config = self.config_manager.get_risk_config()
            self.backtest_config = self.config_manager.get_backtest_config()
            
            self.logger.info("Configurations loaded successfully")
        except Exception as e:
            self.Debug(f"Error loading configurations: {str(e)}")
            # Use default configurations if loading fails
            self.algorithm_config = self.get_default_algorithm_config()
            self.risk_config = self.get_default_risk_config()
    
    def setup_algorithm_parameters(self):
        """Setup basic algorithm parameters from configuration"""
        # Environment settings
        env_config = self.algorithm_config.get('environment', {})
        
        if 'start_date' in env_config:
            start_date = env_config['start_date']
            if isinstance(start_date, str):
                year, month, day = map(int, start_date.split('-'))
                self.SetStartDate(year, month, day)
        
        if 'end_date' in env_config:
            end_date = env_config['end_date']
            if isinstance(end_date, str):
                year, month, day = map(int, end_date.split('-'))
                self.SetEndDate(year, month, day)
        
        if 'initial_cash' in env_config:
            self.SetCash(env_config['initial_cash'])
    
    def setup_logging(self):
        """Setup algorithm-specific logging"""
        behavior_config = self.algorithm_config.get('behavior', {})
        
        if behavior_config.get('debug_mode', False):
            self.SetDebugMode(True)
    
    def get_config_value(self, config_type: str, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to default"""
        return self.config_manager.get_config_value(config_type, key, default)
    
    def calculate_position_size(self, symbol: str, entry_price: float) -> float:
        """
        Calculate position size based on risk management rules
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the position
            
        Returns:
            Position size as percentage of portfolio
        """
        risk_config = self.risk_config.get('position_sizing', {})
        method = risk_config.get('method', 'fixed')
        
        if method == 'fixed':
            return risk_config.get('fixed', {}).get('size', 0.99)
        
        elif method == 'percent_risk':
            # Calculate position size based on risk per trade
            risk_per_trade = risk_config.get('percent_risk', {}).get('risk_per_trade', 0.02)
            stop_loss_percent = self.risk_config.get('stop_loss', {}).get('default_percent', 0.005)
            
            # Position size = (Risk per trade) / (Stop loss percentage)
            position_size = min(risk_per_trade / stop_loss_percent, 0.99)
            return position_size
        
        else:
            # Default to fixed size
            return 0.99
    
    def check_risk_limits(self) -> bool:
        """
        Check if current portfolio state violates risk limits
        
        Returns:
            True if within risk limits, False otherwise
        """
        portfolio_config = self.risk_config.get('portfolio', {})
        
        # Check maximum drawdown
        max_drawdown_limit = portfolio_config.get('max_drawdown_percent', 0.15)
        current_drawdown = self.calculate_current_drawdown()
        
        if current_drawdown > max_drawdown_limit:
            self.log_risk_event("MAX_DRAWDOWN_EXCEEDED", "", {
                "current_drawdown": current_drawdown,
                "limit": max_drawdown_limit
            })
            return False
        
        # Check daily loss limit
        daily_loss_limit = portfolio_config.get('daily_loss_limit_percent', 0.05)
        daily_loss_percent = abs(self.daily_pnl) / self.Portfolio.TotalPortfolioValue
        
        if daily_loss_percent > daily_loss_limit:
            self.log_risk_event("DAILY_LOSS_LIMIT_EXCEEDED", "", {
                "daily_loss_percent": daily_loss_percent,
                "limit": daily_loss_limit
            })
            return False
        
        return True
    
    def calculate_current_drawdown(self) -> float:
        """Calculate current portfolio drawdown"""
        if not hasattr(self, '_peak_portfolio_value'):
            self._peak_portfolio_value = self.Portfolio.TotalPortfolioValue
        
        current_value = self.Portfolio.TotalPortfolioValue
        self._peak_portfolio_value = max(self._peak_portfolio_value, current_value)
        
        if self._peak_portfolio_value > 0:
            drawdown = (self._peak_portfolio_value - current_value) / self._peak_portfolio_value
            self.max_drawdown = max(self.max_drawdown, drawdown)
            return drawdown
        
        return 0.0
    
    def log_trade_execution(self, action: str, symbol: str, quantity: float, price: float):
        """Log trade execution with performance tracking"""
        self.trade_count += 1
        
        trade_info = {
            'timestamp': self.Time,
            'action': action,
            'symbol': str(symbol),
            'quantity': quantity,
            'price': price,
            'portfolio_value': self.Portfolio.TotalPortfolioValue
        }
        
        self.trade_log.append(trade_info)
        
        self.log_trade(action, str(symbol), quantity, price,
                      trade_count=self.trade_count,
                      portfolio_value=self.Portfolio.TotalPortfolioValue)
    
    def update_performance_metrics(self):
        """Update performance tracking metrics"""
        current_value = self.Portfolio.TotalPortfolioValue
        
        self.performance_metrics.update({
            'portfolio_value': current_value,
            'total_trades': self.trade_count,
            'max_drawdown': self.max_drawdown,
            'consecutive_losses': self.consecutive_losses
        })
    
    def get_default_algorithm_config(self) -> Dict[str, Any]:
        """Default algorithm configuration if file loading fails"""
        return {
            'trading': {
                'symbol': 'BTCUSD',
                'market': 'Bitfinex',
                'resolution': 'Minute',
                'consolidation_minutes': 5,
                'position_size': 0.99,
                'trade_duration_minutes': 30
            },
            'indicators': {
                'ema': {'period': 20},
                'rsi': {'period': 14, 'oversold': 30},
                'obv': {'enabled': True}
            },
            'exit': {
                'stop_loss_percent': 0.005,
                'take_profit_percent': 0.01
            },
            'environment': {
                'start_date': '2023-01-01',
                'end_date': '2023-12-31',
                'initial_cash': 1000
            }
        }
    
    def get_default_risk_config(self) -> Dict[str, Any]:
        """Default risk configuration if file loading fails"""
        return {
            'portfolio': {
                'max_drawdown_percent': 0.15,
                'daily_loss_limit_percent': 0.05
            },
            'position_sizing': {
                'method': 'fixed',
                'fixed': {'size': 0.99}
            },
            'stop_loss': {
                'default_percent': 0.005
            }
        }
    
    def OnOrderEvent(self, orderEvent):
        """Handle order events with enhanced logging"""
        if orderEvent.Status == OrderStatus.Filled:
            self.log_trade_execution(
                "FILLED",
                orderEvent.Symbol,
                orderEvent.FillQuantity,
                orderEvent.FillPrice
            )
    
    def OnEndOfDay(self, symbol):
        """End of day processing"""
        self.update_performance_metrics()
        
        # Reset daily P&L tracking
        self.daily_pnl = 0.0
        
        # Log daily performance
        if self.algorithm_config.get('behavior', {}).get('log_performance', True):
            self.log_performance(self.performance_metrics)
