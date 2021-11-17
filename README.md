# nicktrade
Simple stock analysis script to calculate Keltner Channel, EMA, and potentially other indicators. Integrates with AlphaVantage Api for historical data, calculates indicators, and plots alongside historical data. Future integration would include machine learning algorithms to determine buy/sell conditions and automatically generate trade orders.

## Requirements
- AlphaVantage API key
- Spirit of adventure :)

## AlphaVantage API
At the moment, this script uses the AlphaVantage TimeSeriesDaily API for capturing historical data. This is then parsed by the script to convert it to a much easier to work with format. I've tried switching over to the other TimeSeries services but would have to rewrite the parsing portion of the script to correct for that.

Something that I've noticed is there's a limit to the amount of calls to the API, a pretty low one at that, so I used timers and delays in another version to get around this.
