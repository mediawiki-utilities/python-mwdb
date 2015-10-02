import mwdb

enwiki = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
                     "?read_default_file=~/replica.my.cnf")
enwiki.public_replica

with enwiki.transaction() as session:
    print(session.query(enwiki.user)
          .filter_by(user_name="EpochFail")
          .first())

result = enwiki.execute("SELECT * FROM user WHERE user_id=:user_id",
                        {'user_id': 6396742})

print(result.fetchone())
