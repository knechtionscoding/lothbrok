#!/usr/bin/env python

from github import Github
from git import Repo
import os
import configparser
import re, shutil, tempfile
import docker
import semantic_version
from datetime import datetime


"""
This project listens for events from a docker image registry and then will search through configured repositories
looking for Dockerfiles containing 'FROM {container}'. It will then clone master, update the code with the new
docker image, open an issue reporting the out of date container, and then open a PR with a branch called:
{container}-version-update.
"""


def auth(ACCESS_TOKEN):
    gh = Github(ACCESS_TOKEN)
    return gh


def processor(tag, update_minor=True):
    old_tag_prefix = ""
    v_pattern = r"^v\d+.\d+.\d+.*$"
    date_pattern = r"^.+?(?=\d{8})"
    if semantic_version.validate(tag):
        version = semantic_version.Version(tag)
        if not update_minor:
            old_tag_prefix = f"{version.major}.{version.minor}."
        else:
            old_tag_prefix = f"{version.major}."
    # Checks if v<semantic-vesrion>
    elif re.match(v_pattern, tag):
        vless_tag = tag[1:]
        if semantic_version.validate(vless_tag):
            version = semantic_version.Version(vless_tag)
            if not update_minor:
                old_tag_prefix = f"v{version.major}.{version.minor}."
            else:
                old_tag_prefix = f"v{version.major}."
    # Check if there is a YYYYMMDD Date in the tag and return everyting prior
    elif re.match(date_pattern, tag):
        pre_date = re.match(date_pattern, tag)
        old_tag_prefix = f"{pre_date.group()}"
    else:
        old_tag_prefix = ""

    return old_tag_prefix


def sed_inplace(filename, pattern, repl):
    """
    Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    https://stackoverflow.com/questions/4427542/how-to-do-sed-like-text-replace-with-python
    """
    # For efficiency, precompile the passed regular expression.
    pattern_compiled = re.compile(pattern)

    # For portability, NamedTemporaryFile() defaults to mode "w+b" (i.e., binary
    # writing with updating). This is usually a good thing. In this case,
    # however, binary writing imposes non-trivial encoding constraints trivially
    # resolved by switching to text writing. Let's do that.
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))

    # Overwrite the original file with the munged temporary file in a
    # manner preserving file attributes (e.g., permissions).
    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)


def search_github(gh, query, organizations):
    for org in organizations:
        result = gh.search_code(query, organizations=organizations)
        repositories = []
        for repo in result:
            repositories.append(repo.repository.full_name)
    return repositories


def commit_files(repo, head, base, container):
    if repo != None:
        if repo.active_branch == master:
            current = repo.create_head(head)
            current.checkout()
            repo.git.pull("origin", base)

        if repo.index.diff(None) or repo.untracked_files:

            repo.git.add(A=True)
            repo.git.commit(m=f"fix: bump {container}:{tag_prefix} to {new_tag}")
            repo.git.push("--set-upstream", "origin", current)
            print("git push")
        else:
            print("no changes")


def pull_repo(gh, repo_name):
    repo_url = gh.get_repo(repo_name).clone_url
    try:
        print(f"cloning {repo_name}")
        Repo.clone_from(repo_url, repo_name, depth=1)
        repo = Repo(repo_name)
        branch = repo.active_branch
        return branch.name
    except:
        print("something went wrong when cloning repo")


def update_container_image(container, old_tag_prefix, new_tag, directory):
    pattern = f"r'{container}:{old_tag_prefix}.* '"
    for root, _, files in os.walk(directory):
        if name in files:
            sed_inplace(os.path.join(root, name), pattern, new_tag)


def remove_directory(repo_name):
    try:
        shutil.rmtree(repo_name)
    except OSError as e:
        print(f"Error: {repo_name}: {e.sterror}")
    return True


def update_from_image(gh, repositories, container, tag_prefix, new_tag):
    """
    This code pulls the repository in question, does a git checkout on a new branch,
    then does a find and replace on the old image and the new image
    and then does a git commit and git push, and then opens a PR
    """

    for repo in repositories:
        base = pull_repo(gh, repo)
        update_container_image(container, tag_prefix, new_tag, repo)
        head = f"fix/{container}-version-update"
        commit_files(repo, head, base, container)
        open_new_pr(gh, repo, head, body=f"fix: updating {container} version")
        remove_directory(repo)


def open_new_pr(gh, repo, title, body, head="develop", base="master"):
    """
    This function should open a new PR with the requested name against github repo.
    """
    repo = gh.get_repo(repo)
    results = repo.create_pull(title=title, body=body, head=head, base=base)
    return results


def configure():
    """
    This function configures the program and sets constants throughout.
    Constants set via this function:
    ACCESS_TOKEN
    GITHUB_URL
    ORGANIZATIONS
    DOCKERFILE

    First looks for environment variables for each value. Then looks for a config file (specified via environment variable LOTHBROK_CONFIG).
    """

    ACCESS_TOKEN = ""
    # GITHUB_URL = "https://github.com"
    ORGANIZATIONS = []

    try:
        ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
        ORGANIZATIONS = os.environ["ORGANIZATIONS"]
        # GITHUB_URL = os.environ["GITHUB_URL"]
    except KeyError:
        try:
            config = configparser.ConfigParser()
            config.read(os.environ["LOTHBROK_CONFIG"])
            config.get("LOTHBROK", "ACCESS_TOKEN")
            config.get("LOTHBROK", "ORGANIZATIONS")
            # config.get("LOTHBROK", "GITHUB_URL")
        except:
            print(
                "Error getting configurations. Enviornment variables not set or environment Variable: LOTHBROK_CONFIG not set and/or file doesn't exist."
            )
    else:
        return ACCESS_TOKEN, ORGANIZATIONS


def main(container, tag):
    ACCESS_TOKEN, ORGANIZATIONS = configure()
    gh = auth(ACCESS_TOKEN)
    tag_prefix = processor(tag)
    query = f"FROM {container}:tag_prefix"
    # TODO: Solve how to best search. Github won't allow exact match searches
    # We could check out each repo in an organization, but in orgs with lots of repos
    # That will not scale really well.
    # Could search docker repositories if they allow us to do an inspect or something
    # But that isn't a great either because it won't solve non-published containers
    # Or containers that are in other places
    # Github will match every word inside the file, so searching as specifically as possible
    # will result in very close results
    repositories = search_github(gh, query, ORGANIZATIONS)
    update_from_image(gh, repositories, container, tag_prefix, tag)


if __name__ == "__main__":
    container = "debian"
    tag = "11.0.0"
    main(container, tag)
