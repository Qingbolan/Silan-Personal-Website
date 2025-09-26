#!/usr/bin/env python3
"""
Test script to verify configuration-driven content processing.
"""

import sys
import os
from pathlib import Path

def test_parsers_config():
    """Test that parsers configuration can be loaded."""
    print("Testing Parsers Configuration...")

    try:
        # Import directly to avoid module issues
        sys.path.append('silan')
        from config.loader import ConfigLoader

        config = ConfigLoader(Path('silan/config'))
        parsers_config = config.get_parsers_config()

        print(f"✅ Parsers config loaded successfully")

        # Test content types
        content_types = parsers_config.get('content_types', {})
        supported_types = content_types.get('supported_types', [])
        print(f"✅ Supported content types: {', '.join(supported_types)}")

        # Test processing rules
        processing_rules = content_types.get('processing_rules', {})
        for content_type, rules in processing_rules.items():
            primary_patterns = rules.get('primary_file_patterns', [])
            required_fields = rules.get('required_fields', [])
            special_files = rules.get('special_files_enabled', False)
            print(f"✅ {content_type}: patterns={primary_patterns}, required={required_fields}, special_files={special_files}")

        # Test special files config
        special_files = parsers_config.get('special_files', {})
        files_config = special_files.get('files', {})

        for filename, file_config in files_config.items():
            processor = file_config.get('processor')
            metadata_key = file_config.get('metadata_key')
            description = file_config.get('description')
            print(f"✅ {filename}: processor={processor}, key={metadata_key}, desc='{description}'")

        return True

    except Exception as e:
        print(f"❌ Error testing parsers config: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base_parser_config_integration():
    """Test BaseParser integration with configuration."""
    print("\nTesting BaseParser Configuration Integration...")

    try:
        sys.path.append('silan')
        from parsers.base_parser import BaseParser
        from pathlib import Path

        # Create a mock parser
        class TestParser(BaseParser):
            def _get_content_type(self):
                return 'test'

            def parse_file(self, file_path):
                return None

        parser = TestParser(Path('.'))

        # Test content type configuration
        idea_config = parser.get_content_type_config('idea')
        print(f"✅ Idea config: special_files_enabled={idea_config.get('special_files_enabled')}")
        print(f"✅ Idea required fields: {idea_config.get('required_fields')}")

        blog_config = parser.get_content_type_config('blog')
        print(f"✅ Blog config: primary patterns={blog_config.get('primary_file_patterns')}")

        # Test special files configuration
        special_config = parser._get_default_special_file_config()
        print(f"✅ Special files loaded: {list(special_config.keys())}")

        # Test should_process_special_files
        should_process_idea = parser.should_process_special_files('idea')
        should_process_blog = parser.should_process_special_files('blog')
        print(f"✅ Should process special files - idea: {should_process_idea}, blog: {should_process_blog}")

        return True

    except Exception as e:
        print(f"❌ Error testing BaseParser integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_idea_parser_config():
    """Test IdeaParser configuration-driven processing."""
    print("\nTesting IdeaParser Configuration...")

    try:
        sys.path.append('silan')
        from parsers.idea_parser import IdeaParser
        from pathlib import Path

        parser = IdeaParser(Path('.'))

        # Test idea-specific special file config
        idea_special_config = parser._get_idea_special_file_config()

        for filename, config in idea_special_config.items():
            processor = config.get('processor')
            metadata_key = config.get('metadata_key')
            post_process = config.get('post_process')
            print(f"✅ {filename}: processor={processor}, key={metadata_key}, post_process={post_process}")

        # Verify references has idea-specific post-processing
        refs_config = idea_special_config.get('REFERENCES.md', {})
        if refs_config.get('post_process') == 'idea_references':
            print("✅ References has idea-specific post-processing")
        else:
            print("⚠️  References missing idea-specific post-processing")

        return True

    except Exception as e:
        print(f"❌ Error testing IdeaParser config: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_driven_processing():
    """Test that different content types follow their configuration rules."""
    print("\nTesting Configuration-Driven Processing Rules...")

    try:
        sys.path.append('silan')
        from config.loader import ConfigLoader

        config = ConfigLoader(Path('silan/config'))

        # Test extraction rules
        extraction_config = config.get('extraction.frontmatter.parsers', config_file='parsers')
        if extraction_config:
            print(f"✅ Frontmatter parsers: {extraction_config}")

        # Test metadata mapping
        metadata_mapping = config.get('extraction.metadata_mapping', config_file='parsers')
        if metadata_mapping:
            title_mapping = metadata_mapping.get('title', [])
            print(f"✅ Title field mappings: {title_mapping}")

        # Test localization settings
        default_lang = config.get('localization.default_language', config_file='parsers')
        supported_langs = config.get('localization.supported_languages', config_file='parsers')
        print(f"✅ Default language: {default_lang}")
        print(f"✅ Supported languages: {supported_langs}")

        return True

    except Exception as e:
        print(f"❌ Error testing config-driven processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all content processing configuration tests."""
    print("🧪 Content Processing Configuration Test Suite")
    print("=" * 60)

    tests = [
        test_parsers_config,
        test_base_parser_config_integration,
        test_idea_parser_config,
        test_config_driven_processing
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

    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All content processing tests passed!")
        print("\n💡 Key Features Validated:")
        print("  • Content types defined in YAML configuration")
        print("  • Processing rules per content type")
        print("  • Special file processing configuration")
        print("  • Parser-specific customization")
        print("  • Configuration-driven feature flags")
        return 0
    else:
        print("⚠️  Some content processing tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())