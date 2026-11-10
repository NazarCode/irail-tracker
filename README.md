A simple tracker for SNCB routes/connections. 
Employs the official irail API.
Allows both direct output and saving data as .csv.
Needs: Python 3 and requests (pip install requests)
Run: python irail.py, which appends the next Brussels-Central → Leuven trains to train_info.csv 
Import: get access to functions that can fetch, parse, and save info from the irail API. 
Test: call test_function() either on the built-in sample or on your sample.