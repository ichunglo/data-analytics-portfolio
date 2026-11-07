"""Create a small fictional database for exercising the analysis."""
import argparse
import json
import sqlite3
from pathlib import Path


def create(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError('Choose a new demo database path: '+str(path))
    db=sqlite3.connect(path)
    db.executescript('''
      CREATE TABLE drug_target_landscape(drug_id TEXT,drug_name TEXT,target_id TEXT,target_name TEXT,
        gene_symbol TEXT,target_category TEXT,drug_category TEXT,approval_reported INTEGER,
        default_developed_count_eligible INTEGER,PRIMARY KEY(drug_id,target_id));
      CREATE TABLE relationship_evidence(drug_id TEXT,target_id TEXT,source_detail TEXT);
    ''')
    rows=[('D1','Demo drug A','T1','Demo receptor alpha','DEMO1','GPCRs','Small molecule',1,1),
          ('D2','Demo drug B','T1','Demo receptor alpha','DEMO1','GPCRs','Biologic',0,1),
          ('D3','Demo substance C','T1','Demo receptor alpha','DEMO1','GPCRs','Unknown',0,0),
          ('D4','Demo drug D','T1','Demo receptor alpha','DEMO1','GPCRs','Other',1,0),
          ('D1','Demo drug A','T2','Demo kinase beta','DEMO2','Kinases','Small molecule',1,1),
          ('D5','Demo drug E','T2','Demo kinase beta','DEMO2','Kinases','Biologic',0,1)]
    db.executemany('insert into drug_target_landscape values (?,?,?,?,?,?,?,?,?)',rows)
    evidence=[('D1','T1','2016-01-01'),('D1','T1','2016-09-01'),('D1','T1','2017-01-01'),
              ('D2','T1','2016-02-01'),('D3','T1','2016-03-01'),('D5','T2','2020-01-01')]
    db.executemany('insert into relationship_evidence values (?,?,?)',
                   [(d,t,json.dumps({'candidate_study_date_proxy':date})) for d,t,date in evidence])
    db.commit();db.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    create(args.out);print('Created fictional demonstration database:',args.out)


if __name__=='__main__':main()
