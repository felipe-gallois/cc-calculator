# Country centrality calculator

🚧 **Status: Proof of concept (PoC)**  

This program helps you calculate country centrality in Internet routing.

Centrality, in this context, means importance or unavoidability. Thus, a country is central for Internet routing because it is frequently involved in this task, even if not explicitly empowered.

Despite being able to indicate innefficiencies, analyzing Internet routing centrality is important to access the digital sovereignty of a country.

## Developing

These are the requirements for executing locally or testing the program:

- Python
- Poetry

First, install the dependencies required by the project, like so:

```bash
poetry install
```

This will create a new virtual environment and install the dependencies inside it.

To run the country centrality calculator program, execute

```bash
poetry run cccalc
```

, and, to run all tests, execute

```bash
poetry run pytest
```
