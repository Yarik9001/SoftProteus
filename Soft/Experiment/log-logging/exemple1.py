import logging

mylogs = logging.getLogger(__name__)
mylogs.setLevel(logging.DEBUG)
file = logging.FileHandler("app.log")
file.setLevel(logging.INFO)
fileformat = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file.setFormatter(fileformat)
mylogs.addHandler(file)

stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
streamformat = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream.setFormatter(streamformat)


mylogs.addHandler(stream)

mylogs.debug("The debug")
mylogs.info("The info")
mylogs.warning("The warn")
mylogs.error("The error")
mylogs.critical("The critical")