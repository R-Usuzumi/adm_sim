#!/bin/zsh


tpl_file=$1
is_save=$2

for i in {2..6}
do
  rm tree_toshi.res
  echo "Ruuning "$i" resource"
  python toshi_cor.py "$tpl_file" "$i" 100000 2 "$2"
done
