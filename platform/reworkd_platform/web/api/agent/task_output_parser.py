"""任務輸出解析器 — 將 LLM 回傳的任務列表字串解析為結構化資料。"""

import ast
import re
from typing import List

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseOutputParser


class TaskOutputParser(BaseOutputParser[List[str]]):
    """
    Extension of LangChain's BaseOutputParser
    Responsible for parsing task creation output into a list of task strings
    """

    completed_tasks: List[str] = []

    def __init__(self, *, completed_tasks: List[str]):
        super().__init__()
        self.completed_tasks = completed_tasks

    def parse(self, text: str) -> List[str]:
        try:
            array_str = extract_array(text)
            all_tasks = [
                remove_prefix(task) for task in array_str if real_tasks_filter(task)
            ]
            return [task for task in all_tasks if task not in self.completed_tasks]
        except Exception as e:
            msg = f"Failed to parse tasks from completion '{text}'. Exception: {e}"
            raise OutputParserException(msg)

    def get_format_instructions(self) -> str:
        return """
        The response should be a JSON array of strings. Example:

        ["Search the web for NBA news", "Write some code to build a web scraper"]

        This should be parsable by json.loads()
        """


def extract_array(input_str: str) -> List[str]:
    regex = (
        r"\[\s*\]|"  # Empty array check
        r"(\[(?:\s*(?:\"(?:[^\"\\]|\\.)*\"|\'(?:[^\'\\]|\\.)*\')\s*,?)*\s*\])"
    )
    match = re.search(regex, input_str)
    if match is not None:
        return ast.literal_eval(match[0])

    # Fallback：LLM（如 llama-3.1-8b）偶發以花括號 {…} 輸出字串清單（缺 key 的 object），
    # 例如 {"任務一","任務二"}。僅在內容全為引號字串（無 key-value 冒號）時視為任務清單。
    brace_regex = r"\{(\s*(?:\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')\s*,?)*\s*\}"
    brace_match = re.search(brace_regex, input_str)
    if brace_match is not None:
        quoted = re.findall(r"\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'", brace_match[0])
        return [ast.literal_eval(q) for q in quoted]

    return handle_multiline_string(input_str)


def handle_multiline_string(input_str: str) -> List[str]:
    # Handle multiline string as a list
    processed_lines = [
        re.sub(r".*?(\d+\..+)", r"\1", line).strip()
        for line in input_str.split("\n")
        if line.strip() != ""
    ]

    # Check if there is at least one line that starts with a digit and a period
    if any(re.match(r"\d+\..+", line) for line in processed_lines):
        return processed_lines
    else:
        raise RuntimeError(f"Failed to extract array from {input_str}")


def remove_prefix(input_str: str) -> str:
    prefix_pattern = (
        r"^(Task\s*\d*\.\s*|Task\s*\d*[-:]?\s*|Step\s*\d*["
        r"-:]?\s*|Step\s*[-:]?\s*|\d+\.\s*|\d+\s*[-:]?\s*|^\.\s*|^\.*)"
    )
    return re.sub(prefix_pattern, "", input_str, flags=re.IGNORECASE)


def real_tasks_filter(input_str: str) -> bool:
    no_task_regex = (
        r"^No( (new|further|additional|extra|other))? tasks? (is )?("
        r"required|needed|added|created|inputted).*"
    )
    task_complete_regex = r"^Task (complete|completed|finished|done|over|success).*"
    do_nothing_regex = r"^(\s*|Do nothing(\s.*)?)$"

    return (
        not re.search(no_task_regex, input_str, re.IGNORECASE)
        and not re.search(task_complete_regex, input_str, re.IGNORECASE)
        and not re.search(do_nothing_regex, input_str, re.IGNORECASE)
    )
