for i in {6660,6661,6662,6663}
    do 
        supervisorctl -c /opt/you1hui/supervisor/supervisor.conf restart shop_app:shop_app$i;
    done
