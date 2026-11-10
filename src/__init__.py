# AI Co-Scientist package initialization

__version__ = "0.1.0"
__author__ = "AI Co-Scientist Team"

def __getattr__(name):
    if name == 'AICoScientist':
        from .main import AICoScientist
        return AICoScientist
    raise AttributeError(name)

__all__ = ['AICoScientist']

