import os
import json
import twitter
from time import sleep
from derpibooru import Search

# Current dir and init values
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


# Send media
def postT(msg, image, id):
    global pastPosts, t
    # Post to Twitter
    t.PostUpdate(msg, media=image)
    # Add id to past ids
    pastPosts.append(id)
    # Log
    # print('Posted #' + str(id))
    # Wait a bit to prevent hard ratelimit
    sleep(3)


# Display error message
def err(id, err, size):
    print('Error #' + str(id) + ' on ' + size + ': ' + str(err))


# Stop if there's a lock file or create it
if os.path.isfile(os.path.join(THIS_DIR, 'mlptag.lock')):
    exit(0)
else:
    open(os.path.join(THIS_DIR, 'mlptag.lock'), 'a').close()

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
                if 'Images must be less than 5MB.' in str(e):
                    # Try a smaller picture
                    postT(msg, post.tall, post.id)
                else:
                    err(post.id, e, 'full')
            except twitter.error.TwitterError as e:
                try:
                    if 'Images must be less than 5MB.' in str(e):
                        # Try an even smaller picture
                        postT(msg, post.small, post.id)
                    else:
                        err(post.id, e, 'tall')
                except twitter.error.TwitterError as e:
                    try:
                        if 'Images must be less than 5MB.' in str(e):
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

# Delete lock
os.remove(os.path.join(THIS_DIR, 'mlptag.lock'))
