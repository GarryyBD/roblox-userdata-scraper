import os

class Utils():
    """
    Utility functions
    """
    @staticmethod
    def ensure_directories_exist(directories):
        """
        Creates directories if they don't exist
        """
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

    @staticmethod
    def ensure_files_exist(files):
        """
        Creates files if they don't exist
        """
        for file in files:
            if not os.path.exists(file):
                with open(file, 'w'):
                    pass

    @staticmethod
    def clear_line(line: str) -> str:
        """
        Clears a line from spaces, tabs and newlines
        """
        return line.replace("\n", "").replace(" ", "").replace("\t", "")

    @staticmethod
    def return_res(response) -> str:
        """
        Returns a string with the response text and status code
        """
        return response.text + " HTTPStatus: " + str(response.status_code)