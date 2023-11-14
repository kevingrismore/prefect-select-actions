# Select Actions

`select_actions` allows users to choose from a list of predefined actions for their `build`, `push`, and `pull` steps. When `select_actions` is invoked, any combination of `--build`, `--push`, and `--pull` may be provided. These steps must be defined under the `actions` portion of a `prefect.yaml` file. Each action selected will override the default step definition at the root level of your `prefect.yaml`.

## Examples

This repository supposes the following, for the sake of example:

- You have two Prefect workspaces, one used for staging and one used for production.
- You have one or more deployments which should be mirrored across workspaces.
- Your deployments are configured to use git code storage, and the branch a deployment uses should differ per workspace.
- Flows run in containers, so images need to be rebuilt when Python dependencies or docker build steps change. Since dependencies can differ per branch/workspace, each branch/workspace pairing should have its own image.
- Images are stored on Dockerhub.
- The following values are stored as secrets in the repository's settings:
  - `PREFECT_API_KEY`
  - `PREFECT_API_URL` (API url for produciton workspace)
  - `PREFECT_API_URL_STG` (API url for staging workspace)
  - `DOCKERHUB_USERNAME`
  - `DOCKERHUB_TOKEN`

When the Github Actions workflow is run, `select_actions` will modify the `prefect.yaml` that has been cloned into the Github Actions runner. `prefect deploy --all` will be run against the modified yaml, which only persists for the duration of the Actions workflow.

`select_actions` is used as part of a Github Actions workflow to modify `prefect.yaml` according to a set of triggers and conditions. Since these deployments are using git code storage, there are a limited set of conditions under which running `prefect deploy` is required.

See `.github/workflows` for more complete examples.

### Starting `prefect.yaml` (actions section only)

```yaml
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
          tag: "{{ get-commit-hash.stdout }}"
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
          tag: "{{ get-commit-hash.stdout }}"
          dockerfile: Dockerfile
  push:
    push_image:
      - prefect_docker.deployments.steps.push_docker_image:
          requires: prefect-docker
          image_name: "{{ build-image.image_name }}"
          tag: "{{ build-image.tag }}"
  pull:
    staging:
      - prefect.deployments.steps.git_clone:
        repository: git@github.com:kevingrismore/prefect-select-actions.git
        branch: staging
        credentials: "{{ prefect.blocks.github-credentials.my-block-name }}"
    production:
      - prefect.deployments.steps.git_clone:
        repository: git@github.com:kevingrismore/prefect-select-actions.git
        branch: main
        credentials: "{{ prefect.blocks.github-credentials.my-block-name }}"

build: null

push: null

pull: null
```

### Build and push an image

When the `Dockerfile` or `requirements.txt` changes, the image must be built and pushed. Let's say this has happened on the `main` branch. The Github Actions workflow will detect these changes and run the following:

`python select_actions.py --build build_image --push push_image --pull production`

```yaml
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
          tag: "{{ get-commit-hash.stdout }}"
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
          tag: "{{ get-commit-hash.stdout }}"
          dockerfile: Dockerfile
  push:
    push_image: &id002
      - prefect_docker.deployments.steps.push_docker_image:
          requires: prefect-docker
          image_name: "{{ build-image.image_name }}"
          tag: "{{ build-image.tag }}"
  pull:
    staging:
      - prefect.deployments.steps.git_clone:
        repository: git@github.com:kevingrismore/prefect-select-actions.git
        branch: staging
        credentials: "{{ prefect.blocks.github-credentials.my-block-name }}"
    production: &id003
      - prefect.deployments.steps.git_clone:
        repository: git@github.com:kevingrismore/prefect-select-actions.git
        branch: main
        credentials: "{{ prefect.blocks.github-credentials.my-block-name }}"

build: *id001

push: *id002

pull: *id003
```

### Update or create a deployment in `prefect.yaml`

When a deployment definition is changed or added, we need to persist those changes to Prefect Cloud/Server, but no image building or pushing is required. This time, the changes were pushed to the `staging` branch:

`python select_actions.py --pull staging`

```yaml
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
          tag: "{{ get-commit-hash.stdout }}"
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
          tag: "{{ get-commit-hash.stdout }}"
          dockerfile: Dockerfile
  push:
    push_image:
      - prefect_docker.deployments.steps.push_docker_image:
          requires: prefect-docker
          image_name: "{{ build-image.image_name }}"
          tag: "{{ build-image.tag }}"
  pull:
    staging: &id001
      - prefect.deployments.steps.git_clone:
        repository: git@github.com:kevingrismore/prefect-select-actions.git
        branch: staging
        credentials: "{{ prefect.blocks.github-credentials.my-block-name }}"
    production:
      - prefect.deployments.steps.git_clone:
        repository: git@github.com:kevingrismore/prefect-select-actions.git
        branch: main
        credentials: "{{ prefect.blocks.github-credentials.my-block-name }}"

build:

push:

pull: *id001
```
