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


## Data Formats

There is a flask webserver that accepts webhooks. Each container repository has a separate endpoint at /webhooks/<registry-name>

e.g. `/webhooks/artifactory`

That endpoint is responsible for processing the incoming webhook and parsing out the data required


# Dataflow description

* Incoming Webhook containing at least the following two pieces of data: container and tag
* The processor will check if the tag is a semantic version
    * If the tag is a semantic version the program will only update the same major version
    * Option to update all versions, only update minor version
        * if exclude_minor is set to false
    * If the tag is in the format: `<prefix>-<date>` then lothbrok will only update the same prefix
* Return pattern to search for
* Call search function based on passed in option for SCM ()
* Clone repositories where `<container>:<prefix>` is found
* sed_in_place for `<container>:<prefix>` on repository
* git commit
* git push
* based on passed in option for SCM open PR if possible

# Conventional Commits

Lothbrok utilizes [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) both when contributing and when writing to repositories.
This allows for automated generation of changelogs, version bumping, and provide a more intuitive parsing of commits. All commits will be written as `fix:` level commits.
This is because Lothbrok will not update a major version of your container unless there is no versioning at all.

# TODOS:

* Write tests for search functions
* Write general search function
* Write tests for webhooks
* Write general webhook endpoint
* Write tests for cloning
* Write dockerfile
* Publish docker image
* Write K8s and Docker-Compose setup
