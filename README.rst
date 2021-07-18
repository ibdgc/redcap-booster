To run from project folder::

    pip install -r requirements.txt
    uvicorn main:app --app-dir redcap_booster

To install and run in development environment::

    pip install -e .
    uvicorn redcap_booster.main:app
