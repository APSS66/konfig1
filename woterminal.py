import csv
import math
import tkinter as tk
import zipfile
import os
from datetime import datetime
from os import listdir

from main import load_config

IS_FILE = True
IS_DIR = False


class SimpleTerminalApp:


    def __init__(self, root, config:dict):
        self.start_time = datetime.now()
        self.current_dir = '/'

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

    def get_absolute_path(self, path: str, IS_FILE: bool) -> str:
        if path.startswith("/"):
            return path
        res = self.current_dir
        parts_of_path = path.split('/')
        for part in parts_of_path:
            if part == ".":
                pass
            elif part == "..":
                res = res.rsplit('/', 2)[0]
            else:
                if part != '':
                    res += part + '/'
        res = res[:-1] if IS_FILE else res
        res = '/' if len(res) == 0 else res

        return res

    def check_correct_folder_path(self, path: str) -> bool:
        if path == '/':
            return True
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
            for file in zip_ref.infolist():
                p1 = '/' + file.filename
                p2 = self.get_absolute_path(path, IS_DIR)
                if p1 == p2 and file.is_dir():
                    return True
        return False

    def check_correct_file_path(self, path: str) -> bool:
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
            for file in zip_ref.infolist():
                p1 = '/' + file.filename
                p2 = self.get_absolute_path(path, IS_FILE)
                if p1 == p2 and not file.is_dir():
                    return True
        return False

    def check_correct_arguments(self, parsed_command: list) -> bool:
        if parsed_command[0] == 'ls':
            if len(parsed_command) > 2:
                return False
            elif len(parsed_command) == 1:
                return True
            else:
                return self.check_correct_folder_path(self.get_absolute_path(parsed_command[1], IS_DIR))
        elif parsed_command[0] == 'mkdir' or parsed_command[0] == 'touch':
            if len(parsed_command) != 2:
                return False
            file_type = IS_FILE if parsed_command[1] == 'touch' else IS_DIR
            path_to_check = self.get_absolute_path(parsed_command[1], file_type).rsplit('/', 2)[0] + '/'
            print(path_to_check)
            if path_to_check == '' or path_to_check == '/':
                return True
            return self.check_correct_folder_path(path_to_check)
        elif parsed_command[0] == 'rmdir' or parsed_command[0] == 'cd':
            if len(parsed_command) != 2:
                return False
            return self.check_correct_folder_path(self.get_absolute_path(parsed_command[1], IS_DIR))
        elif parsed_command[0] == 'rm':
            if len(parsed_command) != 2:
                return False
            return self.check_correct_file_path(self.get_absolute_path(parsed_command[1], IS_FILE))
        elif (parsed_command[0] == 'exit' or parsed_command[0] == 'clear' or parsed_command[0] == 'uptime'
              or parsed_command[0] == 'pwd' or parsed_command[0] == 'oldls'):
            return len(parsed_command) == 1
        elif parsed_command[0] == 'find':
            if len(parsed_command) != 2:
                return False
            return (self.check_correct_folder_path(self.get_absolute_path(parsed_command[1], IS_DIR))
                    or self.check_correct_file_path(self.get_absolute_path(parsed_command[1], IS_FILE)))
        elif parsed_command[0] == 'cp':
            if len(parsed_command) != 3:
                return False
            return (self.check_correct_file_path(parsed_command[1])
                    and self.check_correct_folder_path(parsed_command[2]))
        else:
            return False

    def clear(self):
        self.output_text.delete('1.0', tk.END)
        self.log_action("clear")

    def exit(self):
        root.quit()
        self.log_action("exit")

    def ls(self, parsed_command):
        self.check_correct_arguments(parsed_command)
        if len(parsed_command) == 1:
            path = self.current_dir
        else:
            if self.get_absolute_path(parsed_command[1], IS_DIR)[-1] == '/':
                path = self.get_absolute_path(parsed_command[1], IS_DIR)
            else:
                path = self.get_absolute_path(parsed_command[1], IS_DIR) + '/'
        with zipfile.ZipFile(self.vfs_path) as zip_file:
            files = set()
            dirs = set()
            for x in zip_file.infolist():
                if ('/' + x.filename).startswith(path):
                    name = ('/' + x.filename).replace(path, '', 1)
                    if name.count('/') > 0:
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

    def oldls(self):
        with zipfile.ZipFile(self.vfs_path) as zip_file:
            for x in zip_file.infolist():
                self.output_text.insert(tk.END, f"{x.filename}\n")

    def mkdir(self, parsed_command):
        with zipfile.ZipFile(self.vfs_path, 'a') as zip_file:
            zip_file.mkdir(parsed_command[1])
        self.log_action("mkdir " + parsed_command[1])

    def touch(self, parsed_command):
        file_path = self.get_absolute_path(parsed_command[1], IS_FILE)[1:]
        with zipfile.ZipFile(self.vfs_path, 'a') as zip_file:
            if file_path not in zip_file.namelist():
                zip_file.writestr(file_path, '')
            else:
                self.output_text.insert(tk.END, "Error: file already exists\n")
        self.log_action("touch " + file_path)

    def rmdir(self, parsed_command):
        temp_zip_path = self.vfs_path + '.tmp'
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_to_read:
            with zipfile.ZipFile(temp_zip_path, 'w') as zip_to_write:
                for item in zip_to_read.infolist():
                    if not self.get_absolute_path(item.filename, IS_DIR).startswith(
                            self.get_absolute_path(parsed_command[1], IS_DIR)):
                        zip_to_write.writestr(item, zip_to_read.read(item.filename))
        os.replace(temp_zip_path, self.vfs_path)
        self.log_action("rmdir" + parsed_command[1])

    def rm(self, parsed_command):
        temp_zip_path = self.vfs_path + '.tmp'
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_to_read:
            with zipfile.ZipFile(temp_zip_path, 'w') as zip_to_write:
                for item in zip_to_read.infolist():
                    p1 = '/' + item.filename
                    p2 = self.get_absolute_path(parsed_command[1], IS_FILE)
                    if p1 != p2:
                        zip_to_write.writestr(item, zip_to_read.read(item.filename))
        os.replace(temp_zip_path, self.vfs_path)
        self.log_action("rm " + parsed_command[1])

    def uptime(self):
        command_time = datetime.now()
        time_duration = command_time - self.start_time
        self.output_text.insert(tk.END,
                                f"{command_time.strftime('%H:%M:%S')} uptime {math.floor(time_duration.total_seconds())} sec\n")
        self.log_action("uptime")

    def find(self, parsed_command):
        abs_path = self.get_absolute_path(parsed_command[1], IS_FILE)
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_to_read:
            for item in zip_to_read.namelist():
                if ('/' + item).startswith(abs_path):
                    self.output_text.insert(tk.END, f"{item}\n")
        self.log_action("find " + parsed_command[1])

    def cp(self, parsed_command):
        zip_temp_path = self.vfs_path + '.tmp'
        file_path = self.get_absolute_path(parsed_command[1], IS_FILE)[1:]
        target_dir = self.get_absolute_path(parsed_command[2], IS_DIR)[1:]
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_to_read:
            with zipfile.ZipFile(zip_temp_path, 'w') as zip_to_write:
                for item in zip_to_read.infolist():
                    tfn = item.filename
                    if file_path == tfn:
                        zip_to_write.writestr(target_dir + item.filename, zip_to_read.read(item.filename))
                    zip_to_write.writestr(item, zip_to_read.read(item.filename))
        os.replace(zip_temp_path, self.vfs_path)
        self.log_action("cp " + parsed_command[1] + " to " + parsed_command[2])

    def cd(self, parsed_command):
        abs_path = self.get_absolute_path(parsed_command[1], IS_DIR)
        self.current_dir = abs_path
        self.log_action("cd to " + parsed_command[1])

    def pwd(self):
        self.output_text.insert(tk.END, f"{self.current_dir}\n")
        self.log_action("pwd")

    def run_command(self, unparsed_command: str):
        parsed_command = unparsed_command.split(" ")
        if not self.check_correct_arguments(parsed_command):
            self.output_text.insert(tk.END, "Incorrect command\n")
            self.log_action("Incorrect command")
            return
        command = parsed_command[0]
        if command == 'clear':
           self.clear()
        elif command == 'exit':
            self.exit()
        elif command == 'ls':
           self.ls(parsed_command)
        elif command == 'oldls':
            self.oldls()
        elif command == 'mkdir':
            self.mkdir(parsed_command)
        elif command == 'touch':
            # Не работает
            self.touch(parsed_command)
        elif command == 'rmdir':
            self.rmdir(parsed_command)
        elif command == 'rm':
           self.rm(parsed_command)
        elif command == 'uptime':
            self.uptime()
        elif command == 'find':
           self.find(parsed_command)
        elif command == 'cp':
            self.cp(parsed_command)
        elif command == "cd":
            self.cd(parsed_command)
        elif command == 'pwd':
            self.pwd()
        self.output_text.insert(tk.END, self.user + ">")



if __name__ == "__main__":
    config = load_config('config.xml')
    root = tk.Tk()
    terminal_app = SimpleTerminalApp(root, config)
    root.mainloop()
