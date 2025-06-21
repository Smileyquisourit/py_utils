# py_utils

**py_utils**  is a modular Python library designed to provide generic tools for configuration management and logging.

It consists of two main subpackages:

- `ConfigHelper` for hierarchical and typed configuration file management.

- `Logueur` for a customizable logging system with topics, levels, and multiple output handlers.

This project aims to centralize reusable utilities across Python projects, emphasizing clarity, robustness, and testability.

---

## ⚙️ Installation

You can install this package from the source:
``` bash
$ git clone https://github.com/Smileyquisourit/py_utils.git
$ cd py_utils
$ pip install .
```

Note: You can also install it in *editable* mode if you want to modify the source code by passing the `-e` flag to the pip command:
``` bash
$ pip install -e .
```

You can also install it directly with this repo, in a virtual environnment:
``` bash
$ python3 -m venv .venv
(.venv) $ pip install git+https://github.com/Smileyquisourit/py_utils.git
```

### Usage

After installation, you can import the modules like this:

```python
from py_utils.ConfigHelper import ConfigHelper
from py_utils.Logueur import Logueur
```

### Make the documentation

To build the documentation, you will need to install a few sphinx package :

```bash
(.venv) $ pip install -r doc-requirements.txt
```

You can then build the documentation :
``` bash
(.venv) $ cd docs
(.venv) $ make html
```

---

## 📦 Description des modules

### 🔧 ConfigHelper

An object-oriented tool for defining, structuring, and validating configuration files. It can read configuration from different format, like a text file (using a modified INI structure) or JSON document.

#### Features :
- Typed variable declaration (int, float, str, bool)
- Automatic consistency checking
- Hierarchical structure via nested sections
- Dedicated exceptions for type or structure errors

#### Usage example :

```python
from py_utils.ConfigHelper import ConfigHelper

# An example configuration, that can be put in a text file:
app_str = """
langage:str = en
debug:bool = False

[user]
timeout:int = 30
langage = fr

[admin]
debug:bool = True
timeout:int = 15
"""

cfg = ConfigHelper()
cfg.read(app_str)

# Access via items:
print(cfg["user"]["timeout"])  # = 30, as an int
print(cfg["user"]["debug"])    # = False, as a bool

# Access via attributs:
print(cfg.admin.debug)  # = True, as bool
print(cfg.langage)      # = "en", as str
```

---

### 🪵 Logueur

A structured, object-oriented logging system with support for:
- levels (`INFO`, `WARNING`, `ERROR`, etc.)
- topics (thematically grouping logs)
- multiple outputs: console, files, etc.

#### Usage example :

```python
from py_utils.Logueur import Logueur, ConsoleLogueurFactory

logger = ConsoleLogueurFactory("INFO")
logger.info("Script startup", topic="System")
```

---

