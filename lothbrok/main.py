#!/usr/bin/env python

from github import Github
from git import Repo

ACCESS_TOKEN = ""
DOCKERFILE = "DOCKERFILE"
ORG_NAMES = ""

"""
This project listens for events from a docker image registry and then will search through configured repositories
looking for Dockerfiles containing 'FROM {container}'. It will then clone master, update the code with the new
docker image, open an issue reporting the out of date container, and then open a PR with a branch called:
{container}-version-update.
"""


def auth(ACCESS_TOKEN):
    gh = Github(ACCESS_TOKEN)
    # org = gh.get_organization(ORG_NAMES)
    return gh


def search_github(gh, query):
    result = gh.search_code(query)
    for repo in result:
        print(repo)
    return result


def commit_files(repo, head, base, container):
    if repo != None:
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


def pull_repo(repo):
    return True


def update_container_image(container):
    return True


def remove_directory():
    return True


def update_from_image(gh, repositories, container):
    """
    This code pulls the repository in question, does a git checkout on a new branch,
    then does a find and replace on the old image and the new image
    and then does a git commit and git push, and then opens a PR
    """
    for repo in repositories:
        pull_repo(repo)
        update_container_image(container)
        head = f"{container}-version-update"
        # TODO: Build in check for master versus main base branch
        commit_files(repo, head, "master", container)
        open_new_pr(gh, repo, head, body=f"updating {container} version")
        remove_directory()


def open_new_pr(gh, repo, title, body, head="develop", base="master"):
    """
    This function should open a new PR with the requested name against github repo.
    """
    repo = gh.get_repo(repo)
    results = repo.create_pull(title=title, body=body, head=head, base=base)
    return results


def main():
    gh = auth(ACCESS_TOKEN)
    container = "debian:latest"
    query = f"org:guild-connect FROM {container} in:{DOCKERFILE}"
    repositories = search_github(gh, query)
    update_from_image(gh, repositories, container)


if __name__ == "__main__":
    main()