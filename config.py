import os

class Config:
    TIMEOUT_SECONDS = 5

    SOURCE_FILE = 'main.cpp'
    EXECUTABLE = 'main'

    CXX = 'g++'
    DIALECT = '-std=c++11'

    SUCCESS = 0
    COMPILATION_ERROR = 1
    RUNTIME_ERROR = 2
    TIME_LIMIT_EXCEEDED = 3
    