# run with command in the the directory containing the project:
# pythn rm_migrations_script.py

import os

for root, dirs, files in os.walk(os.getcwd(), topdown=False):
    path = root.split(os.sep)
    if files.__contains__('db.sqlite3'):
        os.remove(os.path.join(root, 'db.sqlite3'))
    if (path.__contains__('migrations')):
        for file in files:
            if file != '__init__.py':
                os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
                
