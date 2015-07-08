
read -p  "输入y|Y确定重启所有tornado进程:" -a action


action=`echo "$action" | tr -s '[:upper:]' '[:lower:]'`

if [ $action == 'y' ]
then 
	supervisorctl -c /opt/you1hui/supervisor/supervisor.conf reload;
else 
	echo "quit";
fi

