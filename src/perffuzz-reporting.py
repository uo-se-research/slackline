import sys
import slack


def message(m: str):
    slack.post_message_to_slack(f"{m}")


def command(c: str):
    slack.post_message_to_slack(f"```\n{c}\n```")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise RuntimeError(f"Got unexpected number of parameters! "
                           f"argv={sys.argv}.\nWe expect a message type (m or c) and "
                           f"the message it self only.")

    if sys.argv[1] == 'm':
        message(sys.argv[2])
    elif sys.argv[1] == 'c':
        command(sys.argv[2])
    else:
        raise RuntimeError(f"Unexpected message flag {sys.argv[1]}")
