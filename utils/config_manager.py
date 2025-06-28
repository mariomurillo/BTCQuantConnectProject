"""
Configuration Manager for QuantConnect BTC Trading Algorithm
Handles loading and managing configuration from YAML files
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration loading and access for the trading algorithm"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager
        
        Args:
            config_dir: Path to configuration directory. If None, uses default.
        """
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
        
        self._algorithm_config = None
        self._backtest_config = None
        self._risk_config = None
    
    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file"""
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            logger.warning(f"Configuration file {file_path} not found. Using defaults.")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Loaded configuration from {file_path}")
                return config or {}
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {str(e)}")
            return {}
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        """Get algorithm configuration"""
        if self._algorithm_config is None:
            self._algorithm_config = self._load_yaml_file("algorithm_config.yaml")
        return self._algorithm_config
    
    def get_backtest_config(self) -> Dict[str, Any]:
        """Get backtesting configuration"""
        if self._backtest_config is None:
            self._backtest_config = self._load_yaml_file("backtest_config.yaml")
        return self._backtest_config
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        if self._risk_config is None:
            self._risk_config = self._load_yaml_file("risk_config.yaml")
        return self._risk_config
    
    def get_config_value(self, config_type: str, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value
        
        Args:
            config_type: Type of config ('algorithm', 'backtest', 'risk')
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        config_map = {
            'algorithm': self.get_algorithm_config,
            'backtest': self.get_backtest_config,
            'risk': self.get_risk_config
        }
        
        if config_type not in config_map:
            logger.error(f"Unknown config type: {config_type}")
            return default
        
        config = config_map[config_type]()
        
        # Support dot notation for nested keys
        keys = key.split('.')
        value = config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Configuration key '{key}' not found in {config_type} config")
            return default
    
    def reload_configs(self):
        """Reload all configuration files"""
        self._algorithm_config = None
        self._backtest_config = None
        self._risk_config = None
        logger.info("Configuration files reloaded")
