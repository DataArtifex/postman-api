# Postman API

[![PyPI - Version](https://img.shields.io/pypi/v/dartfx-postmanapi.svg)](https://pypi.org/project/dartfx-postmanapi)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dartfx-postmanapi.svg)](https://pypi.org/project/dartfx-postmanapi)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

**This project is in its early development stages. Stability is not guaranteed, and documentation is limited. We welcome your feedback and contributions as we refine and expand this project together!**

## Overview

This Python project aims to facilitate interaction with the Postman platform API. 

The package provides the following core Python classes:

- PostmanApi: for direct access to the Postman API features. Takes a Postman API key as input.
- WorkspaceManager: To work with an existing workspace. Takes a PostmanApi and workspace identifier as input.
- CollectionManager: to work with an existing collection. Takes a WorkspaceManager and collection identifier as input.

Additional classes will be implemented to manage requests, folders, and other resources.

This package also includes Python classes to read/write Postman collections based on version 2.1 of the [schema](https://schema.postman.com/). The initial implementation leverages Python data classes. But this is being transitioned into Pydantic-based classes to strengthen features/validation and facilitate integration with other packages and frameworks.
 
An optional feature is under development to facilitate [tools calling](https://python.langchain.com/docs/concepts/tool_calling/) from [LangChain](https://www.langchain.com/) / [LangGraph](https://langchain-ai.github.io/langgraph/).

This package is a component of the [Data Artifex](https://github.com/dataartifex) project. It is being released independently of the Data Artifex [Postman Toolkit]((https://github.com/dataartifex/postman-toolkit)) package to allow its use by any developer working with Postman.


## Installation

### PyPI Release

Once stable, this package will be officially released and distributed through [PyPI](https://pypi.org/). Stay tuned for updates!

### Local Installation

In the meantime, you can install the package locally by following these steps:

1. **Clone the Repository:**

   First, clone the repository to your local machine:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install the Package:**

   From the project's home directory, run the following command to install the package:

   ```bash
   pip install -e .
   ```

   To install the LangChain/LangGraph integration:
   
   ```bash
   pip install -e .[langchain]
   ```


## Usage

To use this package, you must have a Postman account and [API key](https://learning.postman.com/docs/developer/postman-api/authentication/).

*Until this repository is made public, you must generate the Sphinx documentation locally...*

First, ensure the relevant Sphinx packages are installed in your Python environment:

```
pip install sphinx sphinx sphinx-rtd-theme sphinx-copybutton myst-parser
```

Then navigate to the `docs` directory and call `make`.

If you do not have `make` installed, you can alternatively call:

`sphinx-build -M source build`

Upon completion, open the `docs/build/index.html` file in your browser.

 
## Roadmap

...

## Contributing
 
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

 