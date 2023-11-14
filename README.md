# Scenario

This repository supposes the following, for the sake of example:

- You have two Prefect workspaces, one used for staging and one used for production
- You have one or more deployments which should be mirrored across workspaces
- Your deployments are configured to use git code storage, and the branch a deployment uses should differ per workspace
- Flows run in containers, so images need to be rebuilt when dependencies or build steps change. Since dependencies can differ per branch/workspace, each branch/workspace pairing should have its own image

# Select Actions

`select_actions` allows users to choose from a list of predefined actions for their `build`, `push`, and `pull` steps. When `select_actions` is invoked, any combination of `build`, `push`, and `pull` may be provided. These steps must be defined under the `actions` portion of a `prefect.yaml` file. Each action selected will override the default step definition at the root level of your `prefect.yaml`.

## Example

This example uses `select_actions.py` as part of a Github Actions workflow to modify `prefect.yaml` according to a set of triggers and conditions.

```
actions:
  build:
    build_image_stg:
    - prefect.deployments.steps.run_shell_script:
        id: get-commit-hash
        script: git rev-parse --short HEAD
        stream_output: false
    - prefect_docker.deployments.steps.build_docker_image:
        id: build-image
        requires: prefect-docker
        image_name: kevingrismoreprefect/github-actions-demo-stg
        tag: '{{ get-commit-hash.stdout }}'
        dockerfile: Dockerfile
    build_image_prod:
    - prefect.deployments.steps.run_shell_script:
        id: get-commit-hash
        script: git rev-parse --short HEAD
        stream_output: false
    - prefect_docker.deployments.steps.build_docker_image:
        id: build-image
        requires: prefect-docker
        image_name: kevingrismoreprefect/github-actions-demo-prod
        tag: '{{ get-commit-hash.stdout }}'
        dockerfile: Dockerfile
  push:
    push_image:
    - prefect_docker.deployments.steps.push_docker_image:
        requires: prefect-docker
        image_name: '{{ build-image.image_name }}'
        tag: '{{ build-image.tag }}'
  pull:
    staging:
    - prefect.deployments.steps.git_clone:
      repository: git@github.com:kevingrismore/prefect-select-actions.git
      branch: staging
      credentials: '{{ prefect.blocks.github-credentials.my-block-name }}'
    production:
    - prefect.deployments.steps.git_clone:
      repository: git@github.com:kevingrismore/prefect-select-actions.git
      branch: main
      credentials: '{{ prefect.blocks.github-credentials.my-block-name }}'

build: null

push: null

pull: null
```

`python select_actions.py --build build_image --push push_image --pull production`

```
actions:
  build:
    build_image_stg: &id001
    - prefect.deployments.steps.run_shell_script:
        id: get-commit-hash
        script: git rev-parse --short HEAD
        stream_output: false
    - prefect_docker.deployments.steps.build_docker_image:
        id: build-image
        requires: prefect-docker
        image_name: kevingrismoreprefect/github-actions-demo-stg
        tag: '{{ get-commit-hash.stdout }}'
        dockerfile: Dockerfile
    build_image_prod:
    - prefect.deployments.steps.run_shell_script:
        id: get-commit-hash
        script: git rev-parse --short HEAD
        stream_output: false
    - prefect_docker.deployments.steps.build_docker_image:
        id: build-image
        requires: prefect-docker
        image_name: kevingrismoreprefect/github-actions-demo-prod
        tag: '{{ get-commit-hash.stdout }}'
        dockerfile: Dockerfile
  push:
    push_image: &id002
    - prefect_docker.deployments.steps.push_docker_image:
        requires: prefect-docker
        image_name: '{{ build-image.image_name }}'
        tag: '{{ build-image.tag }}'
  pull:
    staging:
    - prefect.deployments.steps.git_clone:
      repository: git@github.com:kevingrismore/prefect-select-actions.git
      branch: staging
      credentials: '{{ prefect.blocks.github-credentials.my-block-name }}'
    production: &id003
    - prefect.deployments.steps.git_clone:
      repository: git@github.com:kevingrismore/prefect-select-actions.git
      branch: main
      credentials: '{{ prefect.blocks.github-credentials.my-block-name }}'

build: *id001

push: *id002

pull: *id003
```
