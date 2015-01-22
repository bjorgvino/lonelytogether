lonelytogether
==============

Let's be lonely together!

Installation
------------

Install virtualenv, virtualenvwrapper and (optionally) autoenv.

    pip install virtualenv virtualenvwrapper autoenv

Autoenv might need to be activated in your shell. Add the following to `.bash_profile`

    source /usr/local/bin/activate.sh

Create a virtualenv called 'lonelytogether'. You might need to configure `virtualenvwrapper` in your shell profile for the `mkvirtualenv` command to work. See: [virtualenvwrapper installation guide](http://virtualenvwrapper.readthedocs.org/en/latest/install.html#shell-startup-file)

    mkvirtualenv lonelytogether

Install dependencies.

    pip install -r requirements.txt

Start server.

    python flask_server.py

Testing
-------

TODO