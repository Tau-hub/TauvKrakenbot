# coding: utf-8
from keys import API_PRIVATE_KEY, API_PUBLIC_KEY
from display import display
from filehandler import FileHandler
import requests
import hashlib
import hmac
import os
import base64
import time
import json
import logging
import math


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(THIS_DIR,"logs")
logging.basicConfig(filename=LOG_FILE,filemode="a",level=logging.INFO, format='%(asctime)s:  %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
#Nos différents types de method que nous pouvons appeler
api_public = {"Time", "Assets", "Ticker", "AssetPairs" "OHLC", "Depth", "Trades", "Spread"}
api_private = {"Balance", "TradeBalance", "OpenOrders", "ClosedOrders", "QueryOrders", "TradesHistory", "QueryTrades", "OpenPositions", "Ledgers", "QueryLedgers", "TradeVolume", "AddExport", "ExportStatus", "RetrieveExport", "RemoveExport", "GetWebSocketsToken"}
api_trading = {"AddOrder", "CancelOrder"}
api_funding = {"DepositMethods", "DepositAddresses", "DepositStatus", "WithdrawInfo", "Withdraw", "WithdrawStatus", "WithdrawCancel", "WalletTransfer"}


"""
Ma classe définit l'API kraken pour faire nos requetes
"""
class KrakenApi(): 

    """
    Initialise toutes les variables de la classe

    INPUT : <str> averages, path du fichier averages
            <str> ledger, path du fichier averages  
            <str> ticker, path du fichier averages
            <bool> state, indique l'état dans lequel on est : achat ou vente
    """
    def __init__(self, averages, ledger,tickers, state):
        self.averages = FileHandler(averages)
        self.ledger = FileHandler(ledger)
        self.tickers = FileHandler(tickers)
        self.api_private_key = base64.b64decode(API_PRIVATE_KEY)
        self.api_public_key = API_PUBLIC_KEY
        self.session = requests.session()
        self.domain = "https://api.kraken.com"
        self.private_path = "/0/private/"
        self.public_path = "/0/public/"
        self.state = state
        self.__init_files()

    """
    Récupère les informations inscrites dans les fichiers et initialise les buffers. Indique aussi à l'utilisateur si un ordre est actuellement placé ou non
    """
    def __init_files(self):
        self.averages.read_averages()
        self.tickers.read_current_price()
        order = self.__get_open_orders()["open"]
        if not order:
            logging.info("No order placed")
        else :
            logging.info("Order placed")

    """
    Récupère le temps sur l'api Kraken
    OUPUT: <str>,  retourne la date 
    """
    def __get_time(self):
        result_time = self.__request_kraken("Time")
        return time.strftime('%d-%m-%Y %H:%M', time.localtime(result_time["unixtime"]))
    """
    Récupère notre balance account, les assets pairs disponible et tous les tickers respectifs
    """
    def info(self):
        logging.info(self.__get_time())
        self.__get_balance()
        self.__get_assets_pairs()
        self.__get_tickers_list()
        
    """
    Fais une requête pour nous indiquer si nous avons des odres ouverts

    OUTPUT: <dict>, retourne les informations de la requete sous forme de dictionnaire (voir __request_kraken)
    """
    def __get_open_orders(self):
        return self.__request_kraken("OpenOrders")
    
        
    """
    Fais une requête pour nous indiquer si nous avons des odres fermés

    OUTPUT: <dict>, retourne les informations de la requete sous forme de dictionnaire (voir __request_kraken)
    """
    def __get_closed_orders(self):
        return self.__request_kraken("ClosedOrders")


    """
    Fais une requête d'un ticker particulier

    INPUT: <str>, ticker, example "ADAEUR"
    OUTPUT: <float>, retourne en float la valeur actuelle d'un ticker
    """
    def __get_price_ticker(self,ticker):
        ticker = self.__request_kraken("Ticker",["pair={}".format(ticker)])[ticker]
        self.tickers.write_ticker_price(ticker,self.__get_time())
        return float(ticker["c"][0])

    """
    Effectue la requête de tous les assets pair et l'assigne à une variable de classe
    """
    def __get_assets_pairs(self):
        self.result_assets_pairs= self.__request_kraken("AssetPairs")

    """
    Effectue les requête de tous les tickers grace aux assets pair récupérés et l'assigne à une variable de classe
    """
    def __get_tickers_list(self):
        self.tickers_list={}
        for ticker in self.result_assets_pairs.keys() :
            self.tickers_list.update(self.__request_kraken("Ticker",["pair={}".format(ticker)]))

        
    
    """
    Fais la requête de notre balance et affiche toutes les currencies disponibles 
    """
    def __get_balance(self):
        self.balances = self.__request_kraken("Balance")
        for balance in self.balances.keys() :
            logging.info("Currency : {} Balance : {}".format(balance, self.balances[balance]))

    """
    OUTPUT: <unsigned int>, Retourne un nonce correct 
    """
    def __get_nonce(self): 
        return str(int(time.time()*1000))

    """
    Retourne les headers Api-key et Api-sign demandés par l'API

    INPUT: <HMAC> api_hmacsha512,  le hmac512 de l'api sign
    OUTPUT:  <dict>, retourne dictionnaire contenant le header
    """
    def __set_headers(self,api_hmacsha512) :
            return {
                'Api-Key' : self.api_public_key,
                'Api-Sign' :  base64.b64encode(api_hmacsha512.digest())    
            }

    """
    Vérifie si la balise error n'est pas vide dans ce cas affiche l'erreur. Retourne la requete

    INPUT: <request> request, effectuée
    OUTPUT: <dict>, retorune le dictionnaire de la requete avec uniquement le resultat
    """
    def __check_errors(self,request):
        if request["error"]:
            logging.error("Your request failed ! reason={}".format(request["error"]))
        return request["result"]

    """
    Encode en utf-8 pour utiliser les hashlib et le hmac

    INPUT: <str> string, variable à encoder
    OUTPUT: <bytes>,  du string passé en parametre
    """
    def __encode_str(self,string) :
        return string.encode("utf-8")
        
    """
    Prepare la requete pour l'API de Kraken, fais toutes les opérations de hash et de préparation de la post_data
    Si la requete echoue et retourne une exception on rappelle la fonction pour ne pas éteindre le programme
    Si la requete est bonne, on return la requete sous format de json, et la fonction check_error vérifie s'il y'a une erreur. 

    INPUT: <str> api_method, La method indiquée par l'utilisateur
           <[str,str,....,str]> api_data (optional) : les data envoyées si l'utilisateur en a précisé
    OUTPUT: <dict>, Retourne sous forme de dictionnaire la data de la request
    """
    def __request_kraken(self,api_method,api_data=[]) :
        if api_method in api_private or api_method in api_trading or api_method in api_funding:
            api_nonce = self.__get_nonce()
            api_postdata =  self.__encode_str('&'.join(api_data) + "&nonce=" + api_nonce)
            api_sha256 = hashlib.sha256(self.__encode_str(api_nonce) + api_postdata).digest()
            api_hmac512 = hmac.new(self.api_private_key, self.__encode_str(self.private_path) + self.__encode_str(api_method) + api_sha256, hashlib.sha512)
            headers = self.__set_headers(api_hmac512)
            URL = self.domain + self.private_path + api_method 
            logging.info("Requesting URL :  {}".format(URL))
            try : 
                request = self.session.post(URL, headers=headers,data=api_postdata)
                return self.__check_errors(self.__json_data(request))
            except Exception as ex : 
                logging.error("Exception occured, restarting.... reason={}".format(ex))
                return self.__request_kraken(api_method,api_data)
        else :
            URL = self.domain + self.public_path + api_method + '?' + '&'.join(api_data)
            logging.info("Requesting URL :  {}".format(URL))
            try : 
                request = self.session.get(URL)
                return self.__check_errors(self.__json_data(request))
            except Exception as ex : 
                logging.error("Exception occured, restarting.... reason={}".format(ex))
                return self.__request_kraken(api_method,api_data)
           

    
    """
    Transforme notre requete en format json

    INPUT: <requests.models.Response> request, notre requete raw
    OUTPUT: <dict>, notre requete en format dictionnaire
    """
    def __json_data(self,request):
            return json.loads(request.text)

    
    """
    Place un ordre d'achat ou de vente

    INPUT: <str> api_method 
           <str> api_data
    OUTPUT: <dict>, notre requete en format dictionnaire
    """
    def __placeorders(self,api_method,api_data):
          logging.info("Method  : {} , orders : {}".format(api_method,api_data))
          api_data = [data for data in api_data.split()]
          return self.__request_kraken(api_method,api_data)
    

    """
    Loop dans lequel on effectue nos opérations pour savoir si on achète ou si l'on vend
    On effectue tout d'abord la requete pour obtenir le dernier prix de notre ticker
    Si on a assez d'élement dans notre tableau des ticker on calcul une moyenne
    Si on a assez de moyenne et que nous n'avons pas d'orders on regarde si nos trading rules sont respectées 
    Dans ce cas on place un ordre d'achat ou de vente selon notre état.

    INPUT:  <int> index_range, le nombre de valeurs à prendre en considération pour nos moyennes
            <str> ticker, le nom du ticker que l'on veut utiliser pour nos opérations 
            <int/float> buy_price (optional), le dernier prix d'achat qu'on a effectué
            <float> profit_percentage (optional), le pourcentage de gain que l'on souhaite pour vendre
            <float> loss_percentage (optional), le pourcentage que l'on souhaite pour ne pas perdre trop d'argent
            <int/float> balance (optional), le montant de départ de notre bot pour les achats / ventes
            <float> min_volume (optional), le volume minimal pour l'achat de cette monnaie
    """
    def loop(self,index_range,ticker,buy_price=0.0,profit_percentage=1.01,loss_percentage=0.98,balance=5,sleep_time=5):
        logging.info("Entering in loop mode")
        fees_percentage = 0.997
        sell_price = buy_price * profit_percentage
        stop_loss_price = buy_price * loss_percentage
        while True:
            logging.info("\nNew request")
            logging.info("Current balance used for buying/selling : {}".format(balance) )
            if buy_price != 0 and self.state == True :
                logging.info("Last price bought : {}  Needed to sell : {}, Loss selling {}".format(buy_price,sell_price,stop_loss_price))
            
            current_price = self.__get_price_ticker(ticker)
            self.tickers.append_value_to_buffer(current_price)
            logging.info( "{} : {}".format(ticker,current_price))

            buffer_tickers = self.tickers.buffer
            length_buffer_tickers = len(buffer_tickers)


            if length_buffer_tickers >= index_range:
                buffer_tickers = buffer_tickers[-index_range:]
                current_average = sum(buffer_tickers)/len(buffer_tickers)  
                self.averages.append_value_to_buffer(current_average)
                self.averages.write_average("{:.6f}".format(current_average), self.__get_time())

            buffer_average = self.averages.buffer[-index_range:]
            length_buffer_average = len(buffer_average)
            logging.info("BUFFER AVERAGE : {}".format(buffer_average))
            logging.info("BUFFER TICKERS : {}".format(buffer_tickers))
            if not self.__get_open_orders()["open"] :
                if length_buffer_average  >= index_range :
                    trading_rules=True
                    if not self.state:
                        #Si on a pas d'order et qu'on souhaite acheter,
                        #On parcourt de 0 à n-1 pour vérifier si chaque élément n'est pas inférieur à son suivant nos règles de trading ne sont pas remplies
                        # , dans ce cas on a un graphe descendant et on break pour ne pas acheter(prix en baisse)
                        for i in range(0, index_range-1) :
                            if not buffer_average[i] < buffer_average[i+1]  :
                                trading_rules=False
                                break
                        if trading_rules :
                            volume = balance/current_price
                            details_order = "volume bought : {} at price : {} current_balance {}".format(volume,current_price,balance)
                            order = self.__placeorders("AddOrder","pair={} type=buy ordertype=market volume={:.8f}".format(ticker, volume))
                            self.ledger.write_ledger_information(order,self.__get_time(),details_order)
                            buy_price = current_price
                            sell_price = buy_price * profit_percentage
                            stop_loss_price = buy_price * loss_percentage
                            balance= balance * fees_percentage
                            sleep_time = 5
                            self.state = True
                    else:
                        for i in range(0, index_range-1) :
                            if not buffer_average[i] > buffer_average[i+1]  :
                                trading_rules=False
                                break
                        if trading_rules and (current_price >= sell_price  or current_price <= stop_loss_price):
                            current_percentage = current_price / buy_price
                            balance = balance * current_percentage 
                            volume = balance/current_price
                            balance = balance * fees_percentage
                            details_order = "volume sold : {} at price : {}  current_balance {}".format(volume,current_price,balance)
                            order = self.__placeorders("AddOrder", "pair={} type=sell ordertype=market volume={:.8f}".format(ticker, volume))
                            towrite_percentage = 100.0 * abs(1.0 - current_percentage)
                            if current_price >= sell_price :
                                details_order += " profit percentage : {:.2f}%".format(towrite_percentage)
                                logging.info("sell price(profit) :  {}, current_price : {} ".format(sell_price,current_price))
                                self.ledger.write_ledger_information(order,self.__get_time(),details_order,"profit")
                            elif current_price <= stop_loss_price :
                                details_order += " loss percentage : {:.2f}%".format(towrite_percentage)
                                logging.info("sell price(loss) :  {}, current_price : {} ".format(stop_loss_price,current_price))
                                self.ledger.write_ledger_information(order,self.__get_time(),details_order,"loss")
                            self.state = False
                            sleep_time = 10
                    
                    
                    


            time.sleep(60*sleep_time)

display()
averages_path = os.path.join(THIS_DIR,"averages.csv")
ledger_path = os.path.join(THIS_DIR,"ledger.csv")
tickers_path = os.path.join(THIS_DIR,"tickers.csv")
kraken = KrakenApi(averages_path,ledger_path,tickers_path,False)
kraken.info()
try : 
    kraken.loop(5,"ADAEUR",profit_percentage=1.01,loss_percentage=0.97, balance=19.43,sleep_time=10)
except Exception as ex : 
    logging.error("An error occured and the bot crashed ! reason={}".format(ex))
