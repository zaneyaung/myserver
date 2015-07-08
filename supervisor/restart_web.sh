for i in {8880,8881,8882,8883}
    do 
        supervisorctl -c /root/you1hui/supervisor/supervisor.conf restart shop_web:shop_web$i;
    done
