import os
import subprocess
import sys
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    """
    Execute a Python file within a sandboxed working_directory.
    Returns a formatted string with STDOUT/STDERR and exit info, or an Error:... string.
    """
    try:
        # Resolve paths
        abs_working = os.path.abspath(working_directory)
        abs_target = os.path.abspath(os.path.join(working_directory, file_path))

        # Guard: path traversal / outside sandbox
        if os.path.commonpath([abs_target, abs_working]) != abs_working:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # Guard: file exists
        if not os.path.exists(abs_target):
            return f'Error: File "{file_path}" not found.'

        # Guard: python file
        if not abs_target.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        # Build command: use current Python interpreter
        cmd = [sys.executable, abs_target]
        if args:
            # Ensure args are strings
            cmd.extend([str(a) for a in args])

        # Run process
        completed = subprocess.run(
            cmd,
            cwd=abs_working,
            capture_output=True,
            text=True,
            timeout=30
        )

        stdout = completed.stdout or ""
        stderr = completed.stderr or ""

        if not stdout and not stderr:
            return "No output produced."

        out_lines = []
        out_lines.append("STDOUT:")
        out_lines.append(stdout.rstrip())
        out_lines.append("STDERR:")
        out_lines.append(stderr.rstrip())

        if completed.returncode != 0:
            out_lines.append(f"Process exited with code {completed.returncode}")

        return "\n".join(out_lines)

    except subprocess.TimeoutExpired:
        return 'Error: executing Python file: Process timed out after 30 seconds'
    except Exception as e:
        return f"Error: executing Python file: {e}"
    


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of command-line arguments to pass to the Python file.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
    ),
)
