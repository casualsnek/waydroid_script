# Waydroid Extras Script

[![Visits Badge](https://badges.pufler.dev/visits/casualsnek/waydroid_script)](https://github.com/casualsnek)

Script to add gapps and other stuff to waydroid !

# Installation/Usage
"lzip" and "sqlite" is required for this script to work, install it using your distribution's package manager:
## Arch, Manjaro and EndeavourOS based distributions:
	sudo pacman -S lzip sqlite
## Debian and Ubuntu based distributions:
	sudo apt install lzip sqlite  
## RHEL, Fedora and Rocky based distributions:
	sudo dnf install lzip sqlite
## openSUSE based distributions:
	sudo zypper install lzip sqlite
Then run:
	
    git clone https://github.com/casualsnek/waydroid_script
    cd waydroid_script
    sudo python3 -m pip install -r requirements.txt
    sudo python3 waydroid_extras.py [-i/-g/-n/-h]

## Install OpenGapps

Open terminal and switch to directory where "waydroid_extras.py" is located then run:

    sudo python3 waydroid_extras.py -g
Then restart waydroid service with command below :

    sudo systemctl start waydroid-container.service
Then launch waydroid with:

    waydroid show-full-ui
After waydroid has finished booting open terminal and switch to directory where "waydroid_extras.py" is located then run:

    sudo python3 waydroid_extras.py -i
Copy the returned numeric ID open ["https://google.com/android/uncertified/?pli=1"](https://google.com/android/uncertified/?pli=1) enter the id and register it, you may need to wait upto 10-20 minutes for device to get registered, then clear Google Play Service's cache and try logging in !

## Install Magisk

Open terminal and switch to directory where "waydroid_extras.py" is located then run:

    sudo python3 waydroid_extras.py -m
Then restart waydroid service with command below :

    sudo systemctl start waydroid-container.service
Magisk will be installed on next boot !
Note That this is bootless installation and modules don't work as of now !

## Install libndk arm translation 

This may or may not work properly and is only for testing:
Open terminal and switch to directory where "waydroid_extras.py" is located then run:

    sudo python3 waydroid_extras.py -n
Then restart waydroid service with command below :

    sudo systemctl start waydroid-container.service

## Install libhoudini arm translation

This may or may not work properly and is only for testing: ( Much stable than libndk ) and works on android 11 images
Open terminal and switch to directory where "waydroid_extras.py" is located then run:

    sudo python3 waydroid_extras.py -l
Then restart waydroid service with command below :

    sudo systemctl start waydroid-container.service
 
## Get Android ID for device registration

You need to register you device with its it before being able to use gapps, this will print out your Android ID which you can use for device registration required for google apps:
Open terminal and switch to directory where "waydroid_extras.py" is located then run:

    sudo python3 waydroid_extras.py -i

Star this repository if you find this useful, if you encounter problem create a issue on github !

## Error handling  

In case of error, if you retry immediately and it fails with this error 
```
==> Failed to resize image '/var/lib/waydroid/images/system.img' .. !  e2fsck 1.45.5 (07-Jan-2020)
/var/lib/waydroid/images/system.img is mounted.
e2fsck: Cannot continue, aborting.
```
You need to get the mounting point using `df | grep waydroid`. It will be something like `/dev/loopXXX`. Then, unmount it
```
sudo umount /dev/loopXXX
```
And re-run the script.
