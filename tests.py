import unittest
from emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        config = {
            'user': 'test_user',
            'vfs_path': 'virtual_filesystem.zip',
            'log_path': 'log.csv',
            'startup_script': 'startup_script.txt'
        }
        self.emulator = ShellEmulator(config)

    def test_ls(self):
        # Здесь нужно добавить логику тестирования команды ls
        self.emulator.ls([])
        # Добавьте проверки обещаемого вывода

    def test_cd(self):
        self.emulator.cd(['..'])
        self.assertEqual(self.emulator.current_directory, '..')

    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.emulator.exit([])

    # Дополните тестами другие команды

if __name__ == '__main__':
    unittest.main()