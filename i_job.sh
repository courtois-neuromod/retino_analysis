#!/bin/bash

salloc --time=2:0:0 --ntasks=1 --cpus-per-task=16 --gres=gpu:v100:1 --mem-per-cpu=4000M --account=rrg-pbellec
