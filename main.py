import tkinter as tk
from tkinter import scrolledtext, messagebox
import zipfile
import csv
import os
import subprocess
import xml.etree.ElementTree as ET
from time import time


class ShellEmulator:
    def __init__(self, config):
        self.user = config['user']
        self.vfs_path = config['vfs_path']
        self.log_path = config['log_path']
        self.startup_script = config['startup_script']
        self.current_directory = '/'
        self.commands = {
            'ls': self.ls,
            'cd': self.cd,
            'exit': self.exit,
            'cp': self.cp,
            'uptime': self.uptime,
            'find': self.find,
        }

    def run_command(self, command):
        cmd_parts = command.split()
        cmd_name = cmd_parts[0]
        if cmd_name in self.commands:
            self.commands[cmd_name](cmd_parts[1:] if len(cmd_parts) > 1 else [])
        else:
            self.log_action(f"Unknown command: {cmd_name}")
            self.output(f"Unknown command: {cmd_name}")

    # Функции для команд
    def ls(self, args):
        self.log_action("ls command")
        # Здесь должна быть логика для ls используя VFS
        self.output("Listing files...")

    def cd(self, args):
        self.log_action(f"cd to {args[0]}")
        if args:
            self.current_directory = args[0]
            self.output(f"Changed directory to {self.current_directory}")
        else:
            self.output("No directory specified.")

    def exit(self, args):
        self.log_action("exit command")
        self.output("Exiting.")
        os._exit(0)

    def cp(self, args):
        self.log_action("cp command")
        if len(args) < 2:
            self.output("Usage: cp <source> <destination>")
            return
        self.output(f"Copying from {args[0]} to {args[1]}")

    def uptime(self, args):
        self.log_action("uptime command")
        self.output("System uptime: 72 minutes")

    def find(self, args):
        self.log_action("find command")
        self.output(f"Finding '{' '.join(args)}'...")

    def log_action(self, action):
        with open(self.log_path, mode='a', newline='') as log_file:
            log_writer = csv.writer(log_file, delimiter=',')
            log_writer.writerow([self.user, action, time()])

    def output(self, message):
        print(message)  # Вывод в GUI будет реализован далее


class EmulatorGUI:
    def __init__(self, master, emulator):
        self.master = master
        self.master.title("Shell Emulator")
        self.emulator = emulator

        self.txt_output = scrolledtext.ScrolledText(master, state='disabled')
        self.txt_output.pack()

        self.txt_input = tk.Entry(master)
        self.txt_input.bind("<Return>", self.process_command)
        self.txt_input.pack()

    def process_command(self, event):
        command = self.txt_input.get()
        self.txt_input.delete(0, tk.END)
        self.emulator.run_command(command)

    def update_output(self, message):
        self.txt_output.config(state='normal')
        self.txt_output.insert(tk.END, message + '\n')
        self.txt_output.config(state='disabled')


def load_config(file_path) -> dict:
    tree = ET.parse(file_path)
    root = tree.getroot()
    return {
        'user': root.find('user').text,
        'vfs_path': root.find('vfs_path').text,
        'log_path': root.find('log_path').text,
        'startup_script': root.find('startup_script').text
    }


if __name__ == "__main__":
    config = load_config('config.xml')
    emulator = ShellEmulator(config)
    root = tk.Tk()
    gui = EmulatorGUI(root, emulator)
    root.mainloop()
