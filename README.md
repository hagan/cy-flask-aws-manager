# cy-flask-aws-manager
React/Flask code for the frontend/backend sections of our aws manager vice app.

### SETUP INSTRUCTIONS

Setup project/clone
$ cd ~/projects/<main project dir>
$ git clone git@github.com:hagan/cy-flask-aws-manager.git
$ cd ~/projects/<main project dir>/cy-flask-aws-manager

Make sure python3 and poetry are available

$ sudo apt install python3 python3-poetry
 If you don't need python2, run:
$ sudo apt install python-is-python3
$ poetry install
$ poetry env info -p

## To build project
$ cd ~/projects/<main project dir>/cy-flask-aws-manager
$ nvm use stable & npm install
$ NODE_ENV=development webpack --progress --color && npm run flask-static-digest
$ poetry build

Should output a file: ./dist/awsmgr-?.?.?-py3-none-any.whl