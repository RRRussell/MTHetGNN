#!/usr/bin/env bash


python ../main.py --model MTHetNet --window 168 --horizon 3 --channel_size 12 --hid1 40 --hid2 10 --data data/solar_AL.txt --n_e 137 --A TE/sote.txt --B TE/solar_corr.txt
python ../main.py --model MTHetNet --window 168 --horizon 6 --channel_size 12 --hid1 40 --hid2 10 --data data/solar_AL.txt --n_e 137 --A TE/sote.txt --B TE/solar_corr.txt
python ../main.py --model MTHetNet --window 168 --horizon 12 --channel_size 12 --hid1 40 --hid2 10 --data data/solar_AL.txt --n_e 137 --A TE/sote.txt --B TE/solar_corr.txt
python ../main.py --model MTHetNet --window 168 --horizon 24 --channel_size 12 --hid1 40 --hid2 10 --data data/solar_AL.txt --n_e 137 --A TE/sote.txt --B TE/solar_corr.txt