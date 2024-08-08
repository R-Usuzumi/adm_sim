#!/bin/zsh

lam_values=(0.1 0.2 0.5 1 2 5 10)

n=$1
centrality=$2
seed=$3
tpl_file=$4

echo "$lam_values"
echo "Running lam = 0"
python position.py "$n" 4 "$tpl_file" "$centrality" "$seed" > tree.pos
python m_network.py "$n" 0 4 8 "$tpl_file" tree.pos "$seed" > tree.res
python m_result.py "$n" "$tpl_file" tree.pos tree.res 4 8 > res.res
cat res.res
echo "====================="

for lam in "${lam_values[@]}"
do
    echo "Running lam = $lam"    
    python position.py "$n" 4 "$tpl_file" "$centrality" "$seed" > tree.pos

    python m_network.py "$n" "$lam" 4 8 "$tpl_file" tree.pos "$seed" > tree.res

    python m_result.py "$n" "$tpl_file" tree.pos tree.res 4 8 > res.res
    cat res.res
    echo "====================="

done
