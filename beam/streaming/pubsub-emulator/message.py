from hashlib import blake2b, blake2s
import random
from faker import Faker
import datetime

# sneaky globals
h = blake2b(key=b'pseudorandom key', digest_size=4)
# sneaky configs
random.seed(1002)  # do not change!

Faker.seed(1002)  # do not change!
fake = Faker(['en_US'])
fake.seed_instance(1002)  # do not change!


##
# For the sake of the assignment, you MUST use
# NUM_USERS = int(1e3)
# NUM_RECORDS = int(1e5)
# but feel free to change these for experimentation (fewer == easier to understand)
##
NUM_USERS = int(1e3)
NUM_RECORDS = int(1e5)


def record(user_id, user_name, url):
    """
    Generate a record given a name where the record constitutes data used on a website at a particular
    time
    :return: [user, url, access_time, bytes]
    """
    now=datetime.datetime.utcnow()

    return [user_id,
            user_name,
            url,
            fake.date_time_between_dates(
                datetime_start=now-datetime.timedelta(seconds=random.randint(60, 180) if random.randint(0, 256) >= 255 else 0),
                datetime_end=now, tzinfo=None),
            random.randint(0, 512)]


def users(nr_of):
    """
    produce a (username, userid) tuple that is unique in the returned list
    :param nr_of: the number of users to generate
    :return: a list of tuples
    """
    name_bag = set()
    for x in range(0, nr_of):
        name = fake.name()
        h.update(name.encode("utf-8"))
        name_bag.add((h.hexdigest(), name))
    return sorted(list(name_bag))


def record_generator(name_bag, min_records=10):
    for x in range(0, min_records):
        user_id, user_name = random.choice(name_bag)
        # Allow a user to get stuck on a url
        url = fake.url()
        yield record(user_id, user_name, url)
        while random.randint(0, 10) <= 3:
            yield record(user_id, user_name, url)


