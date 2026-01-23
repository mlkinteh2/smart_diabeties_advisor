import sys
import os

# Force AppData path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    import matplotlib
    print(f"Matplotlib File: {matplotlib.__file__}")
    print(f"Matplotlib Version: {matplotlib.__version__}")
except ImportError as e:
    print(f"Error importing matplotlib: {e}")

try:
    import matplotlib.colorizer
    print("Success importing matplotlib.colorizer")
except ImportError as e:
    print(f"Error importing matplotlib.colorizer: {e}")

try:
    import shap
    print(f"SHAP Version: {shap.__version__}")
except ImportError as e:
    print(f"Error importing shap: {e}")
