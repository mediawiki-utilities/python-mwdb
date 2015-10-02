import mwdb

enwiki = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
                     "?read_default_file=~/replica.my.cnf")
enwiki.public_replica

with enwiki.transaction() as session:
    print(session.query(enwiki.revision_userindex)
          .filter_by(rev_user_text="EpochFail")
          .count())

result = enwiki.execute("SELECT COUNT(*) FROM revision_userindex " +
                        "WHERE rev_user=:user_id",
                        {'user_id': 6396742})

print(result.fetchone())
