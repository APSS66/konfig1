import tkinter as tk
import subprocess
import zipfile
import os
import tempfile


class SimpleTerminalApp:
    def __init__(self, root):
        self.current_dir = '.'
        self.pool_of_commands = ['ls', 'clear', 'exit', 'cd', 'mkdir', 'rmdir',
                                 'rm', 'cp', 'uptime', 'find', 'touch', 'pwd']
        self.root = root
        os.environ['TERM'] = "xterm-256color"
        self.root.title("Simple Terminal with Zip Env")

        # Text box for output
        self.output_text = tk.Text(root, wrap='word', height=20, width=70)
        self.output_text.pack()

        # Text box for input commands
        self.input_text = tk.Entry(root, width=70)
        self.input_text.pack()

        # Button to execute command
        self.execute_button = tk.Button(root, text="Execute", command=self.execute_command)
        self.execute_button.pack()

        # Create the ZIP archive upon initialization
        self.temp_dir = tempfile.mkdtemp()  # Create temporary directory
        self.zip_file_path = os.path.join(self.temp_dir, 'env_files.zip')
        self.create_zip_archive()

    def create_zip_archive(self):
        # Create a zip archive and add a sample script
        with zipfile.ZipFile("virtual_filesystem.zip", 'w') as zipf:
            print(zipf.filelist)
            # Create a simple Python script and add it to the ZIP file
            sample_script_content = """\
print("Hello from the sample script!")
"""
            script_filename = os.path.join(self.temp_dir, 'sample_script.py')
            with open(script_filename, 'w') as script_file:
                script_file.write(sample_script_content)

            zipf.write(script_filename, os.path.basename(script_filename))
            self.output_text.insert(tk.END, "S66>")
            #self.output_text.insert(tk.END, f"Created ZIP archive at {self.zip_file_path}\n")

    def execute_command(self):
        command = self.input_text.get()
        if command:
            self.output_text.insert(tk.END, f" {command}\n")
            self.input_text.delete(0, tk.END)
            self.run_command(command)

    def run_command(self, unparsed_command):
        parsed_command = unparsed_command.split(" ")
        command = parsed_command[0]
        try:
            if command == 'clear':
                self.output_text.delete('1.0', tk.END)
            elif command == 'exit':
                root.quit()
            # elif command == 'cd':
            #     print("Проебали"с)
            elif command in self.pool_of_commands:
                output = subprocess.check_output(unparsed_command, cwd=self.temp_dir, stderr=subprocess.STDOUT,
                                                 shell=True, text=True)
                self.output_text.insert(tk.END, output)
            else:
                self.output_text.insert(tk.END, f"Unknown command: {command}\n")
        except subprocess.CalledProcessError as e:
            self.output_text.insert(tk.END, f"Error: {e.output}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Unexpected error: {str(e)}\n")
        self.output_text.insert(tk.END, "S66>")


if __name__ == "__main__":
    root = tk.Tk()
    terminal_app = SimpleTerminalApp(root)
    root.mainloop()
