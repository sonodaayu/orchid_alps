#!/bin/bash
sleep_retry=30 #次の試行までの時間
times_retry=4 #試行回数
sleep_patrol=900 #巡回間隔15分
sleep_between_sensors=5 #センサからデータを受け取るタイミングを若干ずらす
sensors=(1 2) #センサ番号#要変更

while true
do 
  for i in ${sensors[@]}
  do
    echo [`date`] patrolling start for sensor${i} >> log.txt
    isAlive=`ps -ef | grep "alps_sensor_ayu.py sensor${i}" | grep -v grep | wc -l`
    for j in `seq $times_retry`
    do
    if [ $isAlive -eq 1 ]; then
      echo [`date`] sensor${i} was alive >> log.txt
      break
    else
      /usr/bin/python3 /home/ayu/orchid_alps/alps_sensor_ayu.py sensor${i} &
      sleep $sleep_retry 
      isAlive=`ps -ef | grep "alps_sensor_ayu.py sensor${i}" | grep -v grep | wc -l`
      if [ $isAlive -eq 1 ]; then
        echo [`date`] sensor${i} restart >> log.txt
        break
      else
        echo [`date`] sensor${i} failed for $j times >> log.txt 
      fi
    fi
    if [ $j -eq $times_retry ]; then
      echo [`date`] failed to restart sensor${i} and sent notification to LINE >> log.txt
      /usr/bin/python3 /home/ayu/orchid_alps/line_ntf.py sensor${i}
    fi
    done
  sleep $sleep_between_sensors
  done
  sleep $sleep_patrol
done