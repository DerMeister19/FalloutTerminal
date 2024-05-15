import os
import curses
import time
import shutil


def slow_type(stdscr, text, y, x, color_pair):
    for i, char in enumerate(text):
        stdscr.addstr(y, x + i, char, color_pair)
        stdscr.refresh()
        # time.sleep(0.05)  # Delay for typing effect

def display_file_contents(stdscr, filepath):
    """Display the contents of a .entry file."""
    stdscr.clear()
    header = f"[You are viewing {os.path.basename(filepath)}]"
    stdscr.addstr(0, 0, header, curses.color_pair(1) | curses.A_BOLD)

    with open(filepath, 'r') as file:
        lines = file.readlines()
    for i, line in enumerate(lines, 1):
        stdscr.addstr(i, 0, line.strip())

    height, _ = stdscr.getmaxyx()
    stdscr.addstr(height - 1, 0, "[Tab] Close   [F12] Exit", curses.color_pair(1) | curses.A_BOLD)
    stdscr.refresh()

def display_files(stdscr, start_y, color_pair, selected_idx, entries, path):
    if not entries:
        stdscr.addstr(start_y, 0, "No entries", color_pair)
    else:
        for i, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                display_text = f"[{entry}/]"  # Format for folders
            else:
                display_text = f"> [{entry}]"  # Format for files

            if i == selected_idx:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(start_y + i, 0, display_text)
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.addstr(start_y + i, 0, display_text, color_pair)
                
def get_user_input(stdscr, prompt):
    """Prompt user for input just above the options and return the entered string."""
    height, width = stdscr.getmaxyx()
    y = height - 3
    stdscr.move(y, 0)
    stdscr.clrtoeol()
    stdscr.addstr(y, 0, prompt)
    curses.echo()
    input_str = stdscr.getstr()
    curses.noecho()
    return input_str.decode('utf-8')

def confirm_deletion(stdscr, message):
    """Prompt for deletion confirmation."""
    height, width = stdscr.getmaxyx()
    prompt_y = height // 2
    stdscr.addstr(prompt_y, (width - len(message)) // 2, message)
    stdscr.refresh()
    response = stdscr.getkey()
    return response.lower() == 'y'

def main(stdscr):
    curses.curs_set(1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

    initial_path = os.getcwd()  # Start directory
    path_stack = [initial_path]
    selected_idx = 0
    viewing_file = False

    while True:
        stdscr.clear()
        entries = os.listdir(path_stack[-1])
        filtered_entries = [entry for entry in entries if os.path.isdir(os.path.join(path_stack[-1], entry)) or entry.endswith('.entry')]

        if not viewing_file:
            # Dynamically build the current path display from the path_stack
            if len(path_stack) > 1:
                # Build path display without repeating directory names
                current_path_display = "[Root/" + "/".join(os.path.basename(path) for path in path_stack[1:]) + ']'
            else:
                current_path_display = "[Root]"

            title = "Zeit Corporation Data Management System v1.0.0"
            slow_type(stdscr, title, 0, 0, curses.color_pair(1))
            stdscr.addstr(1, 0, f"Current Path: {current_path_display}", curses.color_pair(1))
            display_files(stdscr, 3, curses.color_pair(1), selected_idx, filtered_entries, path_stack[-1])
            height, _ = stdscr.getmaxyx()
            options_line = "[F1] Create Entry   [F2] Create Folder   [Del] Delete   [F12] Exit"
            if len(path_stack) > 1:
                options_line = "[Tab] Back   " + options_line
            stdscr.addstr(height - 1, 0, options_line, curses.color_pair(1))
        else:
            display_file_contents(stdscr, os.path.join(path_stack[-1], filtered_entries[selected_idx]))

        stdscr.refresh()
        k = stdscr.getch()        
        if k == curses.KEY_F12:
            break
        elif k == 9:  # Tab key to close viewing file or navigate back up
            if viewing_file:
                viewing_file = False
            elif len(path_stack) > 1:
                path_stack.pop()
                selected_idx = 0
        elif k == curses.KEY_DC:  # Handle deletion
            if confirm_deletion(stdscr, "Are you sure you want to delete this? Y/N: "):
                item_to_delete = os.path.join(path_stack[-1], filtered_entries[selected_idx])
                if os.path.isdir(item_to_delete):
                    shutil.rmtree(item_to_delete)
                else:
                    os.remove(item_to_delete)
                # Refresh the list
                entries = os.listdir(path_stack[-1])
                filtered_entries = [entry for entry in entries if os.path.isdir(entry) or entry.endswith('.entry')]
        elif k == curses.KEY_F1:
            new_filename = get_user_input(stdscr, "> Enter new file name: ")
            open(os.path.join(path_stack[-1], new_filename + '.entry'), 'w').close()
        elif k == curses.KEY_F2 and not viewing_file:
            new_foldername = get_user_input(stdscr, "> Enter new folder name: ")
            new_folder_path = os.path.join(path_stack[-1], new_foldername)
            os.makedirs(new_folder_path, exist_ok=True)
            entries = os.listdir(path_stack[-1])
            filtered_entries = [entry for entry in entries if os.path.isdir(os.path.join(path_stack[-1], entry)) or entry.endswith('.entry')]
            selected_idx = 0  # Optionally reset the selection index to the top of the list
        elif k == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif k == curses.KEY_DOWN and selected_idx < len(filtered_entries) - 1:
            selected_idx += 1
        elif k == curses.KEY_ENTER or k == 10 and not viewing_file:
            selected_entry = filtered_entries[selected_idx]
            full_path = os.path.join(path_stack[-1], selected_entry)
            if os.path.isdir(full_path):
                path_stack.append(full_path)
                selected_idx = 0
            elif selected_entry.endswith('.entry'):
                viewing_file = True

curses.wrapper(main)
# static_text = "[F5] Edit Mode   [F12] Exit   [Enter] Open   [ArrUp] Up   [ArrDown] Down"
