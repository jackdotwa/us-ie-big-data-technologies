import argparse
from google.cloud import pubsub_v1

def list_subscriptions_in_topic(project_id, topic_name):
    # List the subscriptions for a given topic
    publisher = pubsub_v1.PublisherClient()
    # Create qualified identifier in the form required by Pub/Sub: 'projects/{project_id/topics/{topic_name}}'
    topic_path = publisher.topic_path(project_id, topic_name)

    for subscription in publisher.list_topic_subscriptions(topic_path):
        print(subscription)

def list_subscriptions_in_project(project_id):
    # List all subscriptions in a given project
    subscriber = pubsub_v1.SubscriberClient()
    project_path = subscriber.project_path(project_id)

    for subscription in subscriber.list_subscriptions(project_path):
        print(subscription.name)

def create_subscription(project_id, topic_name, subscription_name):
    # Create a  new pull subscription on a topic
    subscriber = pubsub_v1.SubscriberClient()
    topic_path = subscriber.topic_path(project_id, topic_name)
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name
    )
    subscription = subscriber.create_subscription(
        name=subscription_path, topic=topic_path
    )
    print("Subscription created: {}".format(subscription))

def create_push_subscription(project_id, topic_name, subscription_name, endpoint):
    # Create a new push subscription on a topic
    subscriber = pubsub_v1.SubscriberClient()
    topic_path = subscriber.topic_path(project_id, topic_name)
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name
    )
    push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint)

    subscription = subscriber.create_subscription(
        subscription_path, topic_path, push_config
    )
    print("Push subscription created: {}".format(subscription))
    print("Endpoint for subscription is: {}".format(endpoint))

def delete_subscription(project_id, subscription_name):
    # Delete an existing Pub/Sub subscription
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name
    )
    with subscriber:
        subscriber.delete_subscription(request={"subscription": subscription_path})
    print("Subscription deleted: {}".format(subscription_path))


def update_subscription(project_id, subscription_name, endpoint):
    # Update the subscription push endpoint url (NOTE: Properties such as the topic cannot be modified)
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name
    )
    push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint)

    subscription = pubsub_v1.types.Subscription(
        name=subscription_path, push_config=push_config
    )
    update_mask = {"paths": {"push_config"}}
    subscriber.update_subscription(subscription, update_mask)
    result = subscriber.get_subscription(subscription_path)
    print("Subscription updated: {}".format(subscription_path))
    print("New endpoint for subscription is: {}".format(result.push_config))

def receive_messages(project_id, subscription_name, timeout=None):
    # Receive messages from a pull subscription
    # A timeout can be set for how long (in seconds) the subscriber should listen for messages for
    subscriber = pubsub_v1.SubscriberClient()
    # Create qualified identifier in the form required by Pub/Sub: 'projects/{project_id/subscriptions/{subscription_name}}'
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name
    )

    def callback(message):
        print("Received message: {}".format(message))
        message.ack()

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print("Listening for messages on {}..\n".format(subscription_path))

    # result() in a future will block indefinitely if `timeout` is not set,
    # unless an exception is encountered first.
    try:
        streaming_pull_future.result(timeout=timeout)
    except:  # noqa
        streaming_pull_future.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_id", help="Your Google Cloud project ID")

    subparsers = parser.add_subparsers(dest="command")
    list_in_topic_parser = subparsers.add_parser(
        "list_in_topic", help=list_subscriptions_in_topic.__doc__
    )
    list_in_topic_parser.add_argument("topic_name")

    list_in_project_parser = subparsers.add_parser(
        "list_in_project", help=list_subscriptions_in_project.__doc__
    )

    create_parser = subparsers.add_parser(
        "create", help=create_subscription.__doc__
    )
    create_parser.add_argument("topic_name")
    create_parser.add_argument("subscription_name")

    create_push_parser = subparsers.add_parser(
        "create-push", help=create_push_subscription.__doc__
    )
    create_push_parser.add_argument("topic_name")
    create_push_parser.add_argument("subscription_name")
    create_push_parser.add_argument("endpoint")

    delete_parser = subparsers.add_parser(
        "delete", help=delete_subscription.__doc__
    )
    delete_parser.add_argument("subscription_name")

    update_parser = subparsers.add_parser(
        "update", help=update_subscription.__doc__
    )
    update_parser.add_argument("subscription_name")
    update_parser.add_argument("endpoint")

    receive_parser = subparsers.add_parser(
        "receive", help=receive_messages.__doc__
    )
    receive_parser.add_argument("subscription_name")
    receive_parser.add_argument("--timeout", default=None, type=float)

    args = parser.parse_args()

    if args.command == "list_in_topic":
        list_subscriptions_in_topic(args.project_id, args.topic_name)
    elif args.command == "list_in_project":
        list_subscriptions_in_project(args.project_id)
    elif args.command == "create":
        create_subscription(
            args.project_id, args.topic_name, args.subscription_name
        )
    elif args.command == "create-push":
        create_push_subscription(
            args.project_id,
            args.topic_name,
            args.subscription_name,
            args.endpoint,
        )
    elif args.command == "delete":
        delete_subscription(args.project_id, args.subscription_name)
    elif args.command == "update":
        update_subscription(
            args.project_id, args.subscription_name, args.endpoint
        )
    elif args.command == "receive":
        receive_messages(args.project_id, args.subscription_name, args.timeout)
