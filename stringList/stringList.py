"""
specialized operations on strings and lists
"""

from typing import Iterable
import logging


class FrontLoad:
    """perform specialized join/split operations on lists/strings that front-load the separator
    to the front of the string

    e.g. Markdown headings
    """
    @staticmethod
    def join(iterable: Iterable[str], sep: str) -> str:
        """Join an interable of strings and prepend the sep to the beginning of the string 
        """
        return sep + sep.join(iterable)

    @staticmethod
    def split(text: str, sep: str, maxsplit=-1) -> list[str]:
        """split text, which begins with the sep, into a list of strings"""
        if text.startswith(sep):
            front_load_split_list = text.split(sep=sep, maxsplit=maxsplit)[1:]
            return front_load_split_list
        
        # check if first character of the sep was cut off, e.g. if sep='\n### ' and the text begins with '### '
        if len(sep) > 1 and text.startswith(sep[1:]):
            front_load_split_list = ("\n" + text).split(sep=sep, maxsplit=maxsplit)[1:]
            return front_load_split_list
        
        logging.debug(f"The input text does not begin with the separator, FrontLoad.split was not necessary:\nsep: {sep}\n\ntext:{text}")
        return text.split(sep=sep,maxsplit=maxsplit)
    
