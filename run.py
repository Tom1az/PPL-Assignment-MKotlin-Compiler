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

import glob
import os
import re
import shutil
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
GRAMMAR_DIR = os.path.join(ROOT, "src", "grammar")
EXTERNAL_DIR = os.path.join(ROOT, "external")
VENV_DIR = os.path.join(ROOT, "venv")

ANTLR_VERSION = "4.13.2"
ANTLR_JAR = f"antlr-{ANTLR_VERSION}-complete.jar"
ANTLR_URL = f"https://www.antlr.org/download/{ANTLR_JAR}"
ANTLR_JAR_GLOB = os.path.join(EXTERNAL_DIR, "antlr-*-complete.jar")

PREFERRED_PYTHON_MINOR = 12


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


def _venv_python():
    if sys.platform == "win32":
        path = os.path.join(VENV_DIR, "Scripts", "python.exe")
        return path if os.path.isfile(path) else None
    for name in ("python", "python3"):
        path = os.path.join(VENV_DIR, "bin", name)
        if os.path.isfile(path):
            return path
    return None


def _venv_pip():
    if sys.platform == "win32":
        path = os.path.join(VENV_DIR, "Scripts", "pip.exe")
        return path if os.path.isfile(path) else None
    return os.path.join(VENV_DIR, "bin", "pip")


def _parse_python_minor(version_text):
    match = re.search(r"3\.(\d+)", version_text)
    return int(match.group(1)) if match else None


def _python_cmd_ok(cmd):
    try:
        result = subprocess.run(
            cmd + ["--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode != 0:
        return False
    minor = _parse_python_minor(result.stdout + result.stderr)
    return minor is not None and minor >= 8


def _find_python():
    """Return a command prefix for a Python 3.8+ executable."""
    candidates = [
        [f"python{PREFERRED_PYTHON_MINOR}"],
        ["python3"],
        ["python"],
    ]
    if sys.platform == "win32":
        candidates[:0] = [["py", f"-{PREFERRED_PYTHON_MINOR}"], ["py", "-3"]]

    for cmd in candidates:
        if cmd[0] != "py" and not _which(cmd[0]):
            continue
        if _python_cmd_ok(cmd):
            return cmd
    return None


def _download_antlr_if_needed():
    os.makedirs(EXTERNAL_DIR, exist_ok=True)
    dest = os.path.join(EXTERNAL_DIR, ANTLR_JAR)
    if os.path.isfile(dest):
        return dest
    print(f"Downloading ANTLR {ANTLR_VERSION}...")
    try:
        urllib.request.urlretrieve(ANTLR_URL, dest)
    except Exception as exc:
        print(f"ERROR: failed to download ANTLR: {exc}")
        return None
    print(f"ANTLR saved to {dest}")
    return dest


def _grammar_built():
    return os.path.isfile(os.path.join(GRAMMAR_DIR, "MKotlinLexer.py"))


def _ensure_build():
    if _grammar_built():
        return 0
    print("Grammar not built yet. Running build...")
    return cmd_build()


def _run_pytest(test_path):
    venv_py = _venv_python()
    if not venv_py:
        print("Virtual environment not found. Run `python3 run.py setup` first.")
        return 1

    pip_check = subprocess.run(
        [venv_py, "-m", "pytest", "--version"],
        capture_output=True,
        text=True,
    )
    if pip_check.returncode != 0:
        print("pytest is not installed in the project virtual environment.")
        print("Run `python3 run.py setup` first.")
        if shutil.which("pytest"):
            print(
                "Note: `pytest` on PATH may belong to a different Python. "
                "Always run tests via `python3 run.py test-*`."
            )
            print(f"  {venv_py} -m pytest --version")
        return 1

    build_rc = _ensure_build()
    if build_rc != 0:
        return build_rc

    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT
    cmd = [venv_py, "-m", "pytest", "-q", test_path, "--rootdir", ROOT]
    return _run(cmd, cwd=ROOT, env=env).returncode


# --------------------------------------------------------------------------- #
#  Commands                                                                   #
# --------------------------------------------------------------------------- #
def cmd_check():
    ok = True

    java = _which("java")
    print(f"Java:   {'found at ' + java if java else 'NOT FOUND (install a JRE 8+)'}")
    if not java:
        ok = False

    py_cmd = _find_python()
    if py_cmd:
        print(f"Python: found ({' '.join(py_cmd)})")
    else:
        print("Python: NOT FOUND (need Python 3.8+)")
        ok = False

    jar = _find_antlr_jar()
    if jar:
        print(f"ANTLR:  found {os.path.basename(jar)}")
    else:
        print(f"ANTLR:  NOT FOUND (run: python3 run.py setup)")
        ok = False

    venv_py = _venv_python()
    if not venv_py:
        print("venv:   NOT created (run: python3 run.py setup)")
    else:
        print(f"venv:   found at {VENV_DIR}")
        dep_check = subprocess.run(
            [venv_py, "-c", "import antlr4, pytest"],
            capture_output=True,
            text=True,
        )
        if dep_check.returncode == 0:
            print("deps:   antlr4-python3-runtime and pytest installed in venv")
        else:
            print("deps:   NOT installed in venv (run: python3 run.py setup)")

    print("\nAll required tools present." if ok else "\nSome required tools are missing.")
    return 0 if ok else 1


def cmd_setup():
    if not _which("java"):
        print("ERROR: java not found on PATH.")
        return 1

    py_cmd = _find_python()
    if not py_cmd:
        print("ERROR: Python 3.8+ not found.")
        if sys.platform == "win32":
            print("On Windows, install Python from https://www.python.org/downloads/")
            print("or ensure `py -3.12` / `python` is available.")
        return 1

    print(f"Using {' '.join(py_cmd)} to create the virtual environment.")

    if not os.path.isdir(VENV_DIR):
        res = _run(py_cmd + ["-m", "venv", VENV_DIR])
        if res.returncode != 0:
            return res.returncode

    if not _download_antlr_if_needed():
        return 1

    pip = _venv_pip()
    if not os.path.isfile(pip):
        print("ERROR: pip not found in the virtual environment.")
        return 1

    res = _run([pip, "install", "--upgrade", "pip"])
    if res.returncode != 0:
        return res.returncode

    res = _run([pip, "install", "-r", os.path.join(ROOT, "requirements.txt")])
    if res.returncode != 0:
        return res.returncode

    print("\nSetup complete. Run `python3 run.py build`, then `python3 run.py test-lexer`.")
    return 0


def cmd_build():
    jar = _find_antlr_jar()
    if not jar:
        jar = _download_antlr_if_needed()
    if not jar:
        print("ERROR: ANTLR jar not found. Run `python3 run.py setup`.")
        return 1
    if not _which("java"):
        print("ERROR: java not found on PATH.")
        return 1
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


def cmd_test_lexer():
    return _run_pytest(os.path.join(ROOT, "tests", "test_lexer.py"))


def cmd_test_parser():
    return _run_pytest(os.path.join(ROOT, "tests", "test_parser.py"))


def cmd_test_ast():
    return _run_pytest(os.path.join(ROOT, "tests", "test_ast_gen.py"))


def cmd_test_checker():
    return _run_pytest(os.path.join(ROOT, "tests", "test_checker.py"))


def cmd_test_codegen():
    return _run_pytest(os.path.join(ROOT, "tests", "test_codegen.py"))


def cmd_clean():
    patterns = [
        "MKotlinLexer.py", "MKotlinParser.py", "MKotlinVisitor.py",
        "MKotlin*.interp", "MKotlin*.tokens", "MKotlinLexer.tokens",
    ]
    for pat in patterns:
        for f in glob.glob(os.path.join(GRAMMAR_DIR, pat)):
            os.remove(f)
            print("removed", os.path.relpath(f, ROOT))
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
