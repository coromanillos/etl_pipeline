import pytest
from unittest.mock import mock_open, patch
from src.utils.config import load_config, get_env_var
import yaml

def test_load_config_success():
    dummy_yaml = """
    api:
      key: dummy-key
    """
    with patch("builtins.open", mock_open(read_data=dummy_yaml)):
        result = load_config("/fake/path.yaml")
        assert result == {"api": {"key": "dummy-key"}}

def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/file.yaml")

def test_load_config_yaml_error():
    with patch("builtins.open", mock_open(read_data="this: [unbalanced")):
        with pytest.raises(yaml.YAMLError):
            load_config("/fake/path.yaml")


def test_get_env_var_success():
    result = get_env_var("DUMMY_VAR", getter=lambda k: "value" if k == "DUMMY_VAR" else None)
    assert result == "value"

def test_get_env_var_missing_required():
    with pytest.raises(EnvironmentError):
        get_env_var("MISSING_VAR", getter=lambda k: None)

def test_get_env_var_optional_missing():
    result = get_env_var("OPTIONAL_VAR", required=False, getter=lambda k: None)
    assert result is None
