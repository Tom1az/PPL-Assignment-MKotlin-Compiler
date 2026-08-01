# MKotlin compiler - convenience wrapper around run.py
PY ?= python3

.PHONY: check setup build clean test-lexer test-parser test-ast test-checker test-codegen test

check:
	$(PY) run.py check

setup:
	$(PY) run.py setup

build:
	$(PY) run.py build

test-lexer:
	$(PY) run.py test-lexer

test-parser:
	$(PY) run.py test-parser

test-ast:
	$(PY) run.py test-ast

test-checker:
	$(PY) run.py test-checker

test-codegen:
	$(PY) run.py test-codegen

test: test-lexer test-parser test-ast test-checker test-codegen

clean:
	$(PY) run.py clean
