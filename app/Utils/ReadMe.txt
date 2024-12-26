Create and Activate a Virtual Environment
To create a virtual environment in your project folder:

Windows:

python -m venv venv

Mac/Linux:

python3 -m venv venv
To activate the virtual environment:

Windows:

.\venv\Scripts\activate
Mac/Linux:

source venv/bin/activate
After activating the virtual environment, you can install dependencies from the requirements.txt file:

pip install -r requirements.txt