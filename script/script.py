from config import config


def populate_hateword_data():
    """
    Populate the `hateword` table in MongoDB with data from CSV file.
    """
    with open("./script/hate-speech-lexicons/refined_ngram_dict.csv") as f:
        lst = [row.split(',', 1)[0] for row in f]
        lst = lst[1:]
        print(lst)

        lst = [{'word': word} for word in lst]

        import pymongo
        from pymongo import mongo_client
        try:
            db = mongo_client.MongoClient(config.MONGO_URI).twitter
            db.hateword.delete_many({})
            result = db.hateword.insert_many(lst)
            print(len(result.inserted_ids))
        except pymongo.errors.BulkWriteError as e:
            print(e.details)


if __name__ == '__main__':
    populate_hateword_data()
