# Country centrality calculator

🚧 **Status: Proof of concept (PoC)**  

This program helps you calculate country centrality in Internet routing.

Centrality, in this context, means importance or unavoidability. Thus, a country is central for Internet routing because it is frequently involved in this task, even if not explicitly empowered.

Despite being able to indicate innefficiencies, analyzing Internet routing centrality is important to access the digital sovereignty of a country.

## Installation

This project requires the following dependencies to be pre-installed:

- Python (see versions in `pyproject.toml`)
- Poetry (see versions in `pyproject.toml`)

After installing them, follow the appropriate guide on how to set up your project environment. 

### Development

To set up the project for development, start by installing the development dependencies. The command below will create a new virtual environment and install the dependencies inside it.

```bash
poetry install
```

The dependencies include tools to assist in testing and code analysis:

- `ruff`: a linter and formatter, configured with this project's code conventions
- `mypy`: a static analysis tool that provides type-checking capabilities
- `pytest`: a testing framework

> **Tip:** You can configure your IDE to automate the use of these tools or use some of them as language servers to provide live code insights. 

> **Tip:** Because these tools are installed in the virtual environment, you have to call them through Poetry (`poetry run ...`)

Before submitting code to this repository, run all tests and check linting and formatting rules:

```bash
poetry run pytest
poetry run ruff check
poetry run mypy --strict {src,tests}
poetry run ruff format --check
```
