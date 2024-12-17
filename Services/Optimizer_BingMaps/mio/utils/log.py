import logging

def init_log() -> None:
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  # Setup logging in console
  fmtConsole = logging.Formatter("[%(asctime)s][%(levelname)s][%(process)04X:%(thread)04X][%(filename)s][%(funcName)s_%(lineno)d]: %(message)s")
  #consoleHandler = logging.StreamHandler()
  #consoleHandler.setFormatter(fmtConsole)
  #logger.addHandler(consoleHandler)

  # Setup logging in Azure Application Insights
  import os
  from opencensus.ext.azure.log_exporter import AzureLogHandler
  azureHandler = AzureLogHandler(connection_string=os.getenv("MIO_APPINSIGHT_CONN_STRING"))
  azureHandler.setFormatter(fmtConsole)
  logger.addHandler(azureHandler)

  # Setup logging in file
  #import os
  #import datetime
  #fmtFile = logging.Formatter("[%(asctime)s][%(levelname)s][%(process)04X:%(thread)04X][%(filename)s][%(funcName)s_%(lineno)d]: %(message)s")
  #fmtFile = logging.Formatter("%(message)s")
  #fileHandler = logging.FileHandler("log-{}-{:04X}.txt".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), os.getpid()))
  #fileHandler.setFormatter(fmtFile)
  #logger.addHandler(fileHandler)

  logger.info("Logger initialized")
