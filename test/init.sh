#!/bin/sh
python -c 'from beetlapi.database.main import create_db_and_tables as init; init()'
