import sys
import os

print("--- sys.path ---")
for p in sys.path:
    print(p)

print("\n--- numpy ---")
try:
    import numpy
    print(f"File: {numpy.__file__}")
    print(f"Version: {numpy.__version__}")
except ImportError as e:
    print(e)

print("\n--- sklearn ---")
try:
    import sklearn
    print(f"File: {sklearn.__file__}")
    print(f"Version: {sklearn.__version__}")
except ImportError as e:
    print(e)

print("\n--- Attempting offending import ---")
try:
    from sklearn.externals import array_api_compat
    print("Success importing array_api_compat")
except Exception as e:
    print(f"Failed: {e}")
