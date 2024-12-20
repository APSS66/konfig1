# Shell Emulator

## Описание задания

Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС.
Эмулятор должен запускаться из реальной командной строки, а файл с
виртуальной файловой системой не нужно распаковывать у пользователя.
Эмулятор принимает образ виртуальной файловой системы в виде файла формата
tar. Эмулятор должен работать в режиме GUI.
Конфигурационный файл имеет формат xml и содержит:
-  Имя пользователя для показа в приглашении к вводу.
-  Путь к архиву виртуальной файловой системы.
-  Путь к лог-файлу
-  Путь к стартовому скрипту.
  
Лог-файл имеет формат csv и содержит все действия во время последнего сеанса работы с эмулятором. Для каждого действия указан пользователь.

Стартовый скрипт служит для начального выполнения заданного списка
команд из файла.

Необходимо поддержать в эмуляторе команды `ls`, `cd` и `exit`, а также
следующие команды:
1. `cp`.
2. `uptime`.
3. `find`
   
Все функции эмулятора должны быть покрыты тестами, а для каждой из
поддерживаемых команд необходимо написать 2 теста.

## Функции и настройки

## Функции

- **`ls`**: Показывает содержимое директории.Поддерживается показ содержимого сразу нескольких директорий.
- **`cd`**: Изменяет текущую директорию.
- **`exit`**: Выход из эмулятора.
- **`clear`**: Очистка экрана введенных команд.
- **`rm/rmdir`**: Удаление файла/директории.
- **`cp`**: Копирование файла (1 аргумент) в директорию (2 аргумент)
- **`uptime`**: Вывод времени работы терминала
- **`find`**: Поиск заданных файлов/директорий
При вводе путей можно использовать и относительные, и абсолютные пути. В путях поддерживаются следующие сокращения:
- `.`: Текущая директория
- `..`: Головная директория текущей
- `/`: Корневая директория

## Настройки
Настройки эмулятора задаются при помощи файла config.xml:
- Имя пользователя для показа в приглашении к вводу (тег user).
- Путь к архиву виртуальной файловой системы (тег vfs_path).
- Путь к лог-файлу (тег log_path)
- Путь к стартовому скрипту (тег startup_script).

## Сборка и запуск

Для сборки и запуска проекта в вашей системе должен быть установлен Python. Выполните следующие действия:

1. **Клонирование репозитория**: 
    ```bash
    git clone <repository-url>
    ```

2. **Перемещение в директорию проекта**:
    ```bash
    cd <project-directory>
    ```

3. **Конфигураця xml-файла**

4. **Запуск эмулятора**:
    ```bash
    python terminal.py```


## Примеры использования

![Примеры использования команды `ls`](/images/ls-test)

Примеры использования команды `ls`

![Примеры использования команды `cd`](/images/cd-test)

Примеры использования команды `cd`

![Примеры использования команды `cp`](/images/cp-test)

Примеры использования команды `cp`

![Примеры использования команды `uptime`](/images/uptime-test)

Примеры использования команды `uptime`

![Примеры использования команды `find`](/images/find-test)

Примеры использования команды `find`
## Результаты тестов

![Результаты прогона тестов](/images/tests-screen)
Все функции эмулятора были протестированы. Результаты тестов представлены на скриншоте выше

