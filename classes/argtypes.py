#!/usr/bin/env python3
import os


def dir_path(string: str):
    if os.path.exists(string):
        if os.path.isdir(string):
            return string
        raise NotADirectoryError(string)
    raise FileNotFoundError(string)


def file_path(string: str):
    if os.path.exists(string):
        if not os.path.isdir(string):
            return string
        print(string, "is directory, not a file!")
        exit(1)
    raise FileNotFoundError(string)


def interface(string: str):
    try:
        subprocess.check_output(['ifconfig', string], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError: # Interfejs nie istnieje
        raise_error("Specified interface doesn't exists or is not up")
    return string


if __name__ == "__main__":
    print("Ten skrypt jest jedynie do importu!")

