# calculator/main.py
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import sys

# Import just the schema (not executing the function yet)
from functions.get_files_info import schema_get_files_info

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Hardcode working directory on the app side (not exposed to LLM)
WORKING_DIR = "calculator"

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
""".strip()

# ---- CLI args (keeps your earlier behavior) ----
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

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

# ---- NEW: Tooling (available function declarations) ----
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

# ---- Call model with tools + system instruction ----
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt,
    ),
)

# ---- Output: prefer function call plan if present ----
if getattr(response, "function_calls", None):
    # The assignment asks us to print the planned call name + args
    for fc in response.function_calls:
        print(f'Calling function: {fc.name}({fc.args})')
else:
    # Otherwise, just show normal text
    print(response.text)

if verbose:
    print(f'User prompt: "{user_prompt}"')
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
