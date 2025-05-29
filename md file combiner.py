import os
import glob


def combine_markdown_files(input_folder, output_file):
    """
    Combine all .md files in a folder into a single Markdown file
    formatted for clean and professional PDF conversion.
    """
    md_files = glob.glob(os.path.join(input_folder, '*.md'))

    if not md_files:
        print(f"[ERROR] No .md files found in: {input_folder}")
        return

    # Sort files alphabetically for consistent order
    md_files.sort()

    print(f"\nFound {len(md_files)} Markdown files:")
    for file in md_files:
        print(f" - {os.path.basename(file)}")

    combined_content = "# Project: CRUD Functionality Documentation\n\n"

    for index, md_file in enumerate(md_files):
        try:
            filename = os.path.basename(md_file)
            title = filename.replace("_", " ").replace(".md", "").title()

            print(f"Processing: {filename}")

            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Add a top-level header for each file
            combined_content += f"\n\n# {title}\n\n"
            combined_content += content

            # Add a clean separator for page breaks in PDF
            if index < len(md_files) - 1:
                combined_content += "\n\n---\n\n\\newpage\n\n"

        except Exception as e:
            print(f"[ERROR] Could not process {md_file}: {e}")
            combined_content += f"\n\n## Error processing {filename}\n{str(e)}\n\n"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_content)

        print(f"\n Combined documentation saved to: {output_file}")
        print("\n Next Steps:")
        print(f"1. Convert to PDF via Pandoc:\n   pandoc {output_file} -o output.pdf")
        print("2. Or upload to an online markdown-to-PDF converter like:")
        print("   - https://www.markdowntopdf.com/")
        print("   - https://dillinger.io/")
        print("   - https://stackedit.io/")

    except Exception as e:
        print(f"[ERROR] Could not write to file: {e}")


if __name__ == "__main__":
    input_folder = "crud_docs"
    output_file = "combined_crud_docs.md"

    if not os.path.exists(input_folder):
        print(f"[ERROR] Input folder does not exist: {input_folder}")
    else:
        combine_markdown_files(input_folder, output_file)
