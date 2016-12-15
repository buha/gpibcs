# Semi-Auto GPIB Tester
## What this software is
* A tool to graphically send basic GPIB commands such as `ibwrt`, `ibrd`, `ibrsp`, `ibclr` etc.
* A semi automatic GPIB command sequencer. Loading/saving sequences is provided as a feature.

## What this software isn't
* A fully automatic tester; not flow control mechanisms are provided so the user must split complicated flows into smaller sequences that it executes in an arbitrary order.

# Supported platforms
* Windows 7/10 - using `NI488.2` GPIB driver
* Linux Ubuntu 16.10 - using `linux-gpib` driver

# Dependencies
Source code dialect is Python 3 and the dependencies are as listed below. For python packages, make sure to install using `pip3` if `pip` does not point to `pip3` by default.

## Common
* `Qt5`
* `pyvisa`
* `PyQt5`
* `configparser`

## Linux
* `pyvisa-py` [(custom)](https://github.com/buha/pyvisa-py)
* `linux-gpib` (see below installation instructions)

## Windows
* `pyinstaller` (Optional; only used to build the Windows standalone executable)
* [WiX toolset](http://wixtoolset.org/) (Optional; only used to build the Windows installer)


# `linux-gpib` installation guide
Performed on Ubuntu 16.10 with linux kernel 4.8.0-30-generic.

1. `wget https://netix.dl.sourceforge.net/project/linux-gpib/linux-gpib%20for%203.x.x%20and%202.6.x%20kernels/4.0.3/linux-gpib-4.0.3.tar.gz`
2. `tar -xvf linux-gpib-4.0.3.tar.gz`
3. Ubuntu still likes python2 and we want python3 bindings and installation destination from linux-gpib. Temporarily point `python` to  `python3` by `sudo ln -sf /usr/bin/python3 /usr/bin/python`
3. `cd linux-gpib-4.0.3/`
4. `./configure`
5. `make`
6. `sudo make install`
7. Undo the `python->python3` link using `sudo ln -sf /usr/bin/python2 /usr/bin/python`
8. The `linux-gpib` installer puts the `linux-gpib.so` library in a location that cannot be found by `pyvisa`. Make a symlink as `sudo ln -s /usr/local/lib/libgpib.so.0 /usr/lib/libgpib.so.0`
9. Install `pyvisa` and `pyvisa-py`  using `pip3 install pyvisa pyvisa-py`
9. Test if `pyvisa` sees the GPIB backend by executing `python3 -m visa info`. It should contain the following line:
> GPIB INSTR: Available via Linux GPIB (b'4.0.3')

10. Add current user to group `gpib`: `sudo usermod -a -G gpib $(whoami)`
11. Example `/etc/gpib.conf` provided below, call `sudo gpib_config` when you connect the **USB-GPIB-HS**.
    ```
    interface {
            minor = 0       /* board index, minor = 0 uses /dev/gpib0, minor = 1 uses /dev/gpib1, etc. */
            board_type = "ni_usb_b" /* type of interface board being used */
            name = "gpibprobe"      /* optional name, allows you to get a board descriptor using ibfind() */
            pad = 1 /* primary address of interface             */
            sad = 0 /* secondary address of interface           */
            timeout = T3s   /* timeout for commands */

            eos = 0x0a      /* EOS Byte, 0xa is newline and 0xd is carriage return */
            set-reos = yes  /* Terminate read if EOS */
            set-bin = no    /* Compare EOS 8-bit */
            set-xeos = no   /* Assert EOI whenever EOS byte is sent */
            set-eot = yes   /* Assert EOI with last byte on writes */

            /* settings for boards that lack plug-n-play capability */
            base = 0        /* Base io ADDRESS                  */
            irq  = 0        /* Interrupt request level */
            dma  = 0        /* DMA channel (zero disables)      */

            master = yes    /* interface board is system controller */
    }

    device {
            minor = 0
            name = "prober"
            timeout=T3s
            pad = 5
            sad = 0
    }
    ```
12. `$ lsmod | grep ni` should now contain these 2 modules.
    ```
    ni_usb_gpib            36864  0
    gpib_common            40960  1 ni_usb_gpib
    ```

