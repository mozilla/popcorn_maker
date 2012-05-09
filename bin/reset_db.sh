#!/bin/bash

python manage.py reset_db --router=default
python manage.py syncdb
python manage.py loaddata fixtures/test/category.json
python manage.py loaddata fixtures/test/template.json
