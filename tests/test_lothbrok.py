from lothbrok import main as lothbrok
import pytest
import os


@pytest.mark.processor
def test_processor_semantic_version_with_v_update_minor():
    assert lothbrok.processor("v1.0.0-version") == "v1."


@pytest.mark.processor
def test_processor_semantic_version_without_v_update_minor():
    assert lothbrok.processor("1.0.0-version") == "1."


@pytest.mark.processor
def test_processor_semantic_version_with_v_update_patch():
    assert lothbrok.processor("v1.0.0-version", False) == "v1.0."


@pytest.mark.processor
def test_processor_semantic_version_without_v_update_patch():
    assert lothbrok.processor("1.0.0-version", False) == "1.0."


@pytest.mark.processor
def test_processor_versioned_date():
    assert lothbrok.processor("stuff-20201112") == "stuff-"


# @pytest.mark.search
# def test_search_github():
#     assert lothbrok.search_github()