# MLPTag
[![Build Status](https://travis-ci.org/mkody/MLPTag.svg?branch=master)](https://travis-ci.org/mkody/MLPTag)

> [@MLPTag](https://twitter.com/MLPTag), the Twitter bot posting from its watchlist


## Before using it
- python3
    - `pip3 install python-twitter`
    - `pip3 install git+https://github.com/joshua-stone/DerPyBooru.git`
- Run `python3 mlptag.py` once
- Edit `config.json` with
    - `derpi` with your Derpibooru API key (You can find it in bold here: <https://derpibooru.org/users/edit>)
    - `twitter[...]` with your Twitter app keys and token (create your app here: <https://apps.twitter.com/>)


## Using it
Run the script, `python3 mlptag.py`.

You can use a cron too:
```
*/1 * * * * python3 /path/to/mlptag.py >> /path/to/cron.log 2>&1
```
_You might want to make sure that cron.log file get rotated/cleaned._

