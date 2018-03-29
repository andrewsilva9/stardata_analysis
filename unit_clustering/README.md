## Unit Clustering Things

This folder is for unsupervised (for now) clustering of SCBW units. Data is clearly a big question mark here, so that bit is sort-of TBD, but for now here's what I have:

### cluster_by_attributes

This notebook is dedicated to unsupervised clustering of units by their canonical attributes. That is, I have constructed a tiny dataset of units seen in the first 1000 games of [StarData](https://github.com/TorchCraft/StarData). The dataset is just a single example of each unit, the first time I ever see it. This is saved in a pkl file, and I use that for all of this clustering. You can generate your own version using the `stardata_analysis/utils/generate_unit_base_pkl.py` file. The pickle is extracted from `stardata_analysis/utils/data_utils.py`. You can check that out / edit it if you'd like to include more features, I'm removing basically everything that can change or feels unimportant. 

Most of what's left in that file is then just clustering and visualizing, I used [this sklearn example](http://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html) and adapted it to suit the data I had a bit better, and some old visualization code I had.
