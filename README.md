# stardata_analysis

This is a repo that allows for analysis and reading of SCBW replays using TorchCraft, specifically examining the replays from [StarData](https://github.com/TorchCraft/StarData) and the version of TorchCraft therein.

### Requirements / StarData Install:

There are quite a few requirements for this to work, and they are not well-documented or easy to setup (in my opinion). Hopefully this makes it easier.

First, you will need zstd-devel 1.1.4. This can be [found here](https://github.com/facebook/zstd/releases/tag/v1.1.4), pull down the .tar.gz, then run 
```
tar -xzvf zstd-1.1.4.tar.gz
cd zstd-1.1.4/
make
sudo make install
```
This will give you the appropriate zstd library, required for TorchCraft (later versions seem to work to, but this library gave me a lot of trouble so I'm sticking to what is specified here by the authors). Also note that for me (on Ubuntu 16.04), this installed all of the `libzstd.*` files into `/usr/local/lib/` and not into `/usr/lib/`, so Python had trouble finding them. Maybe it was just weird virtualenv stuff, but if you find later that you can't import torchcraft because a zstd library can't be found, you might have to symlink or copy the `libzstd.*` files to `/usr/lib/`.

Second, we need zeromq 4+. Mercifully, this one is easier. You can find the appropriate [release here](https://github.com/zeromq/libzmq/releases/tag/v4.2.3), and again download the .tar.gz file. then run
```
tar -xzvf zeromq-4.2.3.tar.gz
cd zeromq-4.2.3/
./configure
make
sudo make install
```
and you should be good to go.

Unsurprisingly, we also need torch itself! The [torch docs](http://torch.ch/docs/getting-started.html) are actually quite good for this part. I'll copy them here for completeness:
```
git clone https://github.com/torch/distro.git ~/torch --recursive
cd ~/torch; bash install-deps;
./install.sh
```
If, like me, you choose to install torch somewhere other than your home directory, you should at least symlink it to your home. Unfortunately, the StarData Makefile expects it to be there (it's easy to just edit the Makefile, but maybe easier to just symlink and just be on the safe side in case other things expect to find it at ~/).

Now, we're finally ready to pull down and install the StarData repo:
```
git clone https://github.com/TorchCraft/StarData.git
cd StarData/
git submodule update --init --recursive
cd TorchCraft
pip install .
```

And that should be that. I hope I remembered all of the steps. It was a lot of trial and error, so it's possible things slipped in that I forgot about or didn't even notice, but if that's the case then at the very least this is a reasonable head start.

### What's actually here:

So far, just the .ipynb for pulling in a replay and seeing what's inside. I still have some exploration to do, as it seems so far that units never lose health... But again, this is a decent introduction at least.
