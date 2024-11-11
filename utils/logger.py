import logging

#logger

loggin.basicConfig(level=logging.INFO,
                   fomrmat = "%(asctime)s %(levelname)s - %(message)s",
                   handlers = [
                       logging.FileHandler("server.log"),
                       logging.StreamHandler()
                       
                   ]
)

def get_logger(name):
    return logging.getLogger(name)