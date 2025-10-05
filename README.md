# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Installations and Setting Up

1. PostgresSQL

Install Postgres.app: If you don't have it, download and install it from https://postgresapp.com. It's a free, self-contained application.

Once installed, please open the application and press the "Start" button.

2. `.env` file

Please create a blank `.env` file in the root folder. Then, copy and paste the contents is `dot-env-sample` into the `.env` file. Please be sure to add this file to `.gitignore` since it does contain info that can't be pushed onto Github.

3. Homebrew

Please install homebrew from https://brew.sh/. Once Homebrew is installed, please run the following command:

```
brew install pipx
pipx ensurepath
```

`pipx` is needed in orer to run and install `pipenv`

## Virtual Environment

1. Install `pipenv`

```
pipx install pipenv

# Install production dependencies
pipenv install flask gunicorn python-dotenv

# Install development dependencies
pipenv install --dev pylint pytest coverage black flake8
```
This will create two new files in your project directory:

`Pipfile`: The replacement for pyproject.toml. It lists your project's dependencies.

`Pipfile.lock`: The replacement for poetry.lock. It locks the specific versions of all dependencies for reproducible builds.

2. Activating the Virtual Environment

```
pipenv shell
```

3. Other Necessary Commands

```
# Run the development server
pipenv run flask run

# Run your tests
pipenv run pytest

# Add a new production package
pipenv install <package-name>

# Add a new development package
pipenv install --dev <package-name>

# Remove a package
pipenv uninstall <package-name>
```

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
