#!/usr/bin/env python

from github import Github
from git import Repo
import os
import configparser
import re, shutil, tempfile
import docker

"""
This project listens for events from a docker image registry and then will search through configured repositories
looking for Dockerfiles containing 'FROM {container}'. It will then clone master, update the code with the new
docker image, open an issue reporting the out of date container, and then open a PR with a branch called:
{container}-version-update.
"""


def auth(ACCESS_TOKEN):
    gh = Github(ACCESS_TOKEN)
    return gh


def sed_inplace(filename, pattern, repl):
    '''
    Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    https://stackoverflow.com/questions/4427542/how-to-do-sed-like-text-replace-with-python
    '''
    # For efficiency, precompile the passed regular expression.
    pattern_compiled = re.compile(pattern)

    # For portability, NamedTemporaryFile() defaults to mode "w+b" (i.e., binary
    # writing with updating). This is usually a good thing. In this case,
    # however, binary writing imposes non-trivial encoding constraints trivially
    # resolved by switching to text writing. Let's do that.
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
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
        if repo.active_branch == master
        current = repo.create_head(head)
        current.checkout()
        repo.git.pull("origin", base)

        if repo.index.diff(None) or repo.untracked_files:

            repo.git.add(A=True)
            repo.git.commit(m=f"fix: updating docker image: {container}")
            repo.git.push("--set-upstream", "origin", current)
            print("git push")
        else:
            print("no changes")

def pull_repo(gh, repo_name):
    repo_url = gh.get_repo(repo_name).clone_url
    try:
        print(f"cloning {repo_name}")
        Repo.clone_from(repo_url, repo_name)
        repo = Repo(repo_name)
        branch = repo.active_branch
        return branch.name
    except:
        print("something went wrong when cloning repo")

def update_container_image(old_container, new_container, directory):
    if old_container == new_container:
        client = docker.from_env()
        old_image = client.images.get(old_container)
        # TODO: Figure out how to do a docker inspect because I'm not sure if docker python lib lets us do it...
    for root, dirs, files in os.walk(directory):
        if name in files:
            sed_inplace(os.path.join(root, name),old_container,new_container)

def remove_directory(repo_name):
    try:
        shutil.rmtree(repo_name)
    except OSError as e:
        print(f"Error: {repo_name}: {e.sterror}")
    return True

def update_from_image(gh, repositories, old_container, new_container):
    """
    This code pulls the repository in question, does a git checkout on a new branch,
    then does a find and replace on the old image and the new image
    and then does a git commit and git push, and then opens a PR
    """

    for repo in repositories:
        base = pull_repo(gh, repo)
        update_container_image(old_container, new_container, repo)
        head = f"{container}-version-update"
        commit_files(repo, head, base, container)
        open_new_pr(gh, repo, head, body=f"updating {container} version")
        remove_directory()


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
        DOCKERFILE = os.environ["DOCKERFILE"]
        # GITHUB_URL = os.environ["GITHUB_URL"]
    except KeyError("DOCKERFILE"):
        return ACCESS_TOKEN, ORGANIZATIONS, DOCKERFILE='DOCKERFILE'
    except KeyError:
        try:
            config = configparser.ConfigParser()
            config.read(os.environ["LOTHBROK_CONFIG"])
            config.get("LOTHBROK", "ACCESS_TOKEN")
            config.get("LOTHBROK", "DOCKERFILE")
            config.get("LOTHBROK", "ORGANIZATIONS")
            # config.get("LOTHBROK", "GITHUB_URL")
        except:
            print(
                "Error getting configurations. Enviornment variables not set or environment Variable: LOTHBROK_CONFIG not set and/or file doesn't exist."
            )
    else:
        return ACCESS_TOKEN, DOCKERFILE, ORGANIZATIONS


def main():
    ACCESS_TOKEN, DOCKERFILE, ORGANIZATIONS = configure()
    gh = auth(ACCESS_TOKEN)
    container = "debian:latest"
    query = f"FROM {container} in:{DOCKERFILE}"
    repositories = search_github(gh, query, ORGANIZATIONS)
    update_from_image(gh, repositories, container, container)


if __name__ == "__main__":
    main()