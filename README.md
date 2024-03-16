# cy-flask-aws-manager : submodule
React/Flask code for the frontend/backend sections of our aws manager vice app.

### Prereqs for building application

pyenv (if compiling from source) -> [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv)

pulumi binary -> [https://www.pulumi.com/docs/install/](https://www.pulumi.com/docs/install/)

#### Python compile from scratch

This project does not require most of these packages, however likely including
all during compile time will reduce issues when pip installing from source.

    ```
    $ sudo apt install -y build-essential git wget curl xz-utils llvm \
        libmysqlclient-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev libssh-dev tcl-dev tk-dev libre2-dev libxslt1-dev \
        libxml2-dev libffi-dev libopenblas-dev gettext libglib2.0-dev \
        libkrb5-dev libass-dev libev-dev libevent-dev libgc-dev libc-dev \
        libidn2-dev libjpeg-turbo8-dev libmpc-dev libmpdec-dev nettle-dev \
        libogg-dev libpng-dev libtiff-dev libpq-dev libopenjp2-7-dev \
        libpcre3-dev libpcre2-dev libsdl1.2-dev liblzma-dev libhdf5-dev \
        llvm-dev libmemcached-dev libz-dev libssl-dev libncursesw5-dev \
        libncurses5-dev libgdbm-dev libacl1-dev libpango1.0-0 libcairo2-dev \
        libjpeg8-dev libtiff5-dev

    $ pyenv install 3.11.8
    $ cd <project>/src/flask
    $ pyenv virtualenv 3.11.8 cam-flask-env
    $ pyenv local cam-flask-env
    $ pip install poetry
    ## verify poetry sees your virtual env "cam-flask-emv"
    $ poetry env info
    ## Install flask required packages...
    $ poetry install
    ```

#### Python from debian/ubuntu packaging

```
    $ sudo apt install -y python3 python3-poetry python-is-python3
    $ cd <project>/src/flask
    $ poetry install
```

#### Run project inside poetry

```
   $> cd <project>
   $> poetry shell
   $> poetry run awsmgr <commands/flags/etc...>
```

#### Compile project

This creates a whl file and places it into the ./dist folder.
```
    $ cd <project/src/flask>
    $ ./build.sh
```

Note: You may need to recommit this to the repo via git LFS, ideally make version bump to avoid file clashes on git.

#### Troubleshooting

None yet