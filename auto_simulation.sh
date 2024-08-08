#!/bin/zsh
lam_values=(0.1 0.2 0.5 1 2 5 10)

n=$1
centrality=$2
seed=$3
tpl_file_1=$4
tpl_file_2=$5
tpl_file_3=$6

# 引数チェック
if [ -z "$n" ] || [ -z "$centrality" ] || [ -z "$seed" ] || [ -z "$tpl_file_1" ] || [ -z "$tpl_file_2" ]; then
    echo "Usage: $0 <n> <centrality> <seed> <tpl_file_1> <tpl_file_2>"
    exit 1
fi

run_simulation() {
    local tpl_file=$1
    local n=$2
    local centrality=$3
    local seed=$4


    echo "Running $tpl_file" | tee -a res.res
    python position.py "$n" 4 "$tpl_file" "$centrality" "$seed" > tree.pos

    python m_network.py "$n" 0 4 8 "$tpl_file" tree.pos "$seed" > tree.res

    python m_result.py "$n" "$tpl_file" tree.pos tree.res 4 8 | tee -a res.res
    
    echo "====================="

    for lam in "${lam_values[@]}"
    do
        echo "Running lam = $lam with $tpl_file"    
        python position.py "$n" 4 "$tpl_file" "$centrality" "$seed" > tree.pos
    
        python m_network.py "$n" "$lam" 4 8 "$tpl_file" tree.pos "$seed" > tree.res     
        python m_result.py "$n" "$tpl_file" tree.pos tree.res 4 8 |tee -a res.res  

        echo "====================="
    done
    echo "===================" >> res.res
}


run_simulation $tpl_file_1 $n $centrality $seed
run_simulation $tpl_file_2 $n $centrality $seed
run_simulation $tpl_file_3 $n $centrality $seed
