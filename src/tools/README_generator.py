import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Set, Tuple, Dict

class ReadmeGenerator:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.readme_path = os.path.join(root_dir, "README.md")

    def get_python_files(self) -> Set[str]:
        """Recursively collect all Python files using parallel processing."""
        python_files = set()

        def process_directory(dir_path: str) -> Set[str]:
            local_files = set()
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(".py"):
                        relative_path = os.path.relpath(
                            os.path.join(root, file), self.root_dir
                        )
                        if not relative_path.startswith(
                            "."
                        ) and not relative_path.startswith("__"):
                            local_files.add(relative_path)
            return local_files

        with ThreadPoolExecutor() as executor:
            futures = []
            for item in os.listdir(self.root_dir):
                item_path = os.path.join(self.root_dir, item)
                if os.path.isdir(item_path):
                    futures.append(executor.submit(process_directory, item_path))

            for future in futures:
                python_files.update(future.result())

        return python_files

    def parse_readme_sections(self) -> Tuple[Set[str], Set[str], str]:
        """Parse README.md and extract categorized and TODO files."""
        if not os.path.exists(self.readme_path):
            return set(), set(), ""

        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        categorized_files = set(re.findall(r"- ((?:[\w]+/)*[\w]+\.py)", content))
        todo_match = re.search(r"## TODO\n(.*?)(\n## |\Z)", content, re.S)
        todo_files = set(
            re.findall(
                r"- ((?:[\w]+/)*[\w]+\.py)", todo_match.group(1) if todo_match else ""
            )
        )

        return categorized_files, todo_files, content

    def update_todo_section(self, content: str, new_files: Set[str]) -> str:
        """Update the TODO section with new Python files."""
        if not new_files:
            return content

        todo_section = "## TODO\n"
        for file in sorted(new_files):
            todo_section += f"- {file}: # TODO: Add description\n"

        if "## TODO" in content:
            pattern = r"(## TODO\n)(.*?)(\n## |\Z)"
            todo_section = todo_section.replace('\\', '\\\\')
            return re.sub(pattern, f"\\1{todo_section}\\3", content, flags=re.S)

        return f"{content}\n{todo_section}"

    def update_readme(self) -> Dict[str, int]:
        """Update README.md with new Python files and return statistics."""
        python_files = self.get_python_files()
        categorized_files, todo_files, content = self.parse_readme_sections()

        new_files = python_files - categorized_files - todo_files
        if new_files:
            content = self.update_todo_section(content, new_files)
            with open(self.readme_path, "w", encoding="utf-8") as f:
                f.write(content)

        return {
            "total_files": len(python_files),
            "categorized": len(categorized_files),
            "todo": len(todo_files),
            "new": len(new_files),
        }


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    generator = ReadmeGenerator(root_dir)
    stats = generator.update_readme()

    print(
        f"""README.md Update Summary:
Total Python files: {stats['total_files']}
Categorized files: {stats['categorized']}
TODO files: {stats['todo']}
New files added: {stats['new']}"""
    )


if __name__ == "__main__":
    main()