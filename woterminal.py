import csv
import math
import tkinter as tk
import subprocess
import zipfile
import os
from datetime import time, datetime
from os import listdir

from main import load_config

IS_FILE = True
IS_DIR = False


class SimpleTerminalApp:


    def __init__(self, root, config:dict):
        self.start_time = datetime.now()
        self.current_dir = '/'
        self.pool_of_commands = ['ls', 'clear', 'exit', 'cd', 'mkdir', 'rmdir',
                                 'rm', 'cp', 'uptime', 'find', 'touch', 'pwd']

        self.root = root
        self.root.title("Simple Terminal with Zip Env")
        self.output_text = tk.Text(root, wrap='word', height=20, width=70)
        self.output_text.pack()
        self.input_text = tk.Entry(root, width=70)
        self.input_text.pack()
        self.execute_button = tk.Button(root, text="Execute", command=self.execute_command)
        self.execute_button.pack()

        self.user = config['user']
        self.vfs_path = config['vfs_path']
        self.log_path = config['log_path']
        self.startup_script = config['startup_script']
        if not self.validate_xml(config):
            print("Incorrect xml-file")
            exit(1)

        f = open('log.csv', 'w+')
        f.close()

        self.output_text.insert(tk.END, self.user + ">")

    def validate_xml(self, config:dict) -> bool:
        correct_values = {'vfs_path':False, 'log_path': False, 'startup_script': False}
        for file in listdir(os.curdir):
            if file == config['vfs_path']:
                correct_values['vfs_path'] = True
            if file == config['log_path']:
                correct_values['log_path'] = True
            if file == config['startup_script']:
                correct_values['startup_script'] = True
        return True if all(correct_values.values()) else False

    def log_action(self, action):
        with open(self.log_path, mode='a', newline='') as log_file:
            log_writer = csv.writer(log_file, delimiter=',')
            log_writer.writerow([self.user, action, datetime.now()])

    def execute_command(self):
        command = self.input_text.get()
        if command:
            self.output_text.insert(tk.END, f" {command}\n")
            self.input_text.delete(0, tk.END)
            self.run_command(command)

    # Абсолютный или относительный
    # Если абсолютный: поставить res как /
    # Если относительный : поставить res как current_dir
    # Парсить состоявляющие пути, проверяя их коррекнтость
    def get_absolute_path(self, path: str) -> str:
        if path.startswith("/"):
            return path
        res = self.current_dir
        parts_of_path = path.split('/')
        for part in parts_of_path:
            if part == ".":
                pass
            elif part == "..":
                res = res.rsplit('/', 1)[0]
            else:
                if part != '':
                    res += part + '/'
        res = '/' if len(res) == 0 else res
        return res

    def check_correct_folder_path(self, path: str) -> bool:
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
            for file in zip_ref.infolist():
                p1 = self.get_absolute_path('/' + file.filename)
                p2 = self.get_absolute_path(path)
                if p1 == p2:
                    if file.is_dir():
                        return True
        return False

    def check_correct_file_path(self, path: str) -> bool:
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
            for file in zip_ref.infolist():
                # может неработать
                p1 = self.get_absolute_path(file.filename)
                p2 = self.get_absolute_path(path)
                if p1 == p2 and not file.is_dir():
                    return True
        return False

    # /asd/zxc/ -> /asd/
    # /qwe/asd/zxc/ -> /qwe/asd/
    def check_correct_arguments(self, parsed_command: list) -> bool:
        if parsed_command[0] == 'ls':
            if len(parsed_command) > 2:
                return False
            elif len(parsed_command) == 1:
                return True
            else:
                return self.check_correct_folder_path(self.get_absolute_path(parsed_command[1]))
        elif parsed_command[0] == 'mkdir' or parsed_command[0] == 'touch':
            if len(parsed_command) != 2:
                return False
            path_to_check = self.get_absolute_path(parsed_command[1]).rsplit('/', 2)[0]
            if path_to_check == '' or path_to_check == '/':
                return True
            return self.check_correct_folder_path(path_to_check)
        elif parsed_command[0] == 'rmdir' or parsed_command[0] == 'cd':
            if len(parsed_command) != 2:
                return False
            return self.check_correct_folder_path(self.get_absolute_path(parsed_command[1]))
        elif parsed_command[0] == 'rm':
            if len(parsed_command) != 2:
                return False
            return self.check_correct_file_path(self.get_absolute_path(parsed_command[1]))
        elif (parsed_command[0] == 'exit' or parsed_command[0] == 'clear' or parsed_command[0] == 'uptime'
              or parsed_command[0] == 'pwd' or parsed_command[0] == 'oldls'):
            return len(parsed_command) == 1
        elif parsed_command[0] == 'find':
            if len(parsed_command) != 2:
                return False
            return (self.check_correct_folder_path(self.get_absolute_path(parsed_command[1]))
                    or self.check_correct_file_path(self.get_absolute_path(parsed_command[1])))
        # elif parsed_command[0] == 'cd':
        #     if len(parsed_command) != 2:
        #         return False
        #     return self.check_correct_folder_path(self.get_absolute_path(parsed_command[1]))
        elif parsed_command[0] == 'cp':
            if len(parsed_command) != 3:
                return False
            return (self.check_correct_file_path(parsed_command[1])
                    and self.check_correct_folder_path(parsed_command[2]))
        else:
            return False

    def run_command(self, unparsed_command: str):
        parsed_command = unparsed_command.split(" ")
        if not self.check_correct_arguments(parsed_command):
            self.output_text.insert(tk.END, "Incorrect command\n")
            self.log_action("Incorrect command")
            return
        command = parsed_command[0]
        if command == 'clear':
            self.output_text.delete('1.0', tk.END)
            self.log_action("clear")
        elif command == 'exit':
            root.quit()
            self.log_action("exit")
        elif command == 'ls':
            self.check_correct_arguments(parsed_command)
            if len(parsed_command) == 1:
                path = self.current_dir
            else:
                if self.get_absolute_path(parsed_command[1])[-1] == '/':
                    path = self.get_absolute_path(parsed_command[1])
                else:
                    path = self.get_absolute_path(parsed_command[1]) + '/'
            with zipfile.ZipFile(self.vfs_path) as zip_file:
                files = set()
                dirs = set()
                for x in zip_file.infolist():
                    if ('/' + x.filename).startswith(path):
                        name = ('/' + x.filename).replace(path, '', 1)
                        if x.is_dir():
                            dirs.add(name.split("/", 1)[0])
                        else:
                            files.add(name.split("/", 1)[0])
                for x in dirs:
                    if x != '' and x != '/':
                        self.output_text.insert(tk.END, f"{x}/\n")
                for x in files:
                    if x != '' and x != '/':
                        self.output_text.insert(tk.END, f"{x}\n")
            self.log_action("ls")
        elif command == 'oldls':
            with zipfile.ZipFile(self.vfs_path) as zip_file:
                for x in zip_file.infolist():
                    self.output_text.insert(tk.END, f"{x.filename}\n")
        elif command == 'mkdir':
            with zipfile.ZipFile(self.vfs_path, 'a') as zip_file:
                zip_file.mkdir(parsed_command[1])
            self.log_action("mkdir " + parsed_command[1])
        elif command == 'touch':
            # Не работает
            with zipfile.ZipFile(self.vfs_path, 'a') as zip_file:
                if parsed_command[1] not in zip_file.namelist():
                    zip_file.writestr(parsed_command[1], '')
                else:
                    self.output_text.insert(tk.END, "Error: file already exists\n")
            self.log_action("touch " + parsed_command[1])
        elif command == 'rmdir':
            temp_zip_path = self.vfs_path + '.tmp'
            with zipfile.ZipFile(self.vfs_path, 'r') as zip_to_read:
                with zipfile.ZipFile(temp_zip_path, 'w') as zip_to_write:
                    for item in zip_to_read.infolist():
                        if not self.get_absolute_path(item.filename).startswith(
                                self.get_absolute_path(parsed_command[1])):
                            zip_to_write.writestr(item, zip_to_read.read(item.filename))
            os.replace(temp_zip_path, self.vfs_path)
            self.log_action("rmdir" + parsed_command[1])
        elif command == 'rm':
            temp_zip_path = self.vfs_path + '.tmp'
            with zipfile.ZipFile(self.vfs_path, 'r') as zip_to_read:
                with zipfile.ZipFile(temp_zip_path, 'w') as zip_to_write:
                    for item in zip_to_read.infolist():
                        if item.filename != parsed_command[1]:
                            zip_to_write.writestr(item, zip_to_read.read(item.filename))
            os.replace(temp_zip_path, self.vfs_path)
            self.log_action("rm " + parsed_command[1])
        elif command == 'uptime':
            command_time = datetime.now()
            time_duration = command_time - self.start_time
            self.output_text.insert(tk.END,
                                    f"{command_time.strftime('%H:%M:%S')} uptime {math.floor(time_duration.total_seconds())} sec\n")
            self.log_action("uptime")
        elif command == 'find':
            abs_path = self.get_absolute_path(parsed_command[1])
            with zipfile.ZipFile(self.vfs_path, 'r') as zip_to_read:
                for item in zip_to_read.namelist():
                    if ('/' + item).startswith(abs_path):
                        self.output_text.insert(tk.END, f"{item}\n")
            self.log_action("find " + parsed_command[1])
        elif command == 'cp':
            # пофиксить issue с лишним фантомным файлом при копировании в директорию
            zip_temp_path = self.vfs_path + '.tmp'
            target_dir = self.get_absolute_path(parsed_command[2]).split('/', 1)[1]
            with zipfile.ZipFile(self.vfs_path, 'r') as zip_to_read:
                with zipfile.ZipFile(zip_temp_path, 'w') as zip_to_write:
                    for item in zip_to_read.infolist():
                        if item.filename == parsed_command[1]:
                            zip_to_write.writestr(target_dir + item.filename, zip_to_read.read(item.filename))
                        zip_to_write.writestr(item, zip_to_read.read(item.filename))
            os.replace(zip_temp_path, self.vfs_path)
            self.log_action("cp " + parsed_command[1] + " to " + parsed_command[2])
        elif command == "cd":
            # не работает ../
            abs_path = self.get_absolute_path(parsed_command[1])
            self.current_dir = abs_path
            self.log_action("cd to " + parsed_command[1])
        elif command == 'pwd':
            self.output_text.insert(tk.END, f"{self.current_dir}\n")
            self.log_action("pwd")
        self.output_text.insert(tk.END, self.user + ">")



if __name__ == "__main__":
    config = load_config('config.xml')
    root = tk.Tk()
    terminal_app = SimpleTerminalApp(root, config)
    root.mainloop()

#     def create_zip_archive(self):
#         # Create a zip archive and add a sample script
#         with zipfile.ZipFile(self.zip_file_path, 'w') as zipf:
#             # Create a simple Python script and add it to the ZIP file
#             sample_script_content = """\
# print("Hello from the sample script!")
# """
#             script_filename = os.path.join(self.temp_dir, 'sample_script.py')
#             with open(script_filename, 'w') as script_file:
#                 script_file.write(sample_script_content)
#
#             zipf.write(script_filename, os.path.basename(script_filename))
#
#             self.output_text.insert(tk.END, f"Created ZIP archive at {self.zip_file_path}\n")
