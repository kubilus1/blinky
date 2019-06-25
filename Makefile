packages: dist/blinky.pex dist/blinky.exe

dist/blinky.pex: dist
	#python3 -m pip wheel -w . .
	#pex --python=python3 -f $$PWD -r all_reqs.txt . -e blinky.blinky -o $@
	docker run -w /src --rm -it -v `pwd`:/src ubuntu /bin/bash -c "./setup.sh && pex -f . -v --python=python3 -r all_reqs.txt --build . -o $@ -e blinky.blinky"
	#docker run -w /src --rm -it -v `pwd`:/src ubuntu /bin/bash -c "./setup.sh && python3 -m pip wheel -w . . && pex -f . -v --python=python3 -r all_reqs.txt . -o $@ -e blinky.blinky"

dist/blinky.exe: dist
	docker run --rm -it -v `pwd`:/src cdrx/pyinstaller-windows:python3 "python setup.py install && pyinstaller --clean --workpath /tmp *.spec"

dist:
	mkdir $@

clean:
	-rm blinky.pex
	-rm *.whl
	-rm -rf build
	-rm -rf dist
