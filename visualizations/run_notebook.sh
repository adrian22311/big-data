#!/bin/bash

cd /home/vagrant/big-data-main/visualizations
/home/vagrant/.local/bin/jupyter nbconvert --to notebook --execute visualizations.ipynb
/usr/local/hadoop/bin/hadoop fs -copyFromLocal visualizations.nbconvert.ipynb /user/project/visual/`date --date="yesterday" +%Y%m%d`/notebook.ipynb
