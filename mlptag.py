import os
import json
import twitter

from time import sleep
from derpibooru import Search

# Current dir and instanciate values
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
pastPosts = []
t = None
config = {
    'derpi': '',
    'twitter': {
        'key': '',
        'secret': '',
        'token': '',
        'tokenSecret': ''
    }
}


def postT(m, u, i):
    global pastPosts, t
    # Post to Twitter
    t.PostUpdate(m, media=u)
    # Add id to past ids
    pastPosts.append(i)
    # Log
    print('Posted #' + str(post.id))
    sleep(3)


def err(i, e, a):
    # Display error
    print('Error #' + str(i) + ': ' + str(e))
    if a:
        print('^ image size: ' + a)


# Create config file if it doesn't exists
if not os.path.isfile(os.path.join(THIS_DIR, 'config.json')):
    with open(os.path.join(THIS_DIR, 'config.json'), 'w') as f:
        f.write(json.dumps(config, indent=2))

    print('A config.json file has been created.')
    print('Please fill the values before running again.')
    exit(2)


# Load config file
with open(os.path.join(THIS_DIR, 'config.json')) as d:
    config = json.load(d)

# Check that all values in config are filled
if (config['derpi'] == '' or
   config['twitter']['key'] == '' or config['twitter']['secret'] == '' or
   config['twitter']['token'] == '' or config['twitter']['tokenSecret'] == ''):
    print('Please complete your config.json file')
    exit(3)

# Create past ids file if it doesn't exists
if not os.path.isfile(os.path.join(THIS_DIR, 'past.json')):
    with open(os.path.join(THIS_DIR, 'past.json'), 'w') as f:
        f.write(json.dumps(pastPosts))

# Load past ids file
with open(os.path.join(THIS_DIR, 'past.json')) as d:
    pastPosts = json.load(d)

# Login to Twitter API
t = twitter.Api(consumer_key=config['twitter']['key'],
                consumer_secret=config['twitter']['secret'],
                access_token_key=config['twitter']['token'],
                access_token_secret=config['twitter']['tokenSecret'])

# Looks for our watched list posts
for post in Search().key(config['derpi']).query('my:watched'):
    # If the post is rendered and not already in our past ids
    if (post.is_rendered and post.id not in pastPosts):
        # Add hashtags
        hashtags = ['#Spoilers']
        eps = []

        for tag in post.tags:
            tag = tag.lower()

            if 'spoiler:s08' in tag:
                hashtags.append('#MLPSeason8')
                if 'spoiler:s08e' in tag:
                    eps.append(tag.replace('spoiler:', ''))

            if 'spoiler:s09' in tag:
                hashtags.append('#MLPSeason9')
                if 'spoiler:s09e' in tag:
                    eps.append(tag.replace('spoiler:', ''))

            if 'equestria girls' in tag:
                hashtags.append('#EQG')
                # TODO: check for correct tags, to add to eps

        # Make hashtags unique
        hashtags = list(set(hashtags))

        # Join all hashtags to prefix
        prefix = ' '.join(hashtags)

        # If episodes numbers where found, add them to the prefix
        if len(eps) > 0:
            prefix += ' (' + ', '.join(eps) + ')'

        # Make text message
        msg = '{} \n#{} {}'.format(prefix, post.id, post.url)

        # Add media - if it's a webm, we will need the mp4 version of it
        mediaURL = post.image
        if post.original_format == 'webm':
            mediaURL = post.representations['mp4']

        try:
            postT(msg, mediaURL, post.id)
        except twitter.error.TwitterError as e:
            try:
                if e.message['message'] == 'Images must be less than 5MB.':
                    # Try a smaller picture
                    postT(msg, post.tall, post.id)
                else:
                    err(post.id, e, 'full')
            except twitter.error.TwitterError as e:
                try:
                    if e.message['message'] == 'Images must be less than 5MB.':
                        # Try an even smaller picture
                        postT(msg, post.small, post.id)
                    else:
                        err(post.id, e, 'tall')
                except twitter.error.TwitterError as e:
                    try:
                        if e.message['message'] == 'Images must be less than 5MB.':
                            # Try thumb
                            postT(msg, post.thumb, post.id)
                        else:
                            err(post.id, e, 'small')
                    except Exception as e:
                        err(post.id, e, 'thumb')
                except Exception as e:
                    err(post.id, e, 'small')
            except Exception as e:
                err(post.id, e, 'large')
        except Exception as e:
            err(post.id, e, 'full')

# Save our past ids
with open(os.path.join(THIS_DIR, 'past.json'), 'w') as f:
    f.write(json.dumps(pastPosts[-200:]))  # Save last 200 elements
