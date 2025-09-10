import os
from .config import MAX_READ_CHARS
from google.genai import types

def get_file_content(working_directory, file_path):
    """
    Read a file located within working_directory (sandbox).
    Returns file contents as a string. On any problem, returns an
    error string prefixed with 'Error:'.
    """
    try:
        # Build absolute paths safely
        abs_working = os.path.abspath(working_directory)
        abs_target = os.path.abspath(os.path.join(working_directory, file_path))

        # Ensure target stays within the working directory (no path traversal)
        # commonpath is more robust than startswith for this use case
        if os.path.commonpath([abs_target, abs_working]) != abs_working:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Ensure it's a regular file
        if not os.path.isfile(abs_target):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # Read the file; replace undecodable bytes to avoid exceptions
        with open(abs_target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Truncate if too long
        if len(content) > MAX_READ_CHARS:
            suffix = f'[...File "{file_path}" truncated at {MAX_READ_CHARS} characters]'
            return content[:MAX_READ_CHARS] + suffix

        return content

    except Exception as e:
        return f"Error: {e}"
    

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the contents of a file (truncated for very large files), constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to read, relative to the working directory.",
            ),
        },
    ),
)
