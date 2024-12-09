<h1>Install</h1>

1. Clone the git
2. `cd <clone_dir>/rpi-rgb-led-matrix`
3. Install Python and dependent libs

```
sudo apt-get update && sudo apt-get install python3-dev cython3 python3-pip -y
make build-python PYTHON=$(which python 3)
sudo make install-python 
sudo pip3 install pillow --break-system-packages
```
4. Run the Code
```
cd <clone_dir>/rpi-rgb-led-matrix/PROJ-SAUCY
sudo ./main.py
```