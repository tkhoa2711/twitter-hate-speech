import pymongo
from hatespeech.config import config
from pymongo import mongo_client


def populate_hateword_data():
    """
    Populate the `hateword` table in MongoDB with data from CSV file.
    """
    with open("./script/hate-speech-lexicons/refined_ngram_dict.csv") as f:
        lst = [row.split(',', 1)[0] for row in f]
        lst = lst[1:]

        lst = [{
            'word': word,
            'category': [],
            'similar_to': []
        } for word in lst]

        try:
            db = mongo_client.MongoClient(config.MONGO_URI).twitter
            db.hateword.delete_many({})
            result = db.hateword.insert_many(lst)
            print("Completed populating", len(result.inserted_ids), "hate words")
        except pymongo.errors.BulkWriteError as e:
            print(e.details)


def populate_user_data():
    """
    Pre-populate user data for the app, including an admin account
    """
    try:
        db = mongo_client.MongoClient(config.MONGO_URI).twitter
        db.user.insert_one(
            {
                'username': 'admin',
                'password': 'admin',
            }
        )
        print("Created an admin account")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    populate_hateword_data()
