# Postman API

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-foo.svg)](https://pypi.org/project/hatch-foo)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-foo.svg)](https://pypi.org/project/hatch-foo)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

**This project is in its early development stages, so stability is not guaranteed, and documentation is limited. We welcome your feedback and contributions as we refine and expand this project together!**

## Overview

This generic project facilitates interaction with the Postman API. It is being released independently of the Data Artifex Postman Toolit package to allow its use by any developer working with Postman,

The package provides the following classes:

- PostmanApi: for direct access to the Postman API features. Takes a Postman API key as input.
- WorkspaceManager: To work with an existing workspace. Takes a PostmanApi and workspace identifier as input.
- CollectionManager: to work with an existing collection. Takes a WorkspaceManager and collection identifier as input.

Additional classes will be implemented to manage requests, folders, and other resources.

This package also includes Python classes to read/write Postman collections based on the 2.1 schema. The initial implementation leverages Python data classes. But this is being transitioned into Pydantic-based classes to strengthen features/validation and facilitate integration with other packages and frameworks.
 
An optional feature is under development to facilitate [tools calling](https://python.langchain.com/docs/concepts/tool_calling/) from LangChain / LangGraph.

This package is a component of the Data Artifex project.

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

### Installing Dependencies

To install the required dependencies, execute the following command:

```bash
pip install -r requirements.txt
```

Ensure you are in the project's root directory when running these commands.

Feel free to replace `<repository-url>` and `<repository-directory>` with the actual URL and directory name of your project. This enhanced version provides clear instructions and formatting to guide users through the installation process effectively.


## Usage

To use this package, you must have a Postman account and [API key](https://learning.postman.com/docs/developer/postman-api/authentication/).

See [Documentation](https://dataartifex.github.io/postman-api/).

 
## Roadmap

...

## Contributing
 
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

 
## License
 
The MIT License (MIT)

Copyright (c) 2024 Pascal L.G.A. Heus

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


