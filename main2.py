import tkinter as tk
import subprocess
import zipfile
import os
import tempfile

class SimpleTerminalApp:
    def __init__(self, root):
        self.root = root
        os.environ['TERM'] = ""
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
        with zipfile.ZipFile(self.zip_file_path, 'w') as zipf:
            # Create a simple Python script and add it to the ZIP file
            sample_script_content = """\
print("Hello from the sample script!")
"""
            script_filename = os.path.join(self.temp_dir, 'sample_script.py')
            with open(script_filename, 'w') as script_file:
                script_file.write(sample_script_content)

            zipf.write(script_filename, os.path.basename(script_filename))

            self.output_text.insert(tk.END, f"Created ZIP archive at {self.zip_file_path}\n")

    def execute_command(self):
        command = self.input_text.get()
        if command:
            self.output_text.insert(tk.END, f"> {command}\n")
            self.input_text.delete(0, tk.END)
            self.run_command(command)

    def run_command(self, command):
        try:
            # Execute command in the temp directory where ZIP was extracted
            output = subprocess.check_output(command, cwd=self.temp_dir, stderr=subprocess.STDOUT, shell=True, text=True)
            self.output_text.insert(tk.END, output + "\n")
        except subprocess.CalledProcessError as e:
            self.output_text.insert(tk.END, f"Error: {e.output}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Unexpected error: {str(e)}\n")
        self.output_text.insert(tk.END, "\n>S66 ")

if __name__ == "__main__":
    root = tk.Tk()
    terminal_app = SimpleTerminalApp(root)
    root.mainloop()
