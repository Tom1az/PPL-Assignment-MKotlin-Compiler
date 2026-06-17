#!/usr/bin/env python3
"""MKotlin compiler — project entrypoint.

Usage:
    python3 run.py check          Verify required tools are installed
    python3 run.py setup          Create venv and install dependencies
    python3 run.py build          Generate the ANTLR lexer/parser/visitor
    python3 run.py test-lexer     Run lexer tests
    python3 run.py test-parser    Run parser tests
    python3 run.py test-ast       Run AST-generation tests
    python3 run.py test-checker   Run static-checker tests
    python3 run.py test-codegen   Run code-generation tests
    python3 run.py clean          Remove generated/build artifacts
"""

import os
import sys
import glob
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
GRAMMAR_DIR = os.path.join(ROOT, "src", "grammar")
GRAMMAR_FILE = os.path.join(GRAMMAR_DIR, "MKotlin.g4")
EXTERNAL_DIR = os.path.join(ROOT, "external")
ANTLR_JAR_GLOB = os.path.join(EXTERNAL_DIR, "antlr-*-complete.jar")
VENV_DIR = os.path.join(ROOT, "venv")


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def _find_antlr_jar():
    matches = sorted(glob.glob(ANTLR_JAR_GLOB))
    return matches[-1] if matches else None


def _run(cmd, **kw):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, **kw)


def _which(name):
    return shutil.which(name)


# --------------------------------------------------------------------------- #
#  Commands                                                                   #
# --------------------------------------------------------------------------- #
def cmd_check():
    ok = True

    py = sys.version_info
    print(f"Python: {py.major}.{py.minor}.{py.micro}", "OK" if py >= (3, 8) else "NEED >= 3.8")
    if py < (3, 8):
        ok = False

    java = _which("java")
    print(f"Java:   {'found at ' + java if java else 'NOT FOUND (install a JRE 8+)'}")
    if not java:
        ok = False

    jar = _find_antlr_jar()
    print(f"ANTLR:  {'found ' + os.path.basename(jar) if jar else 'NOT FOUND in external/ (place antlr-4.13.2-complete.jar there)'}")
    if not jar:
        ok = False

    try:
        import antlr4  # noqa: F401
        print("antlr4-python3-runtime: installed")
    except Exception:
        print("antlr4-python3-runtime: NOT installed (run: python3 run.py setup)")

    try:
        import pytest  # noqa: F401
        print("pytest: installed")
    except Exception:
        print("pytest: NOT installed (run: python3 run.py setup)")

    print("\nAll required tools present." if ok else "\nSome required tools are missing.")
    return 0 if ok else 1


def cmd_setup():
    if not os.path.isdir(VENV_DIR):
        _run([sys.executable, "-m", "venv", VENV_DIR])
    pip = os.path.join(VENV_DIR, "bin", "pip")
    if not os.path.exists(pip):
        pip = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    _run([pip, "install", "-r", os.path.join(ROOT, "requirements.txt")])
    print("\nSetup complete. Activate the venv, then `python3 run.py build`.")
    return 0


def cmd_build():
    jar = _find_antlr_jar()
    if not jar:
        print("ERROR: ANTLR jar not found in external/. See `python3 run.py check`.")
        return 1
    if not _which("java"):
        print("ERROR: java not found on PATH.")
        return 1
    # Run from inside the grammar directory so the generated files land in
    # src/grammar/ directly (the @lexer::header package path would otherwise
    # cause ANTLR to nest them under src/grammar/src/grammar/).
    cmd = [
        "java", "-jar", jar,
        "-Dlanguage=Python3",
        "-visitor", "-no-listener",
        "MKotlin.g4",
    ]
    res = _run(cmd, cwd=GRAMMAR_DIR)
    if res.returncode == 0:
        print("Grammar built: MKotlinLexer/Parser/Visitor generated in src/grammar/.")
    return res.returncode


def _pytest(path):
    try:
        import pytest
    except Exception:
        print("pytest not installed. Run `python3 run.py setup` (and activate the venv).")
        return 1
    return pytest.main(["-q", path, "--rootdir", ROOT])


def cmd_test_lexer():
    return _pytest(os.path.join(ROOT, "tests", "test_lexer.py"))


def cmd_test_parser():
    return _pytest(os.path.join(ROOT, "tests", "test_parser.py"))


def cmd_test_ast():
    return _pytest(os.path.join(ROOT, "tests", "test_ast_gen.py"))


def cmd_test_checker():
    return _pytest(os.path.join(ROOT, "tests", "test_checker.py"))


def cmd_test_codegen():
    return _pytest(os.path.join(ROOT, "tests", "test_codegen.py"))


def cmd_clean():
    # Generated ANTLR files
    patterns = [
        "MKotlinLexer.py", "MKotlinParser.py", "MKotlinVisitor.py",
        "MKotlin*.interp", "MKotlin*.tokens", "MKotlinLexer.tokens",
    ]
    for pat in patterns:
        for f in glob.glob(os.path.join(GRAMMAR_DIR, pat)):
            os.remove(f)
            print("removed", os.path.relpath(f, ROOT))
    # __pycache__ and .class / .j artifacts
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if "__pycache__" in dirnames:
            shutil.rmtree(os.path.join(dirpath, "__pycache__"), ignore_errors=True)
        for f in filenames:
            if f.endswith((".class", ".j")):
                os.remove(os.path.join(dirpath, f))
    print("Clean complete.")
    return 0


COMMANDS = {
    "check": cmd_check,
    "setup": cmd_setup,
    "build": cmd_build,
    "test-lexer": cmd_test_lexer,
    "test-parser": cmd_test_parser,
    "test-ast": cmd_test_ast,
    "test-checker": cmd_test_checker,
    "test-codegen": cmd_test_codegen,
    "clean": cmd_clean,
}


def main(argv):
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(__doc__)
        return 1
    return COMMANDS[argv[1]]() or 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
