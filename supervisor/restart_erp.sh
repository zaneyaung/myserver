
for i in {8880,8881,8882,8883,8884,8885,8886,8887}
    do 
        supervisorctl -c /opt/you1hui/supervisor/supervisor.conf restart shop_web:shop_web$i;
    done
