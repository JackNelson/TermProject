import requests

class DiceCountryDAO:
    def __init__(self, db, jobType, country):
        self._db = db

        # Clean jobType
        # 1. replace spaces with '+'
        # 2. convert to lower case
        self._jobType = jobType.replace(" ", "+").lower()

        # location, use zipcode
        self._country = country

        # Derive the collection name as
        # collectionName = jobType + location
        # eg: datascientistUS
        self._collection = getattr(self._db, jobType.replace(" ", "").lower() + country)

        # Construct the URL
        self._url = "http://service.dice.com/api/rest/jobsearch/v1/simple.json?text={}&country={}".format(self._jobType,
                                                                                                       self._country)

    def retrieveJobs(self):
        print("Retrieving jobs from URL:")
        print(self._url)

        # Drop the collection to start fresh
        print("Dropping collection {}".format(getattr(self._collection, 'name')))
        self._collection.drop()

        # Retrieve jobs from the url and store them into mongodb
        # Handle pagination and store all of the docs in one collection

        r = requests.get(self._url)
        json_data = r.json()

        for item in json_data['resultItemList']:
            self._collection.insert_one(item)

        while json_data['count'] != json_data['lastDocument']:

            # get nextUrl for paginated results
            nextURL = json_data['nextUrl']
            r = requests.get("http://service.dice.com" + nextURL)

            json_data = r.json()
            for item in json_data['resultItemList']:
                self._collection.insert_one(item)


    def countJobs(self):

        print("Count the jobs for a jobTitle and location")
        return (self._collection.count())

    def topCompanies(self):

        print("Printing top companies")

        query = [{"$group": {
            "_id": "$company",
            "totalJobs": {"$sum": 1}
            }
        },
            {"$sort":{
                "totalJobs":-1
            }
        },
            {"$project": {
                "_id":0,
                "Company":"$_id",
                "JobCount":"$totalJobs"
            }
        },
            {"$limit":20}
        ]

        return(self._collection.aggregate(query))