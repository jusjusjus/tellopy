
# tellopy

Tello controller library with all perks.

- Connect to 192.168.10.1:8889
- Listen to 192.168.10.2:8889


# Scanning UDP Ports

In `./port-scan` there's an ipython notebook with which you can scan the UDP ports
of your device.  It needs to be executed as root:

```
sudo jupyter notebook --allow-root ./port-scan/scan\ udp\ ports.ipynb
```

The notebook stores the results in a pickled dict by port in
`./port-scan/port-scan.pkl`.


# Manual Control

To start a manual control panel hit:

```
python -m tellopy
```

The functionality requires `PyQt5` and `terminaltables and allows you to
control the drone with your keyboard and mouse using a graphical user
interface.
