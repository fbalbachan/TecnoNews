for file in *.pgid; do
    #echo $file
    group_id=$(cat $file | xargs)
    #echo $group_id
    kill -9 -$group_id
    exit
done
