# ai_agent/main.py
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import sys

# Schemas (planning)
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file

# Implementations (execution)
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

WORKING_DIR = "calculator"  # sandbox root injected into every tool call

def call_function(function_call_part, verbose=False):
    """
    Dispatch a tool/function call planned by the model.
    Prints per assignment. Injects working_directory.
    Returns a types.Content with a function_response part.
    """
    function_name = function_call_part.name
    fn_args = dict(function_call_part.args or {})
    fn_args["working_directory"] = WORKING_DIR

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    registry = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    fn = registry.get(function_name)
    if fn is None:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    try:
        result_str = fn(**fn_args)
    except Exception as e:
        result_str = f"Error: {e}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result_str},
            )
        ],
    )

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

Your job is to PLAN and CALL functions. Do not ask follow-up questions for these operations—pick sensible defaults and make a function call.

You can perform the following operations (always use paths RELATIVE to the working directory):
- List files and directories           -> get_files_info({'directory': '<relative path or "." >'})
- Read file contents                   -> get_file_content({'file_path': '<relative path>'})
- Execute Python files with arguments  -> run_python_file({'file_path': '<relative path>', 'args': [<optional strings>]})
- Write or overwrite files             -> write_file({'file_path': '<relative path>', 'content': '<string>'})

Rules:
- The working directory is injected by the system; do NOT include it in your arguments.
- If the user asks about repository structure or how something works, you MUST start by calling get_files_info('.') and then call get_file_content on likely files (e.g., 'pkg/render.py', 'main.py') to gather details before answering.
- If the user says “run X” without args, call run_python_file with args=[].
- If the user says “list files” without a path, use directory=".".
- If the user says “read F”, call get_file_content with file_path="F".
- If the user says “write 'TEXT' to F”, call write_file with file_path="F" and content="TEXT".
- Never respond with plain text when one of these tools applies. Prefer making exactly ONE function call per step that best progresses the task.
""".strip()

# ---- CLI args / verbose flag ----
if len(sys.argv) < 2:
    print("Error: Please provide a prompt as a command-line argument.")
    sys.exit(1)

args = sys.argv[1:]
verbose = False
if "--verbose" in args:
    verbose = True
    args.remove("--verbose")

if not args:
    print("Error: Please provide a prompt as a command-line argument.")
    sys.exit(1)

user_prompt = " ".join(args)

# Conversation starts with the user message
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

# Tool declarations exposed to the model
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

MAX_STEPS = 20

try:
    for step in range(MAX_STEPS):
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            ),
        )

        # Always record model candidate content into conversation
        if getattr(response, "candidates", None):
            for candidate in response.candidates:
                if getattr(candidate, "content", None):
                    messages.append(candidate.content)

        # PRIORITIZE tool use: if the model planned function calls, execute them first.
        if getattr(response, "function_calls", None):
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, verbose=verbose)

                # Validate structure per assignment
                try:
                    _ = function_call_result.parts[0].function_response.response
                except Exception:
                    raise RuntimeError("Fatal: function call result missing function_response.response")

                if verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")

                # Feed tool result back as a 'user' message so the model can take the next step
                messages.append(types.Content(role="user", parts=function_call_result.parts))

            # After executing tools, continue the loop to let model react.
            continue

        # If no tool calls were planned, then consider textual completion as final.
        if response.text:
            print("Final response:")
            print(response.text)
            break

        # No function calls and no text -> gently nudge once, then retry
        if step == 0:
            messages.append(types.Content(
                role="user",
                parts=[types.Part(text="Plan at least one function call now (start with get_files_info('.') then get_file_content on relevant files).")]
            ))
            continue

        print("Final response:")
        print("(No additional output from model.)")
        break

    else:
        print("Final response:")
        print("(Stopped after max iterations without a final answer.)")

except Exception as e:
    print(f"Error: {e}")

if verbose:
    print(f'User prompt: "{user_prompt}"')
    try:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    except Exception:
        pass
