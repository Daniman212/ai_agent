import os
from google.genai import types

def write_file(working_directory, file_path, content):
    """
    Write (or overwrite) a file inside the working_directory.
    Returns a success or error string.
    """
    try:
        abs_working = os.path.abspath(working_directory)
        abs_target = os.path.abspath(os.path.join(working_directory, file_path))

        # Ensure target stays inside working_directory
        if os.path.commonpath([abs_target, abs_working]) != abs_working:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # Ensure parent directories exist
        os.makedirs(os.path.dirname(abs_target), exist_ok=True)

        # Write content to file
        with open(abs_target, "w", encoding="utf-8", errors="replace") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {e}"


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes (or overwrites) a file with provided content, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The full string content to write into the file.",
            ),
        },
    ),
)