PY_SOURCES = $(shell find compilationmetrics/ -type f -name '*.py')

wrap_compiler: compilationmetrics/collecting/measure $(PY_SOURCES)
	bin/package_compiler_wrapper $@

compilationmetrics/collecting/measure: compilationmetrics/collecting/measure.cpp
	$(CXX) -Os -o $@ $^

.PHONY: clean
clean:
	rm -f wrap_compiler compilationmetrics/collecting/measure
