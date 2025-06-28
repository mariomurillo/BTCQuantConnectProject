# BTC QuantConnect Trading Algorithm Project

A comprehensive trading algorithm project for BTC/USD intraday trading on QuantConnect. This project provides a professional structure with enhanced risk management, configuration management, and performance analysis capabilities.

## Project Overview

This project implements an enhanced intraday trading strategy for BTC/USD using 5-minute bars. The core strategy is based on technical indicators (EMA, RSI, OBV) with comprehensive risk management controls.

### Core Strategy Logic
- **Entry Conditions**: Price above EMA(20) AND RSI < 30 (oversold) AND OBV increasing
- **Exit Conditions**: Stop-loss (0.5%) OR Take-profit (1%) OR Time-based exit (30 minutes)
- **Timeframe**: 5-minute consolidated bars
- **Asset**: BTC/USD (Bitfinex)

## Project Structure

```
BTCQuantConnectProject/
├── algorithms/                    # Trading algorithm implementations
│   ├── btc_intraday_strategy.py   # Main BTC intraday strategy
│   ├── base_algorithm.py          # Base class with common functionality
│   └── strategy_variants/         # Alternative strategy implementations
├── indicators/                    # Custom technical indicators
├── risk_management/               # Risk control and position sizing logic
├── backtesting/                   # Backtesting framework and analysis
│   └── optimization/              # Parameter optimization tools
├── data/                         # Data handling and validation
├── utils/                        # Utility functions and helpers
│   ├── config_manager.py         # Configuration management
│   └── logging_config.py         # Enhanced logging setup
├── config/                       # Configuration files
│   ├── algorithm_config.yaml     # Algorithm parameters
│   ├── backtest_config.yaml      # Backtesting settings
│   └── risk_config.yaml          # Risk management parameters
├── tests/                        # Unit and integration tests
├── notebooks/                    # Jupyter notebooks for analysis
├── requirements.txt              # Python dependencies
├── main.py                       # Entry point for local testing
└── README.md                    # Project documentation
```

## Key Features

### Trading Algorithm
- Modular strategy implementation
- Configuration-driven parameters
- Multiple indicator support (EMA, RSI, OBV, Bollinger Bands, MACD)
- Comprehensive entry/exit logic

### Risk Management
- Dynamic position sizing
- Stop-loss and take-profit controls
- Time-based position exits
- Portfolio-level risk limits
- Maximum drawdown protection
- Daily loss limits

### Configuration Management
- YAML-based configuration files
- Separate configs for algorithm, risk, and backtesting
- Easy parameter tuning without code changes

### Performance Tracking
- Detailed trade logging
- Performance metrics (win rate, P&L, drawdown)
- Signal generation tracking

## Getting Started

### Prerequisites
- QuantConnect account and setup
- Python 3.8+ for local development
- Dependencies listed in `requirements.txt`

### Installation
1. Clone this repository to your QuantConnect project directory
2. For local development, install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure parameters in the `config/` directory files

### Usage
1. Deploy `algorithms/btc_intraday_strategy.py` to QuantConnect
2. Run backtests using the platform
3. For local analysis, use the Jupyter notebooks in `notebooks/`

### Customization
- Modify parameters in `config/algorithm_config.yaml`
- Adjust risk controls in `config/risk_config.yaml`
- Configure backtesting in `config/backtest_config.yaml`

## Strategy Configuration

Key strategy parameters can be modified in `config/algorithm_config.yaml`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `trading.symbol` | Trading pair | BTCUSD |
| `trading.market` | Data source | Bitfinex |
| `trading.consolidation_minutes` | Bar timeframe | 5 minutes |
| `indicators.ema.period` | EMA period | 20 |
| `indicators.rsi.period` | RSI period | 14 |
| `indicators.rsi.oversold` | RSI oversold threshold | 30 |
| `exit.stop_loss_percent` | Stop loss | 0.5% |
| `exit.take_profit_percent` | Take profit | 1.0% |
| `trading.trade_duration_minutes` | Max trade duration | 30 minutes |

## Risk Management

Comprehensive risk controls are configured in `config/risk_config.yaml`:

| Control | Description | Default |
|---------|-------------|---------|
| Portfolio Limits | Maximum exposure and drawdown | 15% max drawdown |
| Position Sizing | Fixed or risk-based sizing | 2% risk per trade |
| Stop Loss | Default and volatility-based | 0.5% default |
| Emergency Controls | Circuit breakers and halts | 5% daily loss limit |

## Backtesting

Backtesting parameters are configured in `config/backtest_config.yaml` with comprehensive performance metrics and reporting options.

## Development

### Adding New Strategies
1. Create new strategy in `algorithms/strategy_variants/`
2. Inherit from `BaseAlgorithm`
3. Implement strategy logic

### Testing
- Unit tests are in `tests/`
- Run with: `pytest tests/`

## Contributing

Contributions are welcome! Please submit pull requests with new features or bug fixes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This trading algorithm is for educational and research purposes only. Trading cryptocurrency carries significant risk, and past performance in backtesting is not indicative of future results. Use at your own risk.
