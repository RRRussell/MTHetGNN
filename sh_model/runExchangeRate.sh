#!/usr/bin/env bash




python ../main.py --model MTHetNet --window 32 --horizon 3 --channel_size 12 --hid1 40 --hid2 10 --data data/exchange_rate.txt --n_e 8 --A TE/sote.txt --B TE/ex_corr.txt
python ../main.py --model MTHetNet --window 32 --horizon 6 --channel_size 12 --hid1 40 --hid2 10 --data data/exchange_rate.txt --n_e 8 --A TE/sote.txt --B TE/ex_corr.txt
python ../main.py --model MTHetNet --window 32 --horizon 12 --channel_size 12 --hid1 40 --hid2 10 --data data/exchange_rate.txt --n_e 8 --A TE/sote.txt --B TE/ex_corr.txt
python ../main.py --model MTHetNet --window 32 --horizon 24 --channel_size 12 --hid1 40 --hid2 10 --data data/exchange_rate.txt --n_e 8 --A TE/sote.txt --B TE/ex_corr.txt





