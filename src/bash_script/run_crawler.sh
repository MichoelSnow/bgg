#!/bin/bash
source /home/msnow/miniconda3/bin/activate bgg
cd /home/msnow/git/bgg/data/kaggle/summary/
mv *.csv old_files/
cd /home/msnow/git/bgg/src/data/
python bgg_weekly_crawler.py
python combine_weekly_data.py
cd /home/msnow/git/bgg/data/kaggle/summary/
kaggle datasets version -m "week of $(date +%Y-%m-%d)" -p . -d -q
