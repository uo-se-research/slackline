__author__ = "Ziyad Alsaeed"
__email__ = "zalsaeed@cs.uoregon.edu"
__status__ = "Testing"

import requests
import json
import logging
import configparser

logger = logging.getLogger("SlackMessages")

HOST = "HostName"  # the name of the server from which these messages are sent.

"""
USING WEBHOOK
Login to the slack account and find the settings under "Incoming Webhooks". The POST URL should be in a 
credentials.ini file under a section named "DEFAULT".
    - go to https://api.slack.com/apps.
    - click on your app name or create  anew one.
    - navigate to "Incoming Webhooks".
    - copy the "Webhook URL" to the credentials.ini file with the key "SLACK".

USING TOKENS:
Login to the slack account and find the OAuth & Permissions" settings. Copy the token given to your 
credentials.ini file under a section named "DEFAULT". Here are the details of the process:
    - Install your app to your workspace in slack.
    - Add your app to the channel where you want these post to go (find configurations under the channel settings).
    - Add the following permissions to your app under the scopes section [app_mentions:read, channels:history, 
        channels:join, channels:manage, channels:read, chat:write, chat:write.customize, chat:write.public, files:read,
        files:write, groups:history, groups:read, groups:write, im:history, im:read, im:write, incoming-webhook,
        links:read, links:write, mpim:history, mpim:read, mpim:write, pins:read, pins:write, reactions:read,
        reactions:write, reminders:read, reminders:write, team:read, usergroups:read, usergroups:write,
        users.profile:read, users:read, users:write]

When in doubt try it externally using curl
>>> curl -F content="Hello" -F channels=CHANNEL -F filename=test.txt -F token=YOUR-TOKEN 
    https://slack.com/api/files.upload
"""
config = configparser.ConfigParser()
try:
    with open("credentials.ini") as configs:
        config.read_file(configs)
except IOError as e:
    logger.warning(f"No configuration file: {e}")
else:
    webhook_url = config['DEFAULT']['WEBHOOK']
    slack_token = config['DEFAULT']['TOKEN']
    slack_channel = config['DEFAULT']['CHANNEL']


def post_message_to_slack_using_web_hooks(text: str):
    """
    Post a message to Slack using a webhook. This is the old method we used to post messages to our channel.
    We now use tokens and specific channels instead.
    :param text: The message to be posted.
    """
    slack_data = {'text': f"*{HOST}:* {text}"}
    response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        logger.warning(f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}')


def post_message_to_slack(text: str):
    """
    Post a message to Slack using a token and a channel. The app must bne added to the channel for this method to work.

    :param text: The message to be posted.
    """
    response = requests.post('https://slack.com/api/chat.postMessage',
                             {'token': slack_token,
                              'channel': f"#{slack_channel}",
                              'text': f"*{HOST}:* {text}",
                              }).json()

    if not bool(response['ok']):
        logger.warning(f'Request to slack returned an error. {response}')


def post_file_to_slack(message: str, file_name: str, content: str, file_type="text"):
    """
    A method to create a file and post it to slack. if what you need to post to slack is long, then a file is you best
    option as long messages will be hard to read in slack.
    For more in posting files on slack see https://api.slack.com/methods/files.upload

    :param message: A brief message to send with the file.
    :param file_name: How do you want to name the file in slack.
    :param content: The content of the file.
    :param file_type: The file types.
    """
    response = requests.post('https://slack.com/api/files.upload',
                             {'token': slack_token,
                              'filename': file_name,
                              'channel': f"#{slack_channel}",
                              'filetype': file_type,
                              'initial_comment': f"*{HOST}:* {message}"
                              },
                             files={'file': content}
                             ).json()

    if not bool(response['ok']):
        logger.warning(f'Request to slack returned an error. {response}')


def message(m: str):
    post_message_to_slack(f"{m}")


def command(c: str):
    post_message_to_slack(f"```\n{c}\n```")


"""
useful resources:
https://api.slack.com/messaging/sending
https://medium.com/arriendoasegurado/send-slack-messages-through-python-e6f7a1891bbd
https://slack.dev/python-slack-sdk/webhook/index.html
https://keestalkstech.com/2019/10/simple-python-code-to-send-message-to-slack-channel-without-packages/
"""