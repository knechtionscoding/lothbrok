from lothbrok import main as lothbrok
import pytest
import os


@pytest.mark.processor
def test_processor_semantic_version_with_v_update_minor():
    assert lothbrok.processor("debian", "v1.0.0-version") == "debian:v1."


@pytest.mark.processor
def test_processor_semantic_version_without_v_update_minor():
    assert lothbrok.processor("debian", "1.0.0-version") == "debian:1."


@pytest.mark.processor
def test_processor_semantic_version_with_v_update_patch():
    assert lothbrok.processor("debian", "v1.0.0-version", False) == "debian:v1.0."


@pytest.mark.processor
def test_processor_semantic_version_without_v_update_patch():
    assert lothbrok.processor("debian", "1.0.0-version", False) == "debian:1.0."


@pytest.mark.processor
def test_processor_versioned_date():
    assert lothbrok.processor("debian", "stuff-20201112") == "debian:stuff-"


# @pytest.mark.search
# def test_search_github():
#     assert lothbrok.search_github()