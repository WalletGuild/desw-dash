build:
	python setup.py build

install:
	python setup.py install
    python install.py

clean:
	rm -rf .cache build dist *.egg-info test/__pycache__
	rm -rf test/*.pyc *.egg *~ *pyc test/*~ .eggs

purge:
    rm /etc/tapp/desw.ini
