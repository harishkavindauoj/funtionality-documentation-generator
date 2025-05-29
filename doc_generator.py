import os
import glob
from dotenv import load_dotenv
from parser import extract_functions_and_docs

import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-pro")

genai.configure(api_key=GEMINI_API_KEY)


def generate_doc(code_snippet: str) -> str:
    """Generate documentation for a code snippet using Gemini AI."""
    with open("prompt_template.txt") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(code=code_snippet)

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    return response.text.strip()


def main(crud_dir="crud", output_dir="crud_docs"):
    """
    Main function to process CRUD files and generate documentation.

    Args:
        crud_dir (str): Directory containing CRUD Python files
        output_dir (str): Directory to save generated documentation
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    crud_path = os.path.join(base_dir, crud_dir)
    output_path = os.path.join(base_dir, output_dir)

    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    # Find all .py files in the CRUD directory
    crud_files = glob.glob(os.path.join(crud_path, "*.py"))

    if not crud_files:
        print(f"No Python files found in {crud_path}")
        return

    print(f"Found {len(crud_files)} Python files to process...")

    for crud_file in crud_files:
        filename = os.path.basename(crud_file).replace(".py", "")
        output_file = os.path.join(output_path, f"{filename}_doc.md")

        print(f"Processing {crud_file}...")

        try:
            functions = extract_functions_and_docs(crud_file)

            if not functions:
                print(f"No functions found in {crud_file}")
                continue

            with open(output_file, "w", encoding='utf-8') as f:
                f.write(f"# Documentation for {filename}.py\n\n")

                for func in functions:
                    print(f"  Generating docs for function: {func['name']}")
                    doc = generate_doc(func["code"])
                    f.write(f"## Function: `{func['name']}`\n\n")
                    f.write(doc + "\n\n---\n\n")

            print(f"Documentation saved to {output_file}")

        except Exception as e:
            print(f"Error processing {crud_file}: {str(e)}")
            continue

    print("Documentation generation complete!")


if __name__ == "__main__":
    main()