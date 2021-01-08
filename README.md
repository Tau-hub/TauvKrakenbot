# Disclaimer

This bot is only for use with Kraken. 

Everything in this bot has been done from scratch and do not need any third party program.

Read the documentation of the Kraken API if you want more information about the bot and the requests : https://www.kraken.com/features/api

USE IT AT YOUR OWN RISK. I AM NOT RESPONSIBLE FOR YOUR LOSS IF YOU USE IT.

Tested with a python 3.8.0. Anything before python 3.0 will not work.
# Usage 

You need to have a file "keys.py" with your your private key and public key named as API_PRIVATE_KEY and  API_PUBLIC_KEY respectively.

example :
```bash
touch keys.py
```

then add the two following lines to the file(replace with your OWN keys) : 
```python
API_PRIVATE_KEY="KxymE02lMefOTYUpD5AFpQiTSg33x9Jf2mWCvEo0RgFVwLE7zgsdMVtsvZzFZnse40tCnzQkklMIQ41gOg3RhaAfwtP4g8XFh5Kkti0iGuCfYXCS8yrexA=="
API_PUBLIC_KEY="lE9B5JO5bCbmdB4d6HTWxTef1EytbTpC"
```

You can also directly replace the two variables in your bot_trading.py but it is strongly not recommended for security reasons.

To change the behavior of your loop you have to change the args in the kraken.loop() call in the bot_trading.py file.
Read the comment above the method to get more information.

Now you can start the bot 

```bash
python ./bot_trading.py
```

You can read what your bot is doing in the logs file. 


If you want to start the script in the background on a linux system you can use the start_in_bg.sh script.

```bash
./start_in_bg.sh
```

