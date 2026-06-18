# MKotlin compiler - convenience wrapper around run.py
ROOT := $(CURDIR)
VENV_DIR := $(ROOT)/venv
PY ?= python3

ifeq ($(OS),Windows_NT)
VENV_PYTHON := $(VENV_DIR)/Scripts/python.exe
else
VENV_PYTHON := $(VENV_DIR)/bin/python
endif

.PHONY: check setup build clean test-lexer test-parser test-ast test-checker test-codegen test

check:
	$(PY) run.py check

setup:
	$(PY) run.py setup

build:
	$(PY) run.py build

test-lexer test-parser test-ast test-checker test-codegen:
	$(PY) run.py $@

test: test-lexer test-parser test-ast test-checker test-codegen

clean:
	$(PY) run.py clean
