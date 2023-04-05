- `apply` doesn't existe anymore in python 3 :
`pip install apply`
```python
from apply import apply
```

- Tkinter as changed:
```python
from Tkinter import *
import tkFileDialog
```
become :
```python
from tkinter import *
from tkinter import filedialog as tkFileDialog
```

- `Numeric` has been removed as of `numpy.oldnumeric`
```python
import Numeric
```
become:
```python
import numpy as Numeric
```

- Some types have been integrated to python 3 directly and int/long are now the same
```python
IntType, FloatType, ComplexType, LongType
```
become:
```python
int, float, complex
```

- Python Imaging Library (`import Image`) replaced by Pillow (`from PIL import Image`)