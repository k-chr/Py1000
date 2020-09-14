"""
Created on Mon Feb  3 20:57:22 2020

@author: Kamil Chrustowski
"""

import sys
from app import App
from typing import List

def main(args: List[str]):
    app = App(args)

if __name__ == '__main__':
    main(sys.argv)