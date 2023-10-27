from abc import ABC
from utils import Utils
import random

class Proxy(ABC):
    """
    Interface for classes that implement proxy support
    """
    supported_proxy_protocols = ["http", "https", "socks4", "socks5"]

    @classmethod
    def write_proxy_line(cls, proxy_type:str, proxy_ip:str, proxy_port:int, proxy_user:str = None, proxy_pass:str = None) -> str:
        """
        Write a correctly formatted proxy line for proxies.txt file
        """
        proxy_type = None if proxy_type == "http" else proxy_type

        if (proxy_user is not None and proxy_pass is not None):
            auth = True
        elif (proxy_user is None and proxy_pass is None):
            auth = False
        else:
            raise ValueError("Invalid Parameters. If proxy has auth, make sure to provide username and password")

        return f"{proxy_type + ':' if proxy_type else ''}{proxy_ip}:{proxy_port}{':' + proxy_user + ':' + proxy_pass if auth else ''}"

    @classmethod
    def check_proxies_file_format(cls, file_path: str) -> bool:
        """
        Makes sure proxies.txt file format is good before checking/using proxies
        """
        try:
            f = open(file_path)
        except FileNotFoundError:
            raise FileNotFoundError("files/proxies.txt path not found. Create it, add proxies and try again")

        lines = f.readlines()
        f.close()

        for i, line in enumerate(lines):
            line = Utils.clear_line(line)
            line_number = i + 1

            # make sure no line is empty
            if line == "":
                raise SyntaxError("Please remove the empty line", (
                    file_path,
                    line_number,
                    None,
                    line
                ))

            try:
                proxy_type_provided, proxy_type, proxy_ip, proxy_port, proxy_user, proxy_pass = cls.get_proxy_values(line)
            except ValueError as e:
                raise SyntaxError(str(e), (
                    file_path,
                    line_number,
                    None,
                    line
                ))

            # make sure proxy_type is supported
            if proxy_type not in cls.supported_proxy_protocols:
                raise SyntaxError("Proxy type not supported", (
                    file_path,
                    line_number,
                    None,
                    line
                ))

            # validate proxy_port
            if not (0 <= proxy_port and proxy_port <= 65536):
                raise SyntaxError("Proxy port must be between 0 and 65536", (
                    file_path,
                    line_number,
                    None,
                    line
                ))

        # if 0 proxy found, display error message
        if len(lines) == 0:
            raise Exception("No proxy found in files/proxies.txt. Please add some and try again")

        return True

    @classmethod
    def get_proxy_values(cls, line: str) -> tuple:
        """
        Gets all proxy values from a line according to different line formats
        """
        num_item = len(line.split(":"))

        proxy_type = None
        proxy_user = None
        proxy_pass = None

        # get proxy_type, proxy_ip, proxy_port, proxy_user (if provided), proxy_pass (if provided)
        if num_item in [2, 4]:
            proxy_type_provided = False
            proxy_type = "http"
            proxy_ip = line.split(":")[0]
            proxy_port = line.split(":")[1]
            if num_item == 4:
                proxy_user = line.split(":")[2]
                proxy_pass = line.split(":")[3]
        elif num_item in [3, 5]:
            proxy_type_provided = True
            proxy_type = line.split(":")[0].lower()
            proxy_ip = line.split(":")[1]
            proxy_port = line.split(":")[2]
            if num_item == 5:
                proxy_user = line.split(":")[3]
                proxy_pass = line.split(":")[4]
        else:
            raise ValueError("Incorrect proxy line format")

        try:
            proxy_port = int(proxy_port)
        except:
            raise ValueError("Proxy port must be a number")

        return proxy_type_provided, proxy_type, proxy_ip, proxy_port, proxy_user, proxy_pass

    @classmethod
    def get_proxies(cls, proxy_type: str, proxy_ip: str, proxy_port: int, proxy_user: str = None, proxy_pass: str = None) -> dict:
        """
        Returns a dict of proxies
        """
        if (proxy_user is not None and proxy_pass is not None):
            auth = True
        elif (proxy_user is None and proxy_pass is None):
            auth = False
        else:
            raise ValueError("Invalid Parameters. If proxy has auth, make sure to provide username and password")

        if auth:
            proxies = { "all://": f"{proxy_type}://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}/" }
        else:
            proxies = { "all://": f"{proxy_type}://{proxy_ip}:{proxy_port}/" }

        return proxies

    @classmethod
    def get_random_proxies(cls, proxies_file_path:str) -> dict:
        """
        Gets random proxies dict from proxies.txt file for httpx module
        """
        try:
            f = open(proxies_file_path, 'r')
        except FileNotFoundError:
            raise FileNotFoundError("files/proxies.txt path not found. Create it, add proxies and try again")

        proxies_list = f.readlines()
        proxies_list = [*set(proxies_list)] # remove duplicates

        if len(proxies_list) == 0:
            raise Exception("No proxies found in files/proxies.txt. Please add some and try again")

        # get random line
        random_line = proxies_list[random.randint(0, len(proxies_list) - 1)]
        random_line = Utils.clear_line(random_line)
        # get proxies dict for httpx module
        proxy_type_provided, proxy_type, proxy_ip, proxy_port, proxy_user, proxy_pass = cls.get_proxy_values(random_line)
        proxies = cls.get_proxies(proxy_type, proxy_ip, proxy_port, proxy_user, proxy_pass)

        return proxies