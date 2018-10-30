#!/bin/bash

cd grt123-DSB2017

ls ../Data > prep_result/list
python main.py
cd ..

python papaya.py

chmod -R a+rw grt123-DSB2017/prep_result/*
chmod -R a+rw grt123-DSB2017/bbox_result/*
chmod -R a+rw /output/papaya*
chmod -R a+rw /output/preview

