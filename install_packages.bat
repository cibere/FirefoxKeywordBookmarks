@echo OFF
call venv/scripts/activate && pip install --upgrade pip && pip install --upgrade -U -r ./requirements-dev.txt