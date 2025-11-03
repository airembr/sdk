To build and publish your `sdk` package to PyPI, follow these steps:

---

### **Step 1: Install Required Tools**
First, ensure you have the latest versions of the required tools installed:

```sh
pip install --upgrade setuptools wheel twine
```

---

### **Step 2: Prepare Your Package Structure**
Ensure your project is structured correctly:

```
sdk/
│── sdk/     # Package directory
│   ├── __init__.py       # Required for Python package
│   ├── your_module.py    # Your package files
│── setup.py              # Setup script
│── README.md             # Long description file
│── LICENSE               # License file (optional)
│── .gitignore            # Ignore build artifacts
```

- The `__init__.py` file inside `skd/` ensures it's treated as a package.
- If you don’t have a `__init__.py` file inside the package directory, create an empty one.

---

### **Step 3: Build the Package**
Run the following command in the root directory of your package:

```sh
python setup.py sdist bdist_wheel
```

This will generate a `dist/` folder containing `.tar.gz` and `.whl` files.

---

### **Step 4: Test Locally (Optional)**
You can install your package locally before publishing to test it:

```sh
pip install dist/airembr_sdk-0.0.1-py3-none-any.whl
```

Verify it installs and works as expected.

---

### **Step 5: Upload to PyPI**
1. **Create an account on PyPI** if you haven't already: [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **Upload your package using Twine**:

```sh
twine upload dist/*
```

You'll be prompted for your PyPI username and password (or API token).

---

### **Step 6: Verify Installation**
Once uploaded, you can install it from PyPI to verify:

```sh
pip install airembr_sdk
```

---

### **Step 7: Automate Future Releases (Optional)**
For easier future releases:
- Update the version in `setup.py` (e.g., `0.0.2`).
- Run the build and upload steps again:

```sh
python setup.py sdist bdist_wheel
twine upload dist/*
```

# Authenticate PIP

To securely upload your Python package to PyPI using Twine with an API token, follow these steps:

---

### **1. Generate a PyPI API Token**

1. **Log in to PyPI**: Access your account at [https://pypi.org/](https://pypi.org/).

2. **Navigate to Account Settings**: Click on your username and select "Account settings."

3. **Create an API Token**:
   - Scroll to the "API tokens" section.
   - Click "Add API token."
   - Optionally, specify a name and scope for the token.
   - Click "Add token" and **copy** the generated token (it starts with `pypi-`).

---

### **2. Configure Authentication for Twine**

You can provide the API token to Twine in two ways:

**A. Using Environment Variables (Recommended for CI/CD Pipelines):**

1. **Set Environment Variables**:
   - Set the `TWINE_USERNAME` to `__token__`.
   - Set the `TWINE_PASSWORD` to your API token.

   For example, in a Unix-like terminal:

   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-Your-API-Token
   ```

   In Windows Command Prompt:

   ```cmd
   set TWINE_USERNAME=__token__
   set TWINE_PASSWORD=pypi-Your-API-Token
   ```

**B. Using a `.pypirc` File (For Local Development):**

1. **Create or Edit `.pypirc`**:
   - Locate or create a `.pypirc` file in your home directory.
   - Add the following configuration:

   ```ini
   [pypi]
   username = __token__
   password = pypi-Your-API-Token
   ```

   Replace `pypi-Your-API-Token` with your actual API token.

   *Note*: Ensure this file is kept secure, as it contains sensitive information.

---

### **3. Upload Your Package Using Twine**

1. **Build Your Package**:
   - Ensure your package distributions are built and located in the `dist/` directory.

2. **Upload with Twine**:
   - Run the following command:

   ```bash
   twine upload dist/*
   ```

   Twine will use the credentials provided via environment variables or the `.pypirc` file to authenticate and upload your package.

---

**Important Considerations**:

- **Security**: Avoid hardcoding your API token in scripts or code. Use environment variables or configuration files with appropriate permissions.

- **Two-Factor Authentication (2FA)**: If your PyPI account has 2FA enabled, API tokens are the recommended method for uploading packages, as username/password authentication is not supported in this scenario. citeturn0search6

- **Windows Users**: When pasting the API token in Command Prompt or PowerShell, standard paste shortcuts might not work. Use the "Edit > Paste" menu option or enable "Use Ctrl+Shift+C/V as Copy/Paste" in the terminal properties. citeturn0search9

By following these steps, you can securely and efficiently upload your Python packages to PyPI using Twine with an API token. 