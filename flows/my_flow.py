from prefect import flow


@flow(log_prints=True)
def my_flow(name):
    print(f"Hello {name}!")


if __name__ == "__main__":
    my_flow("Kevin")
