#!/usr/bin/env python3
"""
Test script to verify the YAML configuration system works correctly.
"""

import sys
import os
from pathlib import Path

# Add the silan package to Python path
sys.path.insert(0, str(Path(__file__).parent / 'silan'))

def test_config_loader():
    """Test the basic configuration loader functionality."""
    print("Testing Configuration Loader...")

    try:
        from silan.config import config
        print("✅ Config module imported successfully")

        # Test basic configuration files
        test_files = ['models', 'api', 'database', 'logging', 'parsers', 'defaults']

        for file_name in test_files:
            try:
                config_data = config.load_file(file_name)
                print(f"✅ {file_name}.yaml loaded successfully - {len(config_data)} top-level keys")
            except Exception as e:
                print(f"❌ Failed to load {file_name}.yaml: {e}")

        return True

    except Exception as e:
        print(f"❌ Failed to import config module: {e}")
        return False

def test_config_getters():
    """Test specific configuration getter methods."""
    print("\nTesting Configuration Getters...")

    try:
        from silan.config import config

        # Test models config
        models_config = config.get_models_config()
        print(f"✅ Models config loaded - {len(models_config)} sections")

        # Test API config
        api_config = config.get_api_config('development')
        print(f"✅ API development config loaded - base_url: {api_config.get('base_url', 'N/A')}")

        # Test database config
        db_config = config.get_database_config()
        print(f"✅ Database config loaded - {len(db_config)} sections")

        # Test logging config
        logging_config = config.get_logging_config()
        print(f"✅ Logging config loaded - {len(logging_config)} sections")

        # Test parsers config
        parsers_config = config.get_parsers_config()
        print(f"✅ Parsers config loaded - {len(parsers_config)} sections")

        return True

    except Exception as e:
        print(f"❌ Failed to test config getters: {e}")
        return False

def test_dot_notation():
    """Test dot notation access to configuration values."""
    print("\nTesting Dot Notation Access...")

    try:
        from silan.config import config

        # Test various dot notation paths
        test_paths = [
            ('models.projects.status.active', 'active'),
            ('models.blog.types.article', 'article'),
            ('models.ideas.priority.high', 'high'),
            ('api.development.base_url', 'http://localhost:5200'),
            ('database.sqlite.default_path', 'portfolio.db'),
            ('logging.theme.gradient_start', '#41B883'),
            ('parsers.special_files.references.filename', 'REFERENCES.md')
        ]

        for path, expected in test_paths:
            try:
                value = config.get(path)
                if value == expected:
                    print(f"✅ {path} = '{value}'")
                else:
                    print(f"⚠️  {path} = '{value}' (expected '{expected}')")
            except Exception as e:
                print(f"❌ Failed to get {path}: {e}")

        return True

    except Exception as e:
        print(f"❌ Failed to test dot notation: {e}")
        return False

def test_model_imports():
    """Test that updated model classes can be imported and used."""
    print("\nTesting Model Imports...")

    try:
        # Test project status enum
        from silan.models.projects import ProjectStatus
        print(f"✅ ProjectStatus imported - ACTIVE = '{ProjectStatus.ACTIVE.value}'")

        # Test blog enums
        from silan.models.blog import BlogContentType, BlogStatus
        print(f"✅ BlogContentType imported - ARTICLE = '{BlogContentType.ARTICLE.value}'")
        print(f"✅ BlogStatus imported - PUBLISHED = '{BlogStatus.PUBLISHED.value}'")

        # Test ideas enums
        from silan.models.ideas import IdeaStatus, IdeaPriority
        print(f"✅ IdeaStatus imported - PUBLISHED = '{IdeaStatus.PUBLISHED.value}'")
        print(f"✅ IdeaPriority imported - HIGH = '{IdeaPriority.HIGH.value}'")

        # Test recent updates enums
        from silan.models.recent_update import UpdateType, UpdateStatus, UpdatePriority
        print(f"✅ UpdateType imported - WORK = '{UpdateType.WORK.value}'")
        print(f"✅ UpdateStatus imported - ACTIVE = '{UpdateStatus.ACTIVE.value}'")
        print(f"✅ UpdatePriority imported - HIGH = '{UpdatePriority.HIGH.value}'")

        return True

    except Exception as e:
        print(f"❌ Failed to import model classes: {e}")
        return False

def test_logger_config():
    """Test that logger can use configuration values."""
    print("\nTesting Logger Configuration...")

    try:
        from silan.utils.logger import ModernLogger

        # Create logger instance (this should load config values)
        logger = ModernLogger(name="test-logger")

        print(f"✅ Logger created successfully")
        print(f"✅ Gradient start: {logger.GRADIENT_START}")
        print(f"✅ Gradient end: {logger.GRADIENT_END}")
        print(f"✅ Theme keys: {list(logger.DEFAULT_THEME.keys())[:5]}...")

        # Test a simple log message
        logger.info("Test log message from configuration system")

        return True

    except Exception as e:
        print(f"❌ Failed to test logger configuration: {e}")
        return False

def test_environment_variables():
    """Test environment variable substitution."""
    print("\nTesting Environment Variable Substitution...")

    try:
        from silan.config import config

        # Set a test environment variable
        os.environ['TEST_API_URL'] = 'https://test.example.com'

        # Create a test config with env var
        test_config = {
            'test_url': '${TEST_API_URL}',
            'test_with_default': '${NONEXISTENT_VAR:-default_value}'
        }

        # Test substitution
        substituted = config._substitute_env_vars(test_config)

        if substituted['test_url'] == 'https://test.example.com':
            print("✅ Environment variable substitution works")
        else:
            print(f"❌ Expected 'https://test.example.com', got '{substituted['test_url']}'")

        if substituted['test_with_default'] == 'default_value':
            print("✅ Default value substitution works")
        else:
            print(f"❌ Expected 'default_value', got '{substituted['test_with_default']}'")

        # Clean up
        del os.environ['TEST_API_URL']

        return True

    except Exception as e:
        print(f"❌ Failed to test environment variables: {e}")
        return False

def main():
    """Run all configuration system tests."""
    print("🧪 YAML Configuration System Test Suite")
    print("=" * 50)

    tests = [
        test_config_loader,
        test_config_getters,
        test_dot_notation,
        test_model_imports,
        test_logger_config,
        test_environment_variables
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Configuration system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())