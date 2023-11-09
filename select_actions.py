"""Tool for selecting build, push, and pull actions in Prefect deployments."""
import click
import ruamel.yaml


def edit_yaml(step: str, action: str) -> None:
    """Reads in prefect.yaml and applies a specified action to a deployment step.

    Args:
        step (str): The name of the Prefect deployment step: build, push, or pull.
        action (str): The name of action to run on the step, as name in prefect.yaml.
    """

    yaml = ruamel.yaml.YAML()

    with open("prefect.yaml", "r") as f:
        data = yaml.load(f)
        data[step] = data["definitions"]["actions"][step][action]

    with open("prefect.yaml", "w") as f:
        yaml.dump(data, f)


@click.command()
@click.option("--build")
@click.option("--push")
@click.option("--pull")
def select_actions(build: str, push: str, pull: str) -> None:
    """Calls edit_yaml for each step in the Prefect deployment pipeline."""
    actions = {
        "build": build,
        "push": push,
        "pull": pull,
    }

    for step, action in actions.items():
        edit_yaml(step, action)


if __name__ == "__main__":
    select_actions()
