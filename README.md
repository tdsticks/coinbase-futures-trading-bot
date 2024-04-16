# Aurox Signals to Coinbase Advanced API Trading Bot

Using the Aurox Signals and trading on the Coinbase Financial Markets (Futures)


## Introduction and Overview
This project develops a trading bot that utilizes Aurox (Ax) signals to strategically 
trade BTC futures on Coinbase Financial Markets. Designed for long-term trading, it 
leverages Weekly and Daily signals to optimize trading decisions within the constraints
of monthly futures contracts. This approach emphasizes financial patience, allowing
trades to mature fully based on the prevailing market conditions signaled by Ax. 
The bot adapts to the complexities of contract expirations, starting with a simple
strategy and evolving to incorporate advanced trading maneuvers like Dollar-Cost 
Averaging (DCA) and dynamic order adjustments.

> **Disclaimer**: Trading cryptocurrencies, especially on leveraged futures markets, 
  involves significant risks. This bot is for educational purposes only. Always review
  and test trading strategies in controlled environments before live deployment. I am not
  responsible for any financial losses incurred from using this software.


## Features
- **Signal Processing**: Handles both Weekly and Daily trading signals.
- **Flexible Timeframes**: Initially uses 1-minute signals for testing; configurable to use more 
  strategic timeframes like Weekly or Daily.
- **Database Integration**: Uses SQLite for initial setup, with scope for migration to more robust 
  database solutions.
- **Adaptive Trading Strategy**: Adjusts trades based on Aurox signals, market conditions, and 
  contract expirations.
- **Local and Cloud Deployment**: Designed for both local setups using ngrok for testing and 
  cloud-based deployment for live environments.


## Usage
Once the setup is complete, the bot will listen for Aurox signals sent to the `/webhook` endpoint. It
will automatically process these signals to manage and execute trades on Coinbase Futures based on 
predefined strategies.


## Contributing
We welcome contributions from the community! Whether it's adding new features, fixing bugs,
or improving documentation, your help is appreciated. Please fork the repository and submit
pull requests with your changes. Follow the existing code style, include unit tests for new
code, and update documentation as appropriate. 


### Key Strategy Highlights:
- **Long-term Trading Focus**: The bot holds positions as long as the Ax signals remain favorable, 
  adjusting only when a clear opposing signal is received.
- **Adaptive to Contract Cycles**: It intelligently manages transitions between futures contracts, 
  maintaining alignment with the overall trading strategy.
- **Initial Simplicity with Scalability**: Starts with a fundamental trading approach, with plans to
  scale up complexity as further stability and predictability are achieved.

> **Note**: While initially optimized for Coinbase futures, the architecture allows potential adaptation
> for spot markets and other trading platforms. Users are advised to exercise caution and to thoroughly
> test the bot in a controlled environment before live deployment due to the inherent risks of leveraged
> futures trading.


## Prerequisites
- **Aurox Account**: Ensure you have at least 3 URUS tokens to access the Ax signal. Purchase URUS 
  tokens via platforms like Gate.io, PancakeSwap, or Uniswap. Connect your wallet to your Aurox account
  for the platform to recognize the tokens.
- **Coinbase Futures Account**: You need a funded Coinbase Futures account. Starting with about $1000
  is recommended, considering the typical contract size and market conditions as of the latest update.
- **Development Environment**: A stable local development setup, preferably with Python 3.10.0, and a
  Python IDE like PyCharm or VS Code. Ensure you have access to a SQLite GUI if using SQLite for data 
  management.
- **Web Hosting for Deployment**: A reliable web hosting service where you can deploy your Flask 
  application, such as Heroku or PythonAnywhere, with support for persistent connections needed for 
  receiving webhooks.

  
## Trading Strategy and Risk Management
Trading in futures and leveraged markets carries significant risks and requires a well-thought-out 
strategy and a clear understanding of potential losses and profits. Leveraged trading can result in 
substantial gains as well as losses, including the possibility of losing more than your initial investment.


### Personal Experience and Learning
My personal journey in automated trading has included both successes and significant losses, which have 
been crucial in shaping my approach to market risk management. For instance, while using 3Commas bots 
and the QFL (Quick Fingers Luc) method, I experienced both substantial profits and painful liquidations.
Such experiences underline the importance of resilience and the ability to objectively assess and respond
to market conditions.


### Building Your Strategy
It is crucial to develop a trading plan that suits your risk tolerance and market approach. Consider 
these principles:
- **Risk Management**: Always know how much of your capital you are willing to risk on a single trade.
- **Profit Taking**: Set clear objectives for taking profits and sticking to them.
- **Continuous Learning**: The market is ever-changing, and continuous learning from both successes and
  failures is key.

### Follow Experienced Traders
Engaging with the community and following experienced traders can provide valuable insights and strategies.
Here are a few traders whose insights I've found beneficial:
- [@TrueCrypto28](https://twitter.com/TrueCrypto28) - Provides deep market analysis.
- [@CarpeNoctom](https://twitter.com/CarpeNoctom) - Offers valuable trading tips and educational content.
- Additional notable traders include [@George1Trader](https://twitter.com/George1Trader), [@IncomeSharks](https://twitter.com/IncomeSharks), and others listed below:
  - @CryptoCapo_
  - @concodanomics
  - @CJ900X
  - @kingthies
  - @MooninPapa
  - @scottmelker
  - @naval
  
> **Disclaimer**: This bot is a tool intended to assist in trading but does not guarantee profits. Trading involves substantial risk of loss and is not suitable for every investor. The valuation of cryptocurrencies may fluctuate, and as a result, clients may lose more than their original investment. My experiences and shared strategies are not solicitations of any order to buy or sell. Therefore, you should not speculate with capital that you cannot afford to lose. I am not responsible for any losses incurred as a result of using this bot. Always perform your due diligence before making trading decisions.


## How it works (high-level)
This project is the middleman between Aurox and Coinbase Futures (CFM). We receive
Weekly and Daily signals from Aurox, then determine if we should place a long or short from the Ax signal. 
Then, create an order with Coinbase Futures. It will also check if we have any existing 
orders so we don't accidentally close out any orders or place additional orders, unless we want them 
(optional). We then check to see when to close out the order, are we need the EOM (end of month) or has
a opposing-sided signal come through, which they don't occur that often in a year. Again, this a long 
term trading strategy that requires much patience. You can read on how the Aurox Indicator works 
here: https://docs.getaurox.com/product-docs/aurox-terminal-guides/indicator-guides/aurox-indicator
So, that essentially it from a high-level. Obviously there's more to it and more we can do, but I wanted
to keep things simple for now.

## Trading Strategy
As mentioned above in the overview and a bit in the how it works, we're working with the Aurox Indicator 
as a means of when to go long or short and when to place trades. Based on Aurox's documentation from 
their indicator, we still need to be careful as to when their indicator is confirmed or not. So the 
method of which you setup your Aurox alerts is important. Using their default "predefined alert" is a 
good starting point. I do adjust mine and remove the opposing condition under the "Criterion" so its 
only long if its a long signal and short for short. The key with this alert is that the Operation is set
to "Becomes" vs "is". I'm using their default "Becomes", but this could be up for debate or need
continued testing on which is better. Since the Weekly signals are far and few in between, we need
to add the last indicator entry to our database (SQLite for now). This will give our bot the starting
point on what to check against for placing trades when Daily signals come in. The other challenging thing
to factor in here is that what chart (market) are we using to read signals from versus the actual 
chart (market) we're placing trades on. As mentioned in the overview, this bot could be modified to use
the normal spot market and give you a one-to-one signals to chart if you're using Coinbase or Binance
to trade on. Being in the US here, finding a legal futures market to trade on can be challenging, but
since we're doing the long game here on our strategy, I'm not afraid of the markets being off since we're
looking from a large time frame.

#### When does the bot enter (when do we place trades)?
  - Well again, we want to be safe and not haphazard with our initial order, especially 
  in futures. I would say it's safer to place after the first Daily indicator after the Weekly was set
  in the same direction. So if the Weekly was short (like on April 8th 2024 using Coinbase BTC/USDT),
  then the first Daily happened on April 12th, 2024. This should be a safer, more confirmed, 
  place to start shorting the market. 

#### When does the bot exit?
  - We need to factor in a few things here:
    - Are we at the end of the monthly futures contract? 
    - How far away are we from the Weekly percentage-wise? A reversal could happen and other events.
    - Do we want to take profits after a certain percentage drop from the weekly? Since we know crypto
      can be very volatile, and we will see bounces, drops and spikes, we could wait for bounces in our
      favor within the Weekly indicator until the next Weekly indicator appears, which I know can be tricky.
      So this is why we need to be careful for how long we keep our trades open and when we take profits.
      > NOTE: Being greedy is dangerous and again, this is a psychological mindset you need to control. 



## Setup and Installation
Detailed steps on setting up the environment, from installing dependencies to configuring your trading
platform connections, including API key generation and webhook setup.


### Coinbase Advanced API
- Generate API keys via the Coinbase Advanced API portal. Ensure the keys are configured with the 
  necessary permissions for trading.
- Store API keys securely and configure your application environment to use these keys without 
  hard-coding them in your source.


### Aurox Configuration
- See [AUROX.md](./AUROX.md) document on account setup and purchasing tokens
- Set up alerts for both Weekly and Daily timeframes using the Aurox platform.
- For local testing and initial deployment, use ngrok to expose your local development server and 
  configure Aurox to send webhook notifications to this URL.


### LOCAL Setup (not production)
Coding Requirements (MacOS):
- A Python IDE (Again, I'm using Pycharm but VS Code can work as well)
- Python 3.10.0
- brew
  - pyenv (for virtual enironment)
  - pyenv-virtualenv
  - ngrok
- git (obviously)
- SQLite GUI


## Installation and Local Testing
1. Setup a new virtual environment using pyenv and python 3.10.0
2. Switch to the new virt-env for this project and install the requirements.txt file
3. Clone the Repository
   1. git clone https://github.com/yourgithub/aurox-coinbase-bot.git
   2. cd aurox-coinbase-bot
4. **Set up the Environment:**
   1. Install Python dependencies: `pip install -r requirements.txt`
   2. Set up `.env` file from `.env.example` template. 
      See [Coinbase Adv API doc](./COINBASE_ADV_API.md)
5. Run the Flask project (port 5000)
   1. Start the Flask app ```Flask run``` in your terminal or IDE
   2. We have a "/webhook" route that will listen for signals from Aurox
6. Create an ngrok account (free)
   1. Setup ngrok per their instructions
   2. Tunnel the local server using ngrok ```ngrok http http://localhost:5000``` in your terminal
   3. Get your public URL from ngrok
      1. Ngrok does offer a "claim a free static domain in your ngrok Dashboard" if you don't want
         to have to keep recreating your Aurox alerts each time you do local development.
   4. Append the webhook route to the end of the ngrok public URL
      1. https:{your ngrok address}.ngrok-free.app/webhook
   5. Configure Aurox to send webhooks to the ngrok URL.
      1. Apply the ngrok URL with the webhook route to the Aurox alerts (for local testing)
      2. Now, if you wait a few minutes, a long or short signal should trigger on the 1 min
         and you should see the Flask app along with ngrok log the signal. I purposely have
         the bot set to NOT do any trading on the lower trading timeframes, so we don't
         accidentally place orders when we don't want them here.


## Production (Deployment)
1. Create a new account with a free hosting site like Heroku, Pythonanywhere or cloud 
   platform of your choice.
2. Setup the account for Flask app
3. Deploy your application to a cloud service.
   1. Upload all necessary code here, including your .env file
   2. Refresh the webapp and test it out using the hosting sites URL they provide you
4. Take the new URL and append the "/webhook" route to the URL
5. Configure Aurox to send webhooks to the ngrok URL.
   1. Add the appended URL to both a long and short Aurox Weekly and Daily alerts
6. Watch the logs on the hosting site
7. Also see if you can access the SQLite database and check for signal entries


## Support the Project

If you find this project useful, consider supporting it by donating:

- **BTC**: `3AHUcVe5a3f4y2iJR8sqXZfzcxK9TzwKmz`
- **ETH/USDT (ETH Network)**: `0xa8EDF5550fE2878b0095eCE6C94adDfdaDf5C6b0`
- **BNB/URUS (BNB Network)**: `0xa8EDF5550fE2878b0095eCE6C94adDfdaDf5C6b0`
