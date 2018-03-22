import os


def reboot(wait=0):
    print("Going to restart device in " + str(wait) + " second(s)")
    os.system("sudo shutdown -r -t sec " + str(wait))


def restart():
    print("Going to restart meterkast service")
    os.system("sudo service meterkast restart")
