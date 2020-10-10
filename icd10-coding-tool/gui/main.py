import sys
sys.path.append("..")
from code_extract.main import call_extract

if __name__ == "__main__":
    a = input("testing")
    call_extract(a)