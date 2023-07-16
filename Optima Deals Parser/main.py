import parser
from credentials import COMPANY, USER, PASSWORD, ID
def main():
    OptimaClientsBro = parser.GetOptimaInfo(COMPANY, USER, PASSWORD, ID)

    OptimaClientsBro.make_request()


if __name__ == '__main__':
    main()
