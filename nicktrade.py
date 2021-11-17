# *********************************************************************
#   NICKTRADE v0.1
#   2021 NICK T LIVENGOOD
#   NEVER, EVER GIVE UP.
# *********************************************************************

# *********************************************************************
#   CONFIGURATION
# *********************************************************************

# ----- ALPHA VANTAGE -----
g_apikey = "demo" # alpha vantage API key:
apikey = g_apikey # legacy code support

# ----- KELTNER CHANNEL -----
g_kc_smoothing = 2
g_kc_period = 10
g_kc_banding = 0.05        # default value for the band multiplier

# ----- VALIDATION -----
g_val_slope_sp = 2         # desired slope for the security
g_val_slope_dt = 10
g_val_banding = 0.02        # default value for the band multiplier
g_val_dKU = 0

# ----- PLOT SAVE -----
plot_folder = "./plot/"
csv_folder = "./csv/"

from numpy.core.fromnumeric import size
from requests import get
import matplotlib.pyplot as plt
import numpy
import csv

class security:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = {"timestamp": [], "open": [], "high": [], "low": [], "close": []}  # set up structure for later
        #self.data = {}
        self.timestamp = []
        self.fetch_data()

    def fetch_data(self):
        # feetch new data from the AlphaVantage API

        url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + str(self.symbol) + "&apikey=" + g_apikey
        for i in range(3):
            try:
                print(str("Fetching data for " + self.symbol) + ":  ", end="", flush=True)
                tsd = get(url).json()
                print("Done.")
                break
            except:
                print("Communication error. Trying again... (Attempt #" + str(i) + ")")

        # parse JSON data into a friendly form and load into data object
        # grab meta information
        self.data["last updated"] = tsd['Meta Data']["3. Last Refreshed"]

        timestamp, open, high, low, close = ([] for i in range(5))


        for i in tsd["Time Series (Daily)"]:
            timestamp.append(i)
            open.append(float(tsd['Time Series (Daily)'][i]["1. open"]))
            high.append(float(tsd['Time Series (Daily)'][i]["2. high"]))
            low.append(float(tsd['Time Series (Daily)'][i]["3. low"]))
            close.append(float(tsd['Time Series (Daily)'][i]["4. close"]))

        # reverse data
        timestamp.reverse()
        open.reverse()
        high.reverse()
        low.reverse()
        close.reverse()

        self.data["timestamp"] = timestamp
        self.data["open"] = open
        self.data["high"] = high
        self.data["low"] = low
        self.data["close"] = close

        #print(tsd['Time Series (Daily)'].keys())
        # clean up
        del tsd, timestamp, open, high, low, close, url
        return

    def indicator_kc(self, band_multiplier=g_kc_banding):
        if "kc_lower" or "kc_upper" or "ema" not in self.data: # make sure all arrays are present for loading
            self.data.update({"kc_lower": [], "kc_upper": [], "ema": []})

        # calculate Keltner Channel values and add to dictionary

        #d = self.tsd
        #d = self.data["close"] # grab close data
        data_close = list(self.data["close"])
        ema = {} # blank array for ema data
        kc_upper = {}
        kc_lower = {}

        smooth = g_kc_smoothing
        period = g_kc_period
        bm = band_multiplier

        m = (smooth/(1+period)) # multiplier

        # --- calculate ema ---
        # empty data for first period
        for i in range(0,period):
            ema[i] = numpy.nan
            kc_lower[i] = numpy.nan
            kc_upper[i] = numpy.nan

        # calculate ema for first period
        ema[period-1] = float(sum(data_close[0:period-2]) / (period-2))
        kc_upper[period-1] = float(ema[period-1]+ema[period-1]*bm)
        kc_lower[period-1] = float(ema[period-1]-ema[period-1]*bm)

        i = period

        for v in data_close[i:]:
            # data_close[i] # today's price
            # ema[i-1] # yesterday's ema
            ema[i]=(data_close[i]*m)+ema[i-1]*(1-m)
            kc_upper[i] = (ema[i]+ema[i]*bm)
            kc_lower[i] = (ema[i]-ema[i]*bm)

            i = i+1

        # convert ema to array and store
        ema_array = []
        kc_upper_array = []
        kc_lower_array = []

        for i in ema:
            ema_array.append(ema.get(i))
            kc_upper_array.append(kc_upper.get(i))
            kc_lower_array.append(kc_lower.get(i))
        self.data.update({"ema": ema_array, "kc_upper": kc_upper_array, "kc_lower": kc_lower_array})
        del ema, data_close, ema_array, kc_upper, kc_upper_array, kc_lower, kc_lower_array
        return

    def plot(self, silent=False):
        timestamp = {}

        plotDataY = []
        plotDataX = [numpy.datetime64(i) for i in list(self.data["timestamp"][0:])]
        plt.figure(figsize=(11, 8.5))
        plt.plot_date(plotDataX, self.data["close"], 'blue', zorder=1)
        plt.plot_date(plotDataX, self.data["ema"], 'red', zorder=1)
        plt.plot_date(plotDataX, self.data["kc_lower"], 'gray', zorder=1)
        plt.plot_date(plotDataX, self.data["kc_upper"], 'gray', zorder=1)
        plt.scatter(plotDataX, self.data["buy_points"], zorder=2, color='green')
        plt.scatter(plotDataX, self.data["sell_points"], zorder=3, color='red')
        plt.title(self.symbol)
        if(silent):
            plt.savefig((plot_folder+self.symbol+".jpg"), dpi=300)
        else:
            plt.show()
    
    def validate(self):
        slope_sp = g_val_slope_sp
        slope_dt = g_val_slope_dt

        score_ema = 40       # below EMA
        score = {}

        condition1 = bool(self.data["close"][-1]<self.data["ema"][-1])

        # update scores        
        # slope is positive and greater than SP
        val_slope = ((self.data["close"][-1]-self.data["close"][-(1+slope_dt)])/slope_dt)
        print("Slope: " + str(val_slope))
        if(val_slope>slope_sp):
            score.update({"slope": score_ema})
        else:
            score.update({"slope": 0})

    def export_csv(self):
        try:
            f = open(csv_folder + self.symbol + ".csv", 'w')
        except:
            print("Unable to access " + csv_folder)
        
        writer = csv.writer(f)

        columns = []

        # header
        for c in self.data:
            if (len(self.data[c])==len(self.data["timestamp"])):
                columns.append(c)
        writer.writerow(columns)

        data = []

        for i in range(0,len(self.data["timestamp"])-1):
            data = []
            for c in columns:
                if (len(self.data[c])==len(self.data["timestamp"])):
                    if(self.data[c][i]==numpy.nan):
                        data.append(0)
                    else:
                        data.append(self.data[c][i])
            writer.writerow(data)
        
        f.close()

        del f, writer

    def validate_hist(self):
        # work in reverse from the end of the list
        buy_points = []
        sell_points = []
        buy_points.append(numpy.nan)
        sell_points.append(numpy.nan)

        for i in range(1,len(self.data["timestamp"])):
            # --- BUY CONDITION ---
            slope_ema = (self.data["ema"][i]-self.data["ema"][i-1])
            slope_ema_longterm = (self.data["ema"][i-1]-self.data["ema"][i-2])
            
            low = self.data["close"][i]<self.data["kc_lower"][i]
            high = self.data["close"][i]>self.data["kc_upper"][i]

            if (low and slope_ema<0):
                buy_points.append(self.data["close"][i])
            else:
                buy_points.append(numpy.nan)

            above_kc_upper = bool(self.data["close"][i]>self.data["kc_upper"][i])

            # ---  SELL CONDITION ---

            if (high and slope_ema>0):
                sell_points.append(self.data["close"][i])
            else:
                sell_points.append(numpy.nan)

        self.data.update({"buy_points": buy_points, "sell_points": sell_points})


class condition:
    def __init__(self, expression):
        self.expression = expression

#for i in {"AAPL", "MSFT", "HSY", "OAS"}:
#    stock = security(i)
#    stock.indicator_kc()
#    stock.plot(True)
#    del stock

stock = security("OAS")

stock.indicator_kc()
stock.validate_hist()
stock.plot()

exit()