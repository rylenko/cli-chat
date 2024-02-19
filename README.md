<h1 align="center">Welcome to CLI-Chat 🌿</h1>
Small CLI chat with AES encryption.

<h1 align="center">Installation</h1>

**1.** Clone this repository how you like it.

**2.** Install the dependencies:
```
$ pip3 install poetry
$ poetry install --only main
```

**3.** In addition, you can check the quality of the code if you need it.
```
$ poetry install
$ sudo chmod a+x lint.sh
$ ./lint.sh
```

**4.** Start the server:
```
$ python3 server.py 127.0.0.1:8888
```

**5.** Start client(s):
```
$ python3 client.py 127.0.0.1:8888
