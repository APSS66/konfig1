import unittest
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime
import zipfile
import terminal

class TestSimpleTerminalApp(unittest.TestCase):

    def setUp(self):
        self.root = MagicMock()
        self.config = {
            'user': 'S66',
            'vfs_path': 'filesys.zip',
            'log_path': 'log.csv',
            'startup_script': 'startup_script.txt'
        }
        self.app = terminal.SimpleTerminalApp(self.root, self.config)

    @patch('os.listdir')
    def test_validate_xml_success(self, mock_listdir):
        mock_listdir.return_value = ['filesys.zip', 'log.csv', 'startup_script.txt']
        result = self.app.validate_xml(self.config)
        self.assertTrue(result)

    @patch('os.listdir')
    def test_validate_xml_failure(self, mock_listdir):
        #mock_listdir.return_value = ['nani']
        mock_listdir.return_value = ['file1.txt', 'file2.txt', 'file3.txt']
        result = self.app.validate_xml(self.config)
        self.assertFalse(result)

    @patch('builtins.open', new_callable=mock_open)
    def test_log_action(self, mock_file):
        action = "test_action"
        self.app.log_action(action)
        mock_file.assert_called_once_with(self.app.log_path, mode='a', newline='')
        handle = mock_file()
        handle.write.assert_called_once_with("S66,{},{}\r\n".format(action, datetime.now().strftime('%H:%M')))

    # @patch('tkinter.Text.insert')
    # @patch('tkinter.Entry.get', return_value='test_command')
    # @patch('tkinter.Entry.delete')
    # def test_execute_command(self, mock_delete, mock_get, mock_insert):
    #     self.app.execute_command()
    #     mock_insert.assert_called_once_with(tk.END, ' test_commandn')
    #     mock_delete.assert_called_once()

    @patch('zipfile.ZipFile')
    def test_check_correct_folder_path_success(self, mock_zipfile):
        mock_zipfile.return_value.__enter__.return_value.infolist.return_value = [
            zipfile.ZipInfo('folder1/'),
            zipfile.ZipInfo('folder2/')
        ]
        result = self.app.check_correct_folder_path('folder1')
        self.assertTrue(result)

    @patch('zipfile.ZipFile')
    def test_check_correct_folder_path_failure(self, mock_zipfile):
        mock_zipfile.return_value.__enter__.return_value.infolist.return_value = [
            zipfile.ZipInfo('folder1/')
        ]
        result = self.app.check_correct_folder_path('folder2')
        self.assertFalse(result)

    @patch('zipfile.ZipFile')
    def test_check_correct_file_path_success(self, mock_zipfile):
        mock_zipfile.return_value.__enter__.return_value.infolist.return_value = [
            zipfile.ZipInfo('file1.txt'),
            zipfile.ZipInfo('file2.txt')
        ]
        result = self.app.check_correct_file_path('file1.txt')
        self.assertTrue(result)

    @patch('zipfile.ZipFile')
    def test_check_correct_file_path_failure(self, mock_zipfile):
        mock_zipfile.return_value.__enter__.return_value.infolist.return_value = [
            zipfile.ZipInfo('file1.txt')
        ]
        result = self.app.check_correct_file_path('file2.txt')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
