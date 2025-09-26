"""
Configuration management for Silan.

This module provides a centralized way to manage configuration settings
using YAML files. It supports environment variable substitution and
hierarchical configuration loading.
"""

from .loader import ConfigLoader, config

__all__ = ['ConfigLoader', 'config']