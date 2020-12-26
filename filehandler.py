import csv
import time
import os


class FileHandler():

    """
    Initialise le buffer et set le chemin du fichier
    INPUT: <str> path_to_file, path du fichier à ouvrir
    """
    def __init__(self,path_to_file):
        self.file = path_to_file
        self.buffer=[]
        self.__check_file_exist()
    """
    Check if the file doesn't exist create it
    """
    def __check_file_exist(self):
        if not os.path.exists(self.file):
            open(self.file,"w").close()
    """
    Ouvre le fichier en lecture 
    OUTPUT: <_io.TextIOWrapper>, Fichier ouvert en mode lecture
    """
    def __open_in_read_mode(self):
        return open(self.file,'r')



    """
    Crée un csv reader et appelle la fonction pour lire les données du fichier averages
    """
    def read_averages(self):
        with self.__open_in_read_mode() as read_file:
            reader = csv.reader(read_file)
            self.__load_data_averages(reader)

    """
    Crée un csv reader et appelle la fonction pour lire les données du fichier tickers
    """
    def read_current_price(self):
        with self.__open_in_read_mode() as read_file:
            reader = csv.reader(read_file)
            self.__load_data_current(reader)

            
    """
    Ouvre le fichier en écriture à la fin du fichier 
    OUTPUT: <_io.TextIOWrapper>, Fichier ouvert en mode écriture à la fin du fichier
    """
    def __open_in_write_mode(self):
        return open(self.file,'a',newline="")


    """
    Ajoute à la fin de son buffer la dernière value constatée (soit un average, soit un current_price)
    INPUT: <int/float> value, current_price
    """
    def append_value_to_buffer(self,value):
        self.buffer.append(value)



    """
    Ecris sur le fichier average.csv  la date et notre dernière valeur  current_average
    INPUT: <str> value, notre dernier current_average
           <str> date, la date 
    """
    def write_average(self,value,date):
        with self.__open_in_write_mode() as write_file:
            writer = csv.writer(write_file)
            writer.writerow([date, value])


    """
    Ecris sur le fichier tickers.csv la date et  notre dernière valeur current_price
    INPUT: <str> value, notre dernier current_price
           <str> date, la date 
    """
    def write_ticker_price(self,ticker,date):
        with self.__open_in_write_mode() as write_file:
            writer = csv.writer(write_file)
            writer.writerow([date, "current", ticker["c"][0]])
            writer.writerow(["", "lowest", ticker["l"][1]])
            writer.writerow(["", "highest", ticker["h"][1]])

    """
    Ecris sur le fichier ledger.csv la date et  notre dernier order
    INPUT: <str> ledger, notre dernier ordre
           <str> date, la date 
    """
    def write_ledger_information(self,ledger,date,info,type_sell="",):
        with self.__open_in_write_mode() as write_file:
            writer = csv.writer(write_file)
            writer.writerow([date, type_sell,ledger["descr"]["order"], ledger["txid"][0], info])

    """
    Load dans le buffer du fichier averages les dernières moyennes
    INPUT: <csvreader> reader, le csv reader qui nous permet de lire le fichier csv
    """
    def __load_data_averages(self,reader):
        for row in reader :
            if row and not row[0].isalpha() : 
                self.buffer.append(float(row[1]))

    """
    Load dans le buffer du fichier tickers les derniers prix
    INPUT: <csvreader> reader, le csv reader qui nous permet de lire le fichier csv 
    """
    def __load_data_current(self,reader):
        for row in reader :
            if "current" in row:
                self.buffer.append(float(row[2]))
