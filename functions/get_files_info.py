import os
from google.genai import types

def get_files_info(working_directory, directory="."):
    """
    List contents of a directory relative to working_directory.
    Returns a string describing files and subdirectories.
    """
    try:
        # Build the full path
        full_path = os.path.join(working_directory, directory)

        # Resolve to absolute paths for safety
        abs_working = os.path.abspath(working_directory)
        abs_target = os.path.abspath(full_path)

        # Ensure the target directory stays inside working_directory
        if not abs_target.startswith(abs_working):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Check if target is actually a directory
        if not os.path.isdir(abs_target):
            return f'Error: "{directory}" is not a directory'

        # Collect entries
        lines = []
        for entry in os.listdir(abs_target):
            entry_path = os.path.join(abs_target, entry)
            try:
                size = os.path.getsize(entry_path)
                is_dir = os.path.isdir(entry_path)
                lines.append(f"- {entry}: file_size={size} bytes, is_dir={is_dir}")
            except Exception as e:
                lines.append(f"- {entry}: Error reading file info ({e})")

        # Return joined string
        return "\n".join(lines)

    except Exception as e:
        return f"Error: {e}"
    
    
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The directory to list files from, relative to the working directory. "
                    "If not provided, lists files in the working directory itself."
                ),
            ),
        },
    ),
)