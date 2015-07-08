#!/bin/bash


path_0='/opt/you1hui'
para=$1
if [ "$para" = 'xiaoher_api' ]
then
	path='/opt/xiaoher_api'
	echo ${path}
	cd ${path}
	#废弃本地没有commit的修改
	git stash
	#拉取远程分支
	git fetch
	#将本地的状态回退到和远程的一样  
	git reset --hard origin/master
	#重启应用
	cd ${path_0}
	supervisor/restart_app.sh
elif [ "$para" = 'xiaoher_shop' ]
then
	path='/opt/xiaoher_shop'
	echo ${path}
	cd ${path}
	#废弃本地没有commit的修改
	git stash
	#拉取远程分支
	git fetch
	#将本地的状态回退到和远程的一样  
	git reset --hard origin/master
	#重启应用
	cd ${path_0}
	supervisor/restart_shop.sh
else
	path=${path_0}
	echo ${path}
	cd ${path}
	#废弃本地没有commit的修改
	git stash
	#拉取远程分支
	git fetch
	#将本地的状态回退到和远程的一样
	git reset --hard origin/master
	#重启应用
	cd ${path_0}
	supervisor/restart_erp.sh
fi