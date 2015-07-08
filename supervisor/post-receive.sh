#!/bin/sh


echo "==============================================="
Path_1='/opt/you1hui'
Path_2='/opt/xiaoher_api'
para=$1
if [ "$para" = 'xiaoher_api' ]
then
	echo "xiaoher_api"
	# cd $Path_1

	#xiaoher1
	rsh 10.168.20.1 bash /opt/you1hui/supervisor/pull_restart.sh ${para}

elif [ "$para" = 'xiaoher_shop' ]
then
	echo "xiaoher_shop"
	# cd $Path_1

	#xiaoher1
	rsh 10.168.20.1 bash /opt/you1hui/supervisor/pull_restart.sh ${para}

	#xiaoher4

	rsh 10.168.178.192 bash /opt/you1hui/supervisor/pull_restart.sh ${para}

else
    echo "you1hui"
	# cd $Path_1

	#本机(xiaoher2)

	bash /opt/you1hui/supervisor/pull_restart.sh

fi
