import argparse
from google.cloud import pubsub_v1
import message
import time





def list_topics(project_id):

    # Lists all existing Pub/Sub topics in the project
    publisher = pubsub_v1.PublisherClient()
    project_path = publisher.project_path(project_id)

    for topic in publisher.list_topics(project_path):
        print(topic)


def create_topic(project_id, topic_name):

    # Create a new Pub/Sub topic in the project
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    topic = publisher.create_topic(request={"name": topic_path})

    print("Topic created: {}".format(topic))


def delete_topic(project_id, topic_name):

    # Delete an existing Pub/Sub topic in the project
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    publisher.delete_topic(request={"topic": topic_path})

    print("Topic deleted: {}".format(topic_path))


def publish_messages(project_id, topic_name):
    """
    :param project_id: a project id (necessary in google cloud platform typically)
    :param topic_name: a pubsub topic name
    :return:
    """

    # Publish messages to a Pub/Sub topic
    publisher = pubsub_v1.PublisherClient()
    # Create qualified identifier in the form required by Pub/Sub: 'projects/{project_id/topics/{topic_name}}'
    topic_path = publisher.topic_path(project_id, topic_name)

    for x in message.record_generator(message.users(message.NUM_USERS), min_records=message.NUM_RECORDS):
        # Encode data to a bytestring for Pub/Sub
        data = ';'.join(map(str, x)).encode("utf-8")
        future = publisher.publish(topic_path, data=data)
        # if int(future.result()) % 1000 == 0:
        print('published:: ({}) : {data}'.format(future.result(), data=data))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_id", help="Your Google Cloud project ID")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list", help=list_topics.__doc__)

    create_parser = subparsers.add_parser("create", help=create_topic.__doc__)
    create_parser.add_argument("topic_name")

    delete_parser = subparsers.add_parser("delete", help=delete_topic.__doc__)
    delete_parser.add_argument("topic_name")

    publish_parser = subparsers.add_parser(
        "publish", help=publish_messages.__doc__
    )
    publish_parser.add_argument("topic_name")

    args = parser.parse_args()

    if args.command == "list":
        list_topics(args.project_id)
    elif args.command == "create":
        create_topic(args.project_id, args.topic_name)
    elif args.command == "delete":
        delete_topic(args.project_id, args.topic_name)
    elif args.command == "publish":
        publish_messages(args.project_id, args.topic_name)
