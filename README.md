# BMW Connected Drive API with Python

This small script shows how to get access to BMW's Connected Drive services/APIs with Python.

The goal is to make it work only by providing the Username and the Password
(and the Vehicle Identification Number (VIN)).

It shall be considered as a simplified example and not as a fully working application.

This work is based on and inspired by articles written by Markus Friedrich

 https://www.markusfriedrich.de/2018/09/23/connected-api-gateway-update/

and

 https://www.markusfriedrich.de/2018/04/30/bmw-connected-drive-hacking-teil-2/

 Thank you!

Instead of basing my on the Connected Drive Smartphone App I used the Website to see how to get the
AccessToken. It seems quite similar to how the Apps are doing it.

# Usage

Alongside the script create a python-file called `bmwcdcredentials.py` which has to contain a class called
`BMWCDCredentials`. This class shall have 3 static member variables: `username`, `password` and `vin`.

```Python
class BMWCDCredentials:
    username = 'Your username (email-address)'
    password = 'Your password'
    vin = 'WB...............' # VIN
```

Fill in the correct information and run the script

```Bash
./bmwcd.py
```

It should print something like

```Bash
access_token Vr............................rx
65846
latitude 45.51184, longitude 3.1100729
```

or an error if something went wrong.
