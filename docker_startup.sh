#!/bin/bash
cd workspace
python3 -m pip install --upgrade pip
pip install -r ./requirements.txt
chmod +x ./wait-for-it.sh
bash ./wait-for-it.sh db:3306 -t 60 -- alembic upgrade head