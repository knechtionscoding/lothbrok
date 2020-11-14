# LOTHBROK

This projects attempts to solve a long standing problem of container to container image dependencies. When a docker container in a registry is updated there is no current mechanism to then create a downstream build of dependent containers across repositories. This projects attempts to listen for a webhook event and then scans github repositories for downstream containers using the image in the webhook. Lothbrok will then pull the repository, update any references to the image in question, push up a new branch and PR into the repository for ease of updating. Lothbrok relies on your own CICD pipelines hooked up to github to validate success and you should review any changes or images.

## SETUP

### Pre-Requisites
- Python3
- Poetry

### Install steps
git clone <repo>
cd <dir> 
poetry install