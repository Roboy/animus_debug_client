# Animus Python Client 🤖

For debugging purposes. Tried with the locomotion and vision modalities.

## Installation

[[Animus Client Library Download](https://animus.cyberanimus.com/dashboard/cyberstore)]

As of the time of writing, the Animus Client library (V3.0.4) requires Python 3.7. 

### On MacOS X

Either emulate Python 3.7 on x86 or recompile the C bindings as follows:

```
conda create -n animus Python=3.8
conda activate animus
cd path/to/animus_client-3.0.4
python3 setup.py build_ext --inplace        # to compile _animus_client_py3 for the current Python version
python3 setup.py install
```

### On Linux

Just use Python 3.7 and you are good.

## Store Cyberselves Account
Write the username and password in environment variables. This way the email and password do not appear in this public repository.

```
# Animus Debug Client
export CYBERSELVES_EMAIL="your_email"
export CYBERSELVES_PWD="your_password"
```