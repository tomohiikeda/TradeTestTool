import sys
from PyQt5 import QtCore, QtWidgets, uic
import os
import trade_api
import pyperclip

class MainWindow:

    #exchange = 'bitFlyer'
    exchange = 'Coincheck'
    #exchange = 'GMO'

    #------------------------------------------------
    # コンストラクタ
    #------------------------------------------------
    def __init__(self):
        self.trade = trade_api.TradeApi(self.exchange)

    #------------------------------------------------
    # 初期化処理
    #------------------------------------------------
    def init(self):
        ui_path = os.path.dirname(os.path.abspath(__file__))
        Form, Window = uic.loadUiType(os.path.join(ui_path, "main_window.ui"))
        app = QtWidgets.QApplication([])
        window = Window()
        self.form = Form()
        self.form.setupUi(window)
        window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        window.show()

        # UI初期設定
        self.__update_price()
        self.form.label_exchange_name.setText(self.exchange)
        self.form.plainTextEdit_size.setPlainText('0.01')
        self.form.plainTextEdit_price.setPlainText('1000000')
        self.form.plainTextEdit_profit.setPlainText('1000000')
        self.form.plainTextEdit_losscut.setPlainText('1000000')

        # 1sec間隔のTimer
        timer_0 = QtCore.QTimer()
        timer_0.setInterval(1000)
        timer_0.timeout.connect(self.__update_price)
        #timer_0.start()

        # ハンドラ登録
        self.form.pushButton_Buy.clicked.connect(self.__on_clicked_buy)
        self.form.pushButton_Sell.clicked.connect(self.__on_clicked_sell)
        self.form.pushButton_test.clicked.connect(self.__on_clicked_test)

        #self.form.pushButton_test.clicked.connect(self.test)
        self.form.pushButton_cancel.clicked.connect(self.trade.cancel_all_orders)

        sys.exit(app.exec_())

    #------------------------------------------------
    # LTPの更新処理
    #------------------------------------------------
    def __update_price(self):
        ltp, bid, ask = self.trade.get_ticker()
        self.form.label_bid.setText('{:,.0f}'.format(bid))
        self.form.label_ask.setText('{:,.0f}'.format(ask))
        return

    #------------------------------------------------
    # 買いボタンクリックハンドラ
    #------------------------------------------------
    def __on_clicked_buy(self):
        ltp, bid, ask = self.trade.get_ticker()
        print(ltp, bid, ask)
        self.trade.buy_limit(ask, 0.01)

    #------------------------------------------------
    # 売りボタンクリックハンドラ
    #------------------------------------------------
    def __on_clicked_sell(self):
        ltp, bid, ask = self.trade.get_ticker()
        print(ltp, bid, ask)
        self.trade.sell_limit(bid, 0.01)

    #------------------------------------------------
    # テストボタンクリックハンドラ
    #------------------------------------------------
    def __on_clicked_test(self):
        ltp, bid, ask = self.trade.get_ticker()
        print(ltp, bid, ask)
        return
