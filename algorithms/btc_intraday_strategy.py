"""
Enhanced BTC Intraday Trading Strategy
Based on the original BTCMVPAlgorithm with improved structure and configuration management
"""

from AlgorithmImports import *
from datetime import timedelta
from typing import Dict, Any, Optional
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from algorithms.base_algorithm import BaseAlgorithm

class BTCIntradayStrategy(BaseAlgorithm):
    """
    Enhanced BTC Intraday Trading Strategy
    
    Strategy Logic:
    - Entry: Price > EMA(20) AND RSI < 30 AND OBV increasing
    - Exit: Stop-loss (0.5%) OR Take-profit (1%) OR Time-based (30 min)
    - Uses 5-minute consolidated bars for BTC/USD
    """
    
    def Initialize(self):
        """Initialize the BTC intraday trading strategy"""
        # Call parent initialization
        super().Initialize()
        
        # Get trading configuration
        trading_config = self.algorithm_config.get('trading', {})
        indicators_config = self.algorithm_config.get('indicators', {})
        
        # Add BTC/USD cryptocurrency
        symbol = trading_config.get('symbol', 'BTCUSD')
        market = trading_config.get('market', 'Bitfinex')
        resolution = getattr(Resolution, trading_config.get('resolution', 'Minute'))
        
        self.btc_symbol = self.AddCrypto(symbol, resolution, market).Symbol
        
        # Setup 5-minute bar consolidation
        consolidation_minutes = trading_config.get('consolidation_minutes', 5)
        self.Consolidate(self.btc_symbol, timedelta(minutes=consolidation_minutes), self.OnFiveMinuteBar)
        
        # Initialize technical indicators
        self.setup_indicators(indicators_config)
        
        # Setup risk management parameters
        self.setup_risk_parameters()
        
        # Setup trading state variables
        self.setup_trading_state()
        
        # Set warmup period
        self.setup_warmup_period()
        
        self.logger.info(f"BTC Intraday Strategy initialized for {symbol} on {market}")
    
    def setup_indicators(self, indicators_config: Dict[str, Any]):
        """Setup technical indicators based on configuration"""
        
        # Exponential Moving Average (EMA)
        ema_config = indicators_config.get('ema', {})
        self.ema_period = ema_config.get('period', 20)
        self.ema = self.EMA(self.btc_symbol, self.ema_period, Resolution.Minute)
        
        # Relative Strength Index (RSI)
        rsi_config = indicators_config.get('rsi', {})
        self.rsi_period = rsi_config.get('period', 14)
        self.rsi_oversold = rsi_config.get('oversold', 30)
        self.rsi_overbought = rsi_config.get('overbought', 70)
        self.rsi = self.RSI(self.btc_symbol, self.rsi_period, MovingAverageType.Simple, Resolution.Minute)
        
        # On Balance Volume (OBV)
        obv_config = indicators_config.get('obv', {})
        if obv_config.get('enabled', True):
            self.obv = self.OBV(self.btc_symbol, Resolution.Minute)
        else:
            self.obv = None
        
        # Optional: Bollinger Bands (for future enhancement)
        bb_config = indicators_config.get('bollinger_bands', {})
        if bb_config.get('enabled', False):
            bb_period = bb_config.get('period', 20)
            bb_std = bb_config.get('std_dev', 2)
            self.bollinger_bands = self.BB(self.btc_symbol, bb_period, bb_std, MovingAverageType.Simple, Resolution.Minute)
        else:
            self.bollinger_bands = None
        
        # Optional: MACD (for future enhancement)
        macd_config = indicators_config.get('macd', {})
        if macd_config.get('enabled', False):
            fast_period = macd_config.get('fast_period', 12)
            slow_period = macd_config.get('slow_period', 26)
            signal_period = macd_config.get('signal_period', 9)
            self.macd = self.MACD(self.btc_symbol, fast_period, slow_period, signal_period, MovingAverageType.Exponential, Resolution.Minute)
        else:
            self.macd = None
    
    def setup_risk_parameters(self):
        """Setup risk management parameters from configuration"""
        exit_config = self.algorithm_config.get('exit', {})
        
        self.stop_loss_percent = exit_config.get('stop_loss_percent', 0.005)
        self.take_profit_percent = exit_config.get('take_profit_percent', 0.01)
        
        # Trading duration
        trading_config = self.algorithm_config.get('trading', {})
        trade_duration_minutes = trading_config.get('trade_duration_minutes', 30)
        self.trade_duration = timedelta(minutes=trade_duration_minutes)
        
        # Position sizing
        self.position_size = trading_config.get('position_size', 0.99)
    
    def setup_trading_state(self):
        """Initialize trading state variables"""
        self.last_obv_value = None
        self.entry_price = 0
        self.entry_time = None
        
        # Performance tracking
        self.signals_generated = 0
        self.trades_executed = 0
        self.winning_trades = 0
        self.losing_trades = 0
    
    def setup_warmup_period(self):
        """Setup warmup period for indicators"""
        behavior_config = self.algorithm_config.get('behavior', {})
        warmup_buffer = behavior_config.get('warmup_buffer', 1)
        
        # Calculate required warmup period
        max_indicator_period = max(self.ema_period, self.rsi_period)
        warmup_period = max_indicator_period + warmup_buffer
        
        self.SetWarmUp(warmup_period)
        
        self.logger.info(f"Warmup period set to {warmup_period} periods")
    
    def OnFiveMinuteBar(self, bar):
        """
        Handle 5-minute consolidated bar data
        Main trading logic implementation
        """
        # Skip if still warming up
        if self.IsWarmingUp:
            return
        
        # Ensure all indicators are ready
        if not self.are_indicators_ready():
            return
        
        # Check risk limits before trading
        if not self.check_risk_limits():
            self.logger.warning("Risk limits exceeded, skipping trading logic")
            return
        
        # Get current market data
        current_price = bar.Close
        current_time = self.Time
        
        # Update OBV tracking
        self.update_obv_tracking()
        
        # Generate trading signals
        entry_signal = self.generate_entry_signal(current_price)
        exit_signal = self.generate_exit_signal(current_price, current_time)
        
        # Execute trading logic
        if not self.Portfolio.Invested and entry_signal:
            self.execute_entry(current_price, current_time)
        elif self.Portfolio.Invested and exit_signal:
            self.execute_exit(current_price, current_time, exit_signal)
        
        # Log indicator values if enabled
        if self.algorithm_config.get('behavior', {}).get('log_indicators', False):
            self.log_indicator_values(current_price)
    
    def are_indicators_ready(self) -> bool:
        """Check if all required indicators are ready"""
        indicators_ready = self.ema.IsReady and self.rsi.IsReady
        
        if self.obv is not None:
            indicators_ready = indicators_ready and self.obv.IsReady
        
        return indicators_ready
    
    def update_obv_tracking(self):
        """Update OBV value tracking for trend detection"""
        if self.obv is not None:
            if self.last_obv_value is None:
                self.last_obv_value = self.obv.Current.Value
    
    def generate_entry_signal(self, current_price: float) -> bool:
        """
        Generate entry signal based on strategy conditions
        
        Entry Conditions:
        1. Price > EMA(20)
        2. RSI < oversold threshold (30)
        3. OBV is increasing (if enabled)
        """
        entry_config = self.algorithm_config.get('entry', {})
        conditions = entry_config.get('conditions', {})
        
        # Condition 1: Price above EMA
        price_above_ema = current_price > self.ema.Current.Value if conditions.get('price_above_ema', True) else True
        
        # Condition 2: RSI oversold
        rsi_oversold = self.rsi.Current.Value < self.rsi_oversold if conditions.get('rsi_oversold', True) else True
        
        # Condition 3: OBV increasing
        obv_increasing = True
        if conditions.get('obv_increasing', True) and self.obv is not None and self.last_obv_value is not None:
            obv_increasing = self.obv.Current.Value > self.last_obv_value
        
        # Generate signal
        entry_signal = price_above_ema and rsi_oversold and obv_increasing
        
        if entry_signal:
            self.signals_generated += 1
            
            # Log signal generation
            if self.algorithm_config.get('behavior', {}).get('log_signals', True):
                self.log_signal("ENTRY", str(self.btc_symbol), {
                    'price': current_price,
                    'ema': self.ema.Current.Value,
                    'rsi': self.rsi.Current.Value,
                    'obv': self.obv.Current.Value if self.obv else 'N/A',
                    'obv_increasing': obv_increasing
                })
        
        return entry_signal
    
    def generate_exit_signal(self, current_price: float, current_time) -> Optional[str]:
        """
        Generate exit signal based on strategy conditions
        
        Exit Conditions:
        1. Stop-loss hit
        2. Take-profit hit
        3. Time-based exit
        """
        if not self.Portfolio.Invested:
            return None
        
        # Stop-loss check
        if current_price <= self.entry_price * (1 - self.stop_loss_percent):
            return "STOP_LOSS"
        
        # Take-profit check
        if current_price >= self.entry_price * (1 + self.take_profit_percent):
            return "TAKE_PROFIT"
        
        # Time-based exit check
        if self.entry_time and (current_time - self.entry_time) >= self.trade_duration:
            return "TIME_EXIT"
        
        return None
    
    def execute_entry(self, current_price: float, current_time):
        """Execute entry order"""
        # Calculate position size
        position_size = self.calculate_position_size(str(self.btc_symbol), current_price)
        
        # Place order
        self.SetHoldings(self.btc_symbol, position_size)
        
        # Update trading state
        self.entry_price = current_price
        self.entry_time = current_time
        self.trades_executed += 1
        
        # Log trade execution
        if self.algorithm_config.get('behavior', {}).get('log_trades', True):
            self.log_trade("BUY", str(self.btc_symbol), position_size, current_price,
                          entry_time=current_time,
                          ema=self.ema.Current.Value,
                          rsi=self.rsi.Current.Value)
        
        self.logger.info(f"ENTRY executed at {current_price:.4f}")
    
    def execute_exit(self, current_price: float, current_time, exit_reason: str):
        """Execute exit order"""
        # Close position
        self.Liquidate(self.btc_symbol)
        
        # Calculate trade performance
        trade_pnl = (current_price - self.entry_price) / self.entry_price
        
        # Update performance tracking
        if trade_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
            self.consecutive_losses += 1
        
        # Log trade execution
        if self.algorithm_config.get('behavior', {}).get('log_trades', True):
            self.log_trade("SELL", str(self.btc_symbol), 0, current_price,
                          exit_reason=exit_reason,
                          entry_price=self.entry_price,
                          pnl_percent=trade_pnl * 100,
                          duration=(current_time - self.entry_time).total_seconds() / 60)
        
        # Reset trading state
        self.entry_price = 0
        self.entry_time = None
        
        self.logger.info(f"EXIT executed at {current_price:.4f} - Reason: {exit_reason}")
    
    def log_indicator_values(self, current_price: float):
        """Log current indicator values for debugging"""
        indicator_values = {
            'price': current_price,
            'ema': self.ema.Current.Value,
            'rsi': self.rsi.Current.Value
        }
        
        if self.obv is not None:
            indicator_values['obv'] = self.obv.Current.Value
        
        if self.bollinger_bands is not None:
            indicator_values.update({
                'bb_upper': self.bollinger_bands.UpperBand.Current.Value,
                'bb_middle': self.bollinger_bands.MiddleBand.Current.Value,
                'bb_lower': self.bollinger_bands.LowerBand.Current.Value
            })
        
        if self.macd is not None:
            indicator_values.update({
                'macd': self.macd.Current.Value,
                'macd_signal': self.macd.Signal.Current.Value,
                'macd_histogram': self.macd.Histogram.Current.Value
            })
        
        self.log_signal("INDICATORS", str(self.btc_symbol), indicator_values)
    
    def OnEndOfAlgorithm(self):
        """Called at the end of algorithm execution"""
        # Calculate final performance metrics
        total_trades = self.winning_trades + self.losing_trades
        win_rate = (self.winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        final_metrics = {
            'total_signals': self.signals_generated,
            'total_trades': total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate_percent': win_rate,
            'final_portfolio_value': self.Portfolio.TotalPortfolioValue,
            'max_drawdown_percent': self.max_drawdown * 100
        }
        
        self.log_performance(final_metrics)
        self.logger.info("BTC Intraday Strategy execution completed")
    
    def OnData(self, data):
        """Handle regular data updates (1-minute bars)"""
        # Update OBV tracking with each data point
        if self.obv is not None and not self.IsWarmingUp:
            self.last_obv_value = self.obv.Current.Value
