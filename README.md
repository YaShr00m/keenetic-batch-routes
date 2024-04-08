This python script allows you to create batch routes for KEENETIC routers via SSH for VPN routing.
You have to enable ssh in your KEENETIC router.
1) install python
2) enter your KEENETIC credentials in `config.ini`
3) run run.py | if packages not intaslled automatically, run `pip install requests && pip install paramiko`. If everything is good, you should see message like `Network::RoutingTable: Renewed static route: IP_NETWORK/SUBNET via INTERFACE.`. Note: old firmwares (e.g. on Keenetic giga II) may shows different output, but script still working.
4) enjoy! you can also add your subnets to mine.lst. Don't foreget to use real VPN or other interface name you want to route. You can find it in running-config file of your KEENETIC.
