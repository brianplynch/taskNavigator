import os
import sys
import subprocess
import re
from pathlib import Path
from typing import Callable


OPEN_FILE_FUNCTION = Callable[[str], None]


def no_win32gui():
    raise OSError("win32gui is not available. This may affect the functionality of the script.")

if sys.platform == "win32":
    import win32gui
else:
    # If win32gui is not available, we can still run the script but without the window title functionality
    win32gui=no_win32gui

def non_cp1252_chars_removed(text: str) -> str:
    """ensure no non-cp1252 encodable characters"""
    safe_text = re.sub("[^\\x00-\\xff]", "_", text)
    return safe_text


def open_file(filename) -> None:
    open_from: dict[str, OPEN_FILE_FUNCTION] = {
        "win32": open_file_vscode_windows,
        "linux": open_file_vscode_linux,
    }

    if sys.platform not in open_from:
        raise NotImplementedError(f"{sys.platform} file-system interface is not implemented")
    open_function = open_from[sys.platform]
    open_function(filename)


def open_file_default_windows(filename: str) -> None:
    if sys.platform != "win32":
        raise NotImplementedError("Windows-based function called in a non-Windows environment")
    try:
        os.startfile(filename)
    except FileNotFoundError as err:
        raise err

def open_file_vscode_windows(filename: str) -> None:
    if sys.platform != "win32":
        raise NotImplementedError("Windows-based function called in a non-Windows environment")
    try:
        subprocess.call(["code", filename], shell=True)
    except Exception as er:
        open_file_default_windows(filename)

def open_file_vscode_linux(filename: str) -> None:
    if sys.platform != "linux":
        raise NotImplementedError("Linux-based function called in a non-linux environment")
    try:
        subprocess.call(["code", filename])
    except Exception as err:
        open_file_default_prog_linux(filename)


def open_file_default_prog_linux(filename: str) -> None:
    subprocess.call(["xdg-open", filename])


def get_file_paths_by_ext(root_path: str, file_extension: str) -> list[str]:
    file_names = os.listdir(root_path)
    file_names_with_ext = list(filter(lambda s: s.endswith(file_extension), file_names))
    file_paths_with_ext = list(map(os.path.sep.join, list(zip([root_path] * len(file_names_with_ext), file_names_with_ext))))
    return file_paths_with_ext


def get_filenames_in_path(root_path: str, file_extension: str="") -> list[str]:
    paths = get_file_paths_by_ext(root_path, file_extension)
    return [Path(p).stem for p in paths]


def get_file_contents(file_path: str) -> str:
    """
    file_path: str, file path of a text file to be read
    returns text of the file where unreadable characters (i.e. not ASCII) are ignored
    """
    if not Path(file_path).exists():
        return ""
    
    with open(file_path, "r", encoding="utf-8") as file_object:
        try:
            file_contents = file_object.read()
        except UnicodeDecodeError:
            with open(file_path, "rb") as file_binary_object:
                file_contents = file_binary_object.read().decode("ascii", "ignore")
    return file_contents


def get_md_references(md_text: str, contains_reference_pattern: str) -> list[str]:
    """Extract a list of all wiki style markdown links e.g. [[file]]"""
    md_note_reference_pattern = re.compile("(?<=\\[\\[).*?(?=\\]\\])")
    md_note_references = re.findall(md_note_reference_pattern, md_text)
    activity_references = list(filter(lambda s: contains_reference_pattern in s, md_note_references))
    return activity_references


def get_all_open_window_titles() -> list[str]:
    winEnumHandler = lambda hwnd, list_to_append: list_to_append.append(win32gui.GetWindowText( hwnd) ) if win32gui.IsWindowVisible( hwnd ) else None
    all_open_window_titles = list()
    win32gui.EnumWindows(winEnumHandler, all_open_window_titles)
    return all_open_window_titles


def get_opened_notes() -> list[str]:
    all_open_window_titles = get_all_open_window_titles()
    notes_windows = filter(lambda s: ".md" in s, all_open_window_titles)

    opened_notes = [note_title[:note_title.find(".md")] for note_title in notes_windows]
    return opened_notes


def output_to_file(root_folder: str, filename: str, contents: str) -> None:
    file_path = Path(root_folder).joinpath(f"{filename}")
    open(file_path, "a").close()
    with open(file_path, "w", encoding="utf8") as output_file:
        output_file.write(contents)
    open_file(file_path)


def get_open_window_titles() -> list[str]:
    """
    Get the titles of all open windows.
    """
    if os.name == 'nt':
        return get_open_window_titles_windows()
    elif os.name == 'posix':
        if os.uname().sysname == 'Linux':
            return get_open_window_titles_linux()
    elif os.name == 'mac':
        return get_open_windows_titles_mac()
    else:
        raise NotImplementedError("Unsupported operating system")
    

def get_open_windows_titles_mac() -> list[str]:
    raise NotImplementedError("MacOS is not supported yet")


def get_open_window_titles_linux() -> list[str]:
    try:
        output = subprocess.check_output(["wmctrl", "-l"])
    except FileNotFoundError as er:
        raise er("wmctrl is not installed. Please install it using: sudo apt-get install wmctrl")
    except subprocess.CalledProcessError as er:
        raise er("Error executing wmctrl")
    
    output = output.decode("utf-8")
    lines = output.strip().split("\n")
    windows = []
    for line in lines:
        parts = line.split(maxsplit=4)
        if len(parts) > 3:
            window_id, _, _, title = parts[0], parts[1], parts[2], parts[3]
            windows.append(title)
    return windows
    

def get_open_window_titles_windows() -> list[str]:
    winEnumHandler = lambda hwnd, list_to_append: list_to_append.append(win32gui.GetWindowText( hwnd) ) if win32gui.IsWindowVisible( hwnd ) else None
    all_open_window_titles = list()
    win32gui.EnumWindows(winEnumHandler, all_open_window_titles)
    return all_open_window_titles

def open_folder(vault: str, folder_name: str) -> None:
    folder_path = Path(vault).joinpath(folder_name)
    if not folder_path.exists():
        folder_path.mkdir()

    if os.name == "nt":
        os.startfile(folder_path)
    elif os.name == 'posix':
        # Open a local file (like a PDF, image, or text file)
        subprocess.run(["xdg-open", folder_path])

if __name__ == "__main__":
    pass
