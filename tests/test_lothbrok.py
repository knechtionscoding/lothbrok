from lothbrok.main import update_from_image
from lothbrok import main as lothbrok
import pytest
import shutil
from github import Github
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


@pytest.mark.repo
def test_pull_repo():
    # Configure for test
    ACCESS_TOKEN, _ = lothbrok.configure()
    gh = lothbrok.auth(ACCESS_TOKEN)

    # Test itself
    result = lothbrok.pull_repo(gh, "KnechtionsCoding/lothbrok")

    # Clean up of the repository afterwards
    cwd = os.getcwd()
    shutil.rmtree(f"{cwd}/KnechtionsCoding")

    assert result


@pytest.mark.repo
def test_update_from_image():
    # Configure for test
    ACCESS_TOKEN, _ = lothbrok.configure()
    gh = lothbrok.auth(ACCESS_TOKEN)
    repositories = [
        {"name": "guild-connect/dockerfile-test-repo", "files": "Dockerfile2"}
    ]
    lothbrok.update_from_image(gh, repositories, "library/ubuntu", "", "test")


@pytest.mark.repo
def test_search_github():
    # Configure for test
    ACCESS_TOKEN, ORGANIZATIONS = lothbrok.configure()
    gh = lothbrok.auth(ACCESS_TOKEN)
    lothbrok.search_github(gh, "FROM library/ubuntu:", ORGANIZATIONS)


@pytest.mark.repo
def test_update_container_image():
    # Configure for test
    ACCESS_TOKEN, _ = lothbrok.configure()
    gh = lothbrok.auth(ACCESS_TOKEN)
    repositories = "guild-connect/dockerfile-test-repo"
    lothbrok.update_container_image(
        "library/ubuntu", "", "test", f"{repositories}/Dockerfile2"
    )


@pytest.mark.repo
def test_commit_files():
    repo = "guild-connect/dockerfile-test-repo"
    lothbrok.commit_files(repo, "test", "main", "library/ubuntu")


# @pytest.mark.search
# def test_search_github():
#     assert lothbrok.search_github()
