import sys
import os
import configparser
sys.path.append(os.path.join(os.path.dirname(__file__), '..\\..\\ExchangeApi'))
import bitflyer_api_wrapper as bitflyer
import coincheck_api_wrapper as coincheck
import gmo_api_wrapper as gmo

class TradeApi:
    #---------------------------------------------------
    # コンストラクタ
    #---------------------------------------------------
    def __init__(self, exchange_name):
        api_key, api_secret = self.__get_api_key(exchange_name)
        if exchange_name == 'bitFlyer':
            self.exchange = bitflyer.BitflyerAPIWrapper(api_key, api_secret, 'BTC_JPY')
        elif exchange_name == 'Coincheck':
            self.exchange = coincheck.CoincheckAPIWrapper(api_key, api_secret, 'btc_jpy')
        elif exchange_name == 'GMO':
            self.exchange = gmo.GmoAPIWrapper(api_key, api_secret, 'BTC')

    #---------------------------------------------------
    # APIキーとシークレットをファイルから読み出す
    #---------------------------------------------------
    def __get_api_key(self, exchange_name):
        path = os.path.dirname(os.path.abspath(__file__))
        inifile = configparser.SafeConfigParser()
        inifile.read(os.path.join(path, "api_key.ini"))
        api_key = inifile.get(exchange_name, 'key')
        api_secret = inifile.get(exchange_name, 'secret')
        return api_key, api_secret

    #---------------------------------------------------
    # 成行買い
    #---------------------------------------------------
    def buy_market(self, size):
        self.__order('MARKET', 'BUY', 0, size)

    #---------------------------------------------------
    # 指値買い
    #---------------------------------------------------
    def buy_limit(self, price, size):
        self.__order('LIMIT', 'BUY', price, size)

    #---------------------------------------------------
    # 指値買いIFDSTOP付き
    #---------------------------------------------------
    def buy_limit_with_stop(self, price, size, stop_price):
        self.exchange.send_parentorders_ifd_stop('BUY', price, size, stop_price)

    #---------------------------------------------------
    # 成行売り
    #---------------------------------------------------
    def sell_market(self, size):
        self.__order('MARKET', 'SELL', 0, size)

    #---------------------------------------------------
    # 指値売り
    #---------------------------------------------------
    def sell_limit(self, price, size):
        self.__order('LIMIT', 'SELL', price, size)

    #---------------------------------------------------
    # 指値売りIFDSTOP付き
    #---------------------------------------------------
    def sell_limit_with_stop(self, price, size, stop_price):
        self.exchange.send_parentorders_ifd_stop('SELL', price, size, stop_price)

    #---------------------------------------------------
    # 注文
    #---------------------------------------------------
    def __order(self, order_type, side, price, size):
        self.exchange.send_childorders(order_type, side, price, size)

    #---------------------------------------------------
    # STOP注文
    #---------------------------------------------------
    def stop_order(self, side, price, size):
        ltp = self.get_fx_ltp()
        if side == 'BUY' and price < ltp:
            print('price < ltp')
            return
        elif side == 'SELL' and price > ltp:
            print('price > ltp')
            return
        self.exchange.send_parentorders_simple_stop(side, price, size)

    #---------------------------------------------------
    # 注文全キャンセル
    #---------------------------------------------------
    def cancel_all_orders(self):
        self.exchange.cancel_all_child_orders()

    #---------------------------------------------------
    # Tickerを取得
    #---------------------------------------------------
    def get_ticker(self):
        ltp, bid, ask = self.exchange.get_ticker()
        return ltp, bid, ask

    #---------------------------------------------------
    # 板情報を取得
    #---------------------------------------------------
    def get_order_books(self):
        self.exchange.get_order_books()
        return

    #---------------------------------------------------
    # 現在のポジションの
    # 方向、合計数量、SWAPポイント、平均約定価格、損益分岐価格を取得
    #---------------------------------------------------
    def get_current_position(self):
        cur_positions = self.exchange.get_positions()
        pos_sum = 0
        swap_sum = 0
        average = 0
        price_sum = 0

        for pos in cur_positions:
            pos_sum += float(pos['size'])
            swap_sum += float(pos['swap_point_accumulate'])
            price = float(pos['price'])
            size = float(pos['size'])
            price_sum += price
            average += (price * size)

        if pos_sum != 0:
            average /= pos_sum

        if len(cur_positions) == 0 :
            side = '-'
            even_price = 0
        elif cur_positions[0]['side'] == 'BUY' :
            side ='L'
            even_price = average + swap_sum
        else:
            side = 'S'
            even_price = average - swap_sum
        
        return side, pos_sum, swap_sum, average, even_price
