for i in {9090,9091,9092,9093,9094,9095,9096,9097}
    do 
       supervisorctl -c /opt/you1hui/supervisor/supervisor.conf restart new_shop:new_shop$i;
    done
