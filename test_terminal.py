import math
import unittest
import os
from unittest.mock import MagicMock, patch, mock_open, create_autospec
from datetime import datetime, timedelta
import zipfile
import terminal
import tkinter as tk


class TestSimpleTerminalApp(unittest.TestCase):
    @patch('tkinter.Text')
    @patch('tkinter.Entry')
    @patch('tkinter.Button')
    def setUp(self, mock_button, mock_entry, mock_text):
        self.root = tk.Tk()
        self.output_text = mock_text.return_value
        self.input_text = mock_entry.return_value

        self.config = {
            'user': 'S66',
            'vfs_path': 'filesys.zip',
            'log_path': 'log.csv',
            'startup_script': 'startup_script.txt'
        }
        self.app = terminal.SimpleTerminalApp(self.root, self.config)
        self.app.output_text = self.output_text
        self.app.input_text = self.input_text
        self.app.current_dir = "/"
        self.app.start_time = datetime.now();
    
    @patch('os.listdir')
    def test_validate_xml(self, mock_listdir):
        mock_listdir.return_value = ['filesys.zip', 'log.csv', 'startup_script.txt']
        result = self.app.validate_xml(self.config, os.listdir())
        self.assertTrue(result)

    @patch('builtins.open', new_callable=mock_open)
    def test_log_action(self, mock_file):
        action = "test_action"
        self.app.log_action(action)
        mock_file.assert_called_once_with(self.app.log_path, mode='a', newline='')
        handle = mock_file()
        handle.write.assert_called_once_with("S66,{},{}\r\n".format(action, datetime.now().strftime('%H:%M')))

    @patch('zipfile.ZipFile')
    def test_check_correct_folder_path(self, mock_zipfile):
        mock_zipfile.return_value.__enter__.return_value.infolist.return_value = [
            zipfile.ZipInfo('folder1/'),
            zipfile.ZipInfo('folder2/')
        ]
        result = self.app.check_correct_folder_path('folder1')
        self.assertTrue(result)

    @patch('zipfile.ZipFile')
    def test_check_correct_file_path(self, mock_zipfile):
        mock_zipfile.return_value.__enter__.return_value.infolist.return_value = [
            zipfile.ZipInfo('file1.txt'),
            zipfile.ZipInfo('file2.txt')
        ]
        result = self.app.check_correct_file_path('file1.txt')
        self.assertTrue(result)

    @patch('builtins.open', new_callable=mock_open, read_data = 'ls')
    def test_execute_startup_script(self, mock_startup_script):
        self.app.run_command = MagicMock()
        self.app.execute_startup_script();
        mock_startup_script.assert_called_with('startup_script.txt', 'r')
        self.app.output_text.insert.assert_any_call(tk.END, ' ls\n')
        self.app.run_command.assert_any_call('ls')

    @patch('builtins.open', new_callable=mock_open)
    @patch.object(terminal.SimpleTerminalApp, 'run_command')
    def test_execute_command(self, mock_open, mocked_run):
        self.input_text.get.return_value = 'clear'
        self.app.execute_command()
        self.output_text.insert.assert_called_with(tk.END, ' clear\n')
        self.input_text.delete.assert_called_with(0, tk.END)
        self.app.run_command.assert_called_once_with('clear')

    def test_get_absolute_path(self):
        self.assertEqual(self.app.get_absolute_path('/', terminal.IS_DIR), '/')
        self.assertEqual(self.app.get_absolute_path("qwe", terminal.IS_FILE), '/qwe')

    def test_check_correct_argument(self):
        self.assertTrue(self.app.check_correct_arguments(['ls']))
        self.assertFalse(self.app.check_correct_arguments(['cp']))

    @patch.object(terminal.SimpleTerminalApp, 'ls')
    def test_run_command(self, mocked_ls):
        self.app.run_command('ls')
        self.output_text.insert.assert_called_with(tk.END, "S66>")
        self.app.ls.assert_called_once_with(['ls'])

    def test_pwd(self):
        self.app.pwd()
        self.output_text.insert.assert_called_with(tk.END, f"{self.app.current_dir}\n")

    @patch.object(terminal.SimpleTerminalApp, 'get_absolute_path')
    def test_cd_1(self, mocked_abs_path):
        mocked_abs_path.return_value = '/'
        self.app.cd(['cd', '/'])
        self.app.get_absolute_path.assert_called_with('/', terminal.IS_DIR)
        self.assertEqual(self.app.current_dir, '/')

    @patch.object(terminal.SimpleTerminalApp, 'get_absolute_path')
    def test_cd_2(self, mocked_abs_path):
        mocked_abs_path.return_value = '/asd/'
        self.app.cd(['cd', 'asd/'])
        self.app.get_absolute_path.assert_called_with('asd/', terminal.IS_DIR)
        self.assertEqual(self.app.current_dir, '/asd/')

    @patch('zipfile.ZipFile')
    @patch('os.replace')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    @patch.object(terminal.SimpleTerminalApp, 'get_absolute_path')
    def test_cp1(self, mock_get_absolute_path, mock_log_action, mock_os_replace, mock_zipfile):
        self.app.cp(['cp', 'test', 'asd/'])
        mock_zipfile.assert_any_call('filesys.zip', 'r')
        mock_zipfile.assert_any_call('filesys.zip.tmp', 'w')
        mock_os_replace.assert_called_once_with('filesys.zip.tmp', 'filesys.zip')
        mock_log_action.assert_called_once_with("cp test to asd/")

    @patch('zipfile.ZipFile')
    @patch('os.replace')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    @patch.object(terminal.SimpleTerminalApp, 'get_absolute_path')
    def test_cp2(self, mock_get_absolute_path, mock_log_action, mock_os_replace, mock_zipfile):
        self.app.cp(['cp', 'asd/test', '/'])
        mock_zipfile.assert_any_call('filesys.zip', 'r')
        mock_zipfile.assert_any_call('filesys.zip.tmp', 'w')
        mock_os_replace.assert_called_once_with('filesys.zip.tmp', 'filesys.zip')
        mock_log_action.assert_called_once_with("cp asd/test to /")
    
    @patch('zipfile.ZipFile')
    @patch.object(terminal.SimpleTerminalApp, 'get_absolute_path')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    def test_find1(self, mock_log_action, mock_get_absolute_path, mock_zipfile):
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.namelist.return_value = [
            'absolute/path/to/file1.txt',
            'absolute/path/to/file2.txt',
            'absolute/other/path/to/file3.txt'
        ]
        mock_get_absolute_path.return_value = '/absolute/path/to'
        self.app.output_text.insert = MagicMock()
        self.app.find(['find', 'file2.txt'])
        self.app.output_text.insert.assert_called_with(tk.END, 'absolute/path/to/file2.txt\n')
        mock_log_action.assert_called_once_with('find file2.txt')
        
    @patch('zipfile.ZipFile')
    @patch.object(terminal.SimpleTerminalApp, 'get_absolute_path')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    def test_find2(self, mock_log_action, mock_get_absolute_path, mock_zipfile):
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.namelist.return_value = []
        mock_get_absolute_path.return_value = '/absolute/path/to'
        self.app.output_text.insert = MagicMock()
        self.app.find(['find', 'file2.txt'])
        self.app.output_text.insert.assert_not_called()
        mock_log_action.assert_called_once_with('find file2.txt')

    @patch('datetime.datetime')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    def test_uptime(self, mock_datetime, mock_log_action):
        self.app.uptime()
        command_time = datetime.now()
        time_duration = command_time - self.app.start_time
        expected_output = f"{command_time.strftime('%H:%M:%S')} uptime {math.floor(time_duration.total_seconds())} sec\n"
        self.app.log_action.assert_called_once_with("uptime")
        self.app.output_text.insert.assert_called_with(tk.END, expected_output)

    @patch('zipfile.ZipFile')
    @patch('os.replace')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    @patch.object(terminal.SimpleTerminalApp, 'get_absolute_path')
    def test_rm1(self, mock_get_absolute_path, mock_log_action, mock_os_replace, mock_zipfile):
        mock_zip_instance = MagicMock()
        self.app.log_action = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.infolist.return_value = [MagicMock(filename='file1.txt'), MagicMock(filename='file2.txt')]
        mock_zip_instance.read.side_effect = lambda filename: f"content of {filename}".encode()
        self.app.get_absolute_path = MagicMock(return_value='/file1.txt')
        self.app.rm(['rm', 'file1.txt'])
        mock_zip_instance.writestr.assert_called_once_with(mock_zip_instance.infolist()[1], b'content of file2.txt')
        mock_os_replace.assert_called_once_with('filesys.zip.tmp', 'filesys.zip')
        self.app.log_action.assert_called_once_with("rm file1.txt")

    @patch('zipfile.ZipFile')
    @patch('os.replace')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    @patch.object(terminal.SimpleTerminalApp, 'get_absolute_path')
    def test_rm2(self, mock_get_absolute_path, mock_log_action, mock_os_replace, mock_zipfile):
        mock_zip_instance = MagicMock()
        self.app.log_action = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.infolist.return_value = [MagicMock(filename='asd/file1.txt'), MagicMock(filename='file2.txt')]
        mock_zip_instance.read.side_effect = lambda filename: f"content of {filename}".encode()
        self.app.get_absolute_path = MagicMock(return_value='/asd/file1.txt')
        self.app.rm(['rm', 'asd/file1.txt'])
        mock_zip_instance.writestr.assert_called_once_with(mock_zip_instance.infolist()[1], b'content of file2.txt')
        mock_os_replace.assert_called_once_with('filesys.zip.tmp', 'filesys.zip')
        self.app.log_action.assert_called_once_with("rm asd/file1.txt")
    
    @patch('zipfile.ZipFile')
    @patch('os.replace')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    def test_rmdir1(self, mock_log_action, mock_os_replace, mock_zipfile):
        mock_zip_instance = MagicMock()
        self.app.log_action = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.infolist.return_value = [MagicMock(filename='asd/'), MagicMock(filename='file.txt')]
        mock_zip_instance.read.side_effect = lambda filename: f"content of {filename}".encode()
        self.app.rmdir(['rmdir', 'asd/'])
        mock_zip_instance.writestr.assert_called_once_with(mock_zip_instance.infolist()[1], b'content of file.txt')
        self.assertEqual(mock_zip_instance.writestr.call_count, 1)
        mock_os_replace.assert_called_once_with('filesys.zip.tmp', 'filesys.zip')
        self.app.log_action.assert_called_once_with("rmdir asd/")


    @patch('zipfile.ZipFile')
    @patch('os.replace')
    @patch.object(terminal.SimpleTerminalApp, 'log_action')
    def test_rmdir2(self, mock_log_action, mock_os_replace, mock_zipfile):
        mock_zip_instance = MagicMock()
        self.app.log_action = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.infolist.return_value = [MagicMock(filename='asd/'), MagicMock(filename='asd.txt')]
        mock_zip_instance.read.side_effect = lambda filename: f"content of {filename}".encode()
        self.app.rmdir(['rmdir', 'asd/'])
        mock_zip_instance.writestr.assert_called_once_with(mock_zip_instance.infolist()[1], b'content of asd.txt')
        self.assertEqual(mock_zip_instance.writestr.call_count, 1)
        mock_os_replace.assert_called_once_with('filesys.zip.tmp', 'filesys.zip')
        self.app.log_action.assert_called_once_with("rmdir asd/")

    @patch('zipfile.ZipFile')
    def test_touch1(self, mock_zipfile):
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.namelist.return_value = []  # Нет существующих файлов
        self.app.get_absolute_path = MagicMock(return_value='/new_file.txt')
        self.app.touch(['touch', 'new_file.txt'])
        mock_zip_instance.writestr.assert_called_once_with('new_file.txt', '')
        self.app.log_action = MagicMock()
        self.app.touch(['touch', 'new_file.txt'])
        self.app.log_action.assert_called_once_with("touch new_file.txt")

    @patch('zipfile.ZipFile')
    def test_touch2(self, mock_zipfile):
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.namelist.return_value = ['existing_file.txt'] 
        self.app.get_absolute_path = MagicMock(return_value='/existing_file.txt')
        self.app.touch(['touch', 'existing_file.txt'])
        mock_zip_instance.writestr.assert_not_called()
        self.app.output_text.insert = MagicMock()
        self.app.touch(['touch', 'existing_file.txt'])
        self.app.output_text.insert.assert_called_once_with(tk.END, "Error: file already exists\n")

    def test_clear(self):
        self.app.log_action = MagicMock()
        self.app.clear()
        self.app.output_text.delete.assert_called_with('1.0', tk.END)
        self.app.log_action.assert_called_once_with("clear")

    def test_exit(self):
        self.app.log_action = MagicMock()
        self.app.root = MagicMock()
        self.app.exit();
        self.app.root.quit.assert_called_once();
        self.app.log_action.assert_called_once_with("exit")

    @patch('zipfile.ZipFile')
    def test_mkdir(self, mock_zipfile):
        self.app.log_action = MagicMock()
        mock_zip_file_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_file_instance
        parsed_command = ['mkdir', 'new_directory']
        self.app.mkdir(parsed_command)
        mock_zip_file_instance.mkdir.assert_called_once_with('new_directory')
        self.app.log_action.assert_called_once_with("mkdir new_directory")

    @patch('zipfile.ZipFile')
    def test_ls1(self, mock_zipfile):
        self.app.check_correct_arguments = MagicMock()
        self.app.log_action = MagicMock()
        mock_zip_file_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_file_instance
        mock_zip_file_instance.infolist.return_value = [
            zipfile.ZipInfo('dir1/file1.txt'),
            zipfile.ZipInfo('dir2/file2.txt'),
            zipfile.ZipInfo('dir1/'),
            zipfile.ZipInfo('dir2/subdir1/file3.txt'),
        ]
        parsed_command = ['ls']
        self.app.ls(parsed_command)
        self.app.output_text.insert.assert_any_call(tk.END, "dir1/\n")
        self.app.output_text.insert.assert_any_call(tk.END, "dir2/\n")
        self.app.log_action.assert_called_once_with("ls")

    @patch('zipfile.ZipFile')
    def test_ls2(self, mock_zipfile):
        self.app.check_correct_arguments = MagicMock()
        self.app.log_action = MagicMock()
        mock_zip_file_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_file_instance
        mock_zip_file_instance.infolist.return_value = [
            zipfile.ZipInfo('dir1/file1.txt'),
            zipfile.ZipInfo('dir2/file2.txt'),
             zipfile.ZipInfo('dir1/'),
            zipfile.ZipInfo('dir2/subdir1/file3.txt'),
        ]
        parsed_command = ['ls', 'dir1']
        self.app.ls(parsed_command)
        self.app.output_text.insert.assert_any_call(tk.END, "file1.txt\n")
        self.app.log_action.assert_called_once_with("ls")


if __name__ == '__main__':
    unittest.main()
