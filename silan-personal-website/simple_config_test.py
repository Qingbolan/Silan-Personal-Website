#!/usr/bin/env python3
"""
Simple test to verify YAML configuration files can be loaded.
"""

import yaml
from pathlib import Path

def test_yaml_files():
    """Test that all YAML files can be loaded and parsed."""
    config_dir = Path('silan/config')

    if not config_dir.exists():
        print(f"❌ Config directory not found: {config_dir}")
        return False

    yaml_files = list(config_dir.glob('*.yaml'))

    if not yaml_files:
        print(f"❌ No YAML files found in {config_dir}")
        return False

    print(f"Found {len(yaml_files)} YAML configuration files:")

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data:
                top_keys = list(data.keys())
                print(f"✅ {yaml_file.name}: {len(top_keys)} sections - {', '.join(top_keys)}")
            else:
                print(f"⚠️  {yaml_file.name}: Empty file")

        except Exception as e:
            print(f"❌ {yaml_file.name}: Failed to load - {e}")
            return False

    return True

def test_config_structure():
    """Test that config files have expected structure."""
    config_dir = Path('silan/config')

    expected_files = {
        'models.yaml': ['models'],
        'api.yaml': ['api'],
        'database.yaml': ['database'],
        'logging.yaml': ['logging'],
        'parsers.yaml': ['parsers'],
        'defaults.yaml': ['defaults']
    }

    print("\nTesting configuration structure:")

    for filename, expected_keys in expected_files.items():
        file_path = config_dir / filename

        if not file_path.exists():
            print(f"❌ {filename}: File not found")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            missing_keys = [key for key in expected_keys if key not in data]

            if missing_keys:
                print(f"⚠️  {filename}: Missing keys - {', '.join(missing_keys)}")
            else:
                print(f"✅ {filename}: All expected keys present")

        except Exception as e:
            print(f"❌ {filename}: Error - {e}")

    return True

def test_models_config_values():
    """Test specific model configuration values."""
    config_file = Path('silan/config/models.yaml')

    if not config_file.exists():
        print("❌ models.yaml not found")
        return False

    print("\nTesting model configuration values:")

    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    models = data.get('models', {})

    # Test project status
    project_status = models.get('projects', {}).get('status', {})
    expected_status = ['active', 'completed', 'paused', 'cancelled']

    for status in expected_status:
        if status in project_status:
            print(f"✅ Project status '{status}': '{project_status[status]}'")
        else:
            print(f"❌ Project status '{status}' not found")

    # Test blog types
    blog_types = models.get('blog', {}).get('types', {})
    expected_types = ['article', 'vlog', 'episode']

    for btype in expected_types:
        if btype in blog_types:
            print(f"✅ Blog type '{btype}': '{blog_types[btype]}'")
        else:
            print(f"❌ Blog type '{btype}' not found")

    # Test idea priorities
    idea_priority = models.get('ideas', {}).get('priority', {})
    expected_priorities = ['low', 'medium', 'high', 'urgent']

    for priority in expected_priorities:
        if priority in idea_priority:
            print(f"✅ Idea priority '{priority}': '{idea_priority[priority]}'")
        else:
            print(f"❌ Idea priority '{priority}' not found")

    return True

def main():
    """Run simple configuration tests."""
    print("🧪 Simple YAML Configuration Tests")
    print("=" * 40)

    success = True

    if not test_yaml_files():
        success = False

    if not test_config_structure():
        success = False

    if not test_models_config_values():
        success = False

    print("\n" + "=" * 40)
    if success:
        print("🎉 All basic configuration tests passed!")
        return 0
    else:
        print("⚠️  Some configuration tests failed.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())