"""Analyze the audited SQLite drug–target snapshot without modifying it."""
import argparse
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator

PROJECT = Path(__file__).resolve().parents[1]
YEARS = tuple(range(2015, 2025))
COLORS = LinearSegmentedColormap.from_list('sea', ['#e7f1f3', '#80b2c1', '#123f60'])


def analyze(db, scope='clinical'):
    if scope not in ('clinical','broad'):
        raise ValueError('scope must be clinical or broad')
    db.row_factory = sqlite3.Row
    sql = (PROJECT/'sql/target_rankings.sql').read_text(encoding='utf8')
    ranking = [dict(r) for r in db.execute(sql, {'scope':scope})]
    links = [dict(r) for r in db.execute('''SELECT drug_id,target_id,drug_category,
        default_developed_count_eligible,approval_reported FROM drug_target_landscape
        WHERE ?='broad' OR default_developed_count_eligible=1 OR approval_reported=1''',(scope,))]
    pairs={(r['drug_id'],r['target_id']) for r in links}
    modalities=defaultdict(set)
    for row in links:modalities[(row['target_id'],row['drug_category'])].add(row['drug_id'])
    annual=defaultdict(set)
    for row in db.execute("SELECT drug_id,target_id,source_detail FROM relationship_evidence WHERE source_detail LIKE '{%'"):
        if (row['drug_id'],row['target_id']) not in pairs:continue
        try:detail=json.loads(row['source_detail'])
        except (TypeError,ValueError):continue
        if not isinstance(detail,dict):continue
        date=str(detail.get('candidate_study_date_proxy') or '')
        if re.fullmatch(r'20\d\d(?:-\d\d(?:-\d\d)?)?',date) and int(date[:4]) in YEARS:
            annual[(row['target_id'],int(date[:4]))].add(row['drug_id'])
    return {'ranking':ranking,'links':links,'modalities':modalities,'annual':annual}


def display(row):
    label=row['gene_symbol'] or row['target_name']
    return label if len(label)<=30 else label[:27]+'…'


def save(fig, path):
    fig.savefig(path.with_suffix('.png'),dpi=180,bbox_inches='tight',facecolor='white')
    svg=path.with_suffix('.svg')
    fig.savefig(svg,bbox_inches='tight',facecolor='white')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    plt.close(fig)


def summarize(results):
    """Calculate target and drug summaries without counting a drug twice."""
    classes = Counter((r['target_category'] or 'Unclear') for r in results['ranking'])
    drugs = {}
    for row in results['links']:
        drug = drugs.setdefault(row['drug_id'], {'category': row['drug_category'] or 'Unknown',
                                                  'approved': row['approval_reported'], 'targets': set()})
        if (drug['category'], drug['approved']) != (row['drug_category'] or 'Unknown', row['approval_reported']):
            raise ValueError('Inconsistent drug category or approval status: ' + row['drug_id'])
        drug['targets'].add(row['target_id'])
    categories = defaultdict(Counter)
    degree = Counter()
    for drug in drugs.values():
        categories[drug['category']]['approval reported' if drug['approved'] == 1 else 'approval not recorded'] += 1
        n = len(drug['targets'])
        degree['1' if n == 1 else '2' if n == 2 else '3–4' if n <= 4 else '5–9' if n <= 9 else '10+'] += 1
    queue = [r for r in results['ranking'] if r['reported_approved'] == 0][:15]
    return {'classes': classes, 'categories': categories, 'degree': degree, 'queue': queue}


def plot(results, out, scope):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'svg.fonttype':'none'})
    top=results['ranking'][:15]
    fig,ax=plt.subplots(figsize=(10,7));y=range(len(top));counts=[r['linked_drugs'] for r in top]
    ax.barh(y,counts,color='#b8d7df',label='Linked drug records')
    ax.barh(y,[r['reported_approved'] for r in top],height=.48,color='#176383',label='Of these: approval reported')
    for i,r in enumerate(top):
        ax.text(r['linked_drugs']+.8,i,str(r['linked_drugs']),va='center',fontsize=9)
        approved=r['reported_approved']
        if approved:ax.text(approved-.8 if approved>=8 else approved+.8,i,str(approved),va='center',
                            ha='right' if approved>=8 else 'left',fontsize=8,color='white' if approved>=8 else '#123f60')
    ax.set_yticks(list(y),[display(r) for r in top]);ax.invert_yaxis();ax.set_xlabel('Distinct linked drug records')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True));ax.grid(axis='x',color='#e3ecef');ax.set_axisbelow(True)
    ax.set_title('Most connected targets',loc='left',weight='bold',fontsize=16)
    view='phase/approved' if scope=='clinical' else 'broad source'
    ax.legend(frameon=False,loc='lower right');fig.text(.02,.015,f'Sources: TTD 2024 snapshot and paper-derived catalog; {view} view.\nApproval is drug-level and may be outside the U.S.',fontsize=8,color='#526978')
    fig.tight_layout(rect=(0,.06,1,1));save(fig,out/'target-rankings')
    types=['Small molecule','Biologic','Other','Unknown'];matrix=[[len(results['modalities'].get((r['target_id'],c),set())) for c in types] for r in top]
    draw_heatmap(matrix,[display(r) for r in top],types,'Target relationships by drug category',
                 f'TTD 2024 snapshot and paper-derived catalog; {view} view. Unknown category is retained.',out/'target-by-modality',figsize=(9,7))
    recent=sorted((r for r in results['ranking'] if any(results['annual'].get((r['target_id'],y)) for y in YEARS)),
       key=lambda r:(-len(set().union(*(results['annual'].get((r['target_id'],y),set()) for y in YEARS))),display(r)))[:15]
    if recent:
        matrix=[[len(results['annual'].get((r['target_id'],y),set())) for y in YEARS] for r in recent]
        draw_heatmap(matrix,[display(r) for r in recent],[str(y) for y in YEARS],
          'Selected study-date candidates by target and year',
          f'TTD / registry candidates, 2015–2024; {view} view. Dates are not verified first entry or numbers of trials.',out/'target-by-year',figsize=(11,7))

    summary = summarize(results)
    classes = summary['classes'].most_common()
    fig, ax = plt.subplots(figsize=(10, 6.5))
    y = range(len(classes)); values = [v for _, v in classes]
    ax.barh(y, values, color=[COLORS(.28 + .65*v/max(values)) for v in values])
    for i, v in enumerate(values): ax.text(v+max(values)*.012, i, f'{v:,}', va='center', fontsize=9)
    ax.set_yticks(list(y), [k for k, _ in classes]); ax.invert_yaxis()
    ax.set_xlabel('Distinct target records'); ax.set_title('Which target classes are represented?', loc='left', weight='bold', fontsize=16)
    ax.grid(axis='x', color='#e3ecef'); ax.set_axisbelow(True); ax.set_xlim(0,max(values)*1.16)
    fig.text(.02,.015,f'TTD 2024 snapshot and paper-derived catalog; {view} view.\nClasses are source-derived; unclear classifications are retained.',fontsize=8,color='#526978')
    fig.tight_layout(rect=(0,.07,1,1)); save(fig,out/'target-classes')

    labels = ['Small molecule', 'Biologic', 'Other', 'Unknown']
    for category in summary['categories']:
        if category not in labels: labels.append(category)
    reported = [summary['categories'][k]['approval reported'] for k in labels]
    unrecorded = [summary['categories'][k]['approval not recorded'] for k in labels]
    fig,ax=plt.subplots(figsize=(10,4.8)); y=range(len(labels))
    ax.barh(y,reported,color='#176383',label='Approval reported')
    ax.barh(y,unrecorded,left=reported,color='#b8d7df',label='Approval not recorded')
    for i,(a,b) in enumerate(zip(reported,unrecorded)):
        ax.text(a+b+max(reported+unrecorded)*.025,i,f'{a:,} / {b:,}',va='center',color='#123f60',fontsize=9)
    ax.set_yticks(list(y),labels);ax.invert_yaxis();ax.set_xlabel('Distinct drug records')
    ax.set_xlim(0,max(a+b for a,b in zip(reported,unrecorded))*1.32)
    ax.set_title('Drug categories and recorded approvals',loc='left',weight='bold',fontsize=16)
    ax.legend(frameon=False,loc='lower right');ax.grid(axis='x',color='#e3ecef');ax.set_axisbelow(True)
    fig.text(.02,.015,f'Labels: approval reported / approval not recorded. Sources: TTD 2024 and paper-derived catalog; {view} view.\nApproval is drug-level, may be outside the U.S., and missing records do not establish failure.',fontsize=8,color='#526978')
    fig.tight_layout(rect=(0,.09,1,1));save(fig,out/'drug-category-approval')

    bins=['1','2','3–4','5–9','10+']; counts=[summary['degree'][b] for b in bins]
    fig,ax=plt.subplots(figsize=(9,4.8)); bars=ax.bar(bins,counts,color=[COLORS(.3+.6*n/max(counts)) for n in counts])
    ax.bar_label(bars,labels=[f'{n:,}' for n in counts],padding=4,fontsize=9)
    ax.set_ylim(0,max(counts)*1.15);ax.set_xlabel('Number of linked target records per drug')
    ax.set_ylabel('Distinct drug records');ax.set_title('How many targets are linked to each drug?',loc='left',weight='bold',fontsize=16)
    ax.grid(axis='y',color='#e3ecef');ax.set_axisbelow(True)
    fig.text(.02,.015,f'TTD 2024 snapshot and paper-derived catalog; {view} view.\nLinks reflect source coverage and grouping, not proven clinical mechanisms.',fontsize=8,color='#526978')
    fig.tight_layout(rect=(0,.09,1,1));save(fig,out/'drug-target-degree')

    queue=summary['queue']
    if queue:
        fig,ax=plt.subplots(figsize=(10,7)); y=range(len(queue));counts=[r['linked_drugs'] for r in queue]
        ax.hlines(y,0,counts,color='#b8d7df',linewidth=4);ax.scatter(counts,y,s=60,color='#cf703b',zorder=3)
        for i,n in enumerate(counts):ax.text(n+.5,i,str(n),va='center',fontsize=9)
        ax.set_yticks(list(y),[display(r) for r in queue]);ax.invert_yaxis();ax.set_xlim(0,max(counts)*1.18)
        ax.set_xlabel('Distinct linked drug records');ax.set_title('Targets with no approval recorded in this snapshot',loc='left',weight='bold',fontsize=15)
        ax.grid(axis='x',color='#e3ecef');ax.set_axisbelow(True)
        fig.text(.02,.015,f'TTD 2024 snapshot and paper-derived catalog; {view} view.\nA missing approval is not proof of no approval, drug failure, or target failure.',fontsize=8,color='#526978')
        fig.tight_layout(rect=(0,.07,1,1));save(fig,out/'targets-no-recorded-approval')


def draw_heatmap(matrix,labels,columns,title,footnote,path,figsize):
    fig,ax=plt.subplots(figsize=figsize);image=ax.imshow(matrix,cmap=COLORS,aspect='auto',interpolation='nearest')
    ax.set_xticks(range(len(columns)),columns,rotation=30,ha='right');ax.set_yticks(range(len(labels)),labels)
    maximum=max((v for row in matrix for v in row),default=1) or 1
    for i,row in enumerate(matrix):
        for j,n in enumerate(row):ax.text(j,i,str(n) if n else '–',ha='center',va='center',fontsize=8,color='white' if n/maximum>.62 else '#234458')
    ax.tick_params(length=0);ax.set_title(title,loc='left',weight='bold',fontsize=15,pad=12)
    fig.colorbar(image,ax=ax,shrink=.65,label='Distinct drug records');fig.text(.02,.01,footnote,fontsize=8,color='#526978')
    fig.tight_layout(rect=(0,.04,1,1));save(fig,path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--scope',choices=('clinical','broad'),default='clinical');args=parser.parse_args()
    if not args.db.is_file():parser.error('Database not found: '+str(args.db))
    args.out.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(args.db.resolve().as_uri()+'?mode=ro',uri=True) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Database integrity check failed')
        result=analyze(db,args.scope)
    ranking=result['ranking']
    if not ranking:raise ValueError('No eligible drug–target relationships')
    with (args.out/'target-ranking.csv').open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=ranking[0].keys());writer.writeheader();writer.writerows(ranking)
    with args.db.open('rb') as file:
        digest=hashlib.file_digest(file,'sha256').hexdigest() if hasattr(hashlib,'file_digest') else hashlib.sha256(file.read()).hexdigest()
    meta={'scope':args.scope,'database_sha256':digest,'target_count':len(ranking),
          'drug_count':len({r['drug_id'] for r in result['links']}),'relationship_count':len(result['links']),
          'candidate_date_window':'2015–2024','unit':'distinct linked drug records',
          'limits':['Source-reported approval may be non-US and is a drug-level claim.',
                    'Candidate study dates are not verified first clinical entry or trial counts.',
                    'The dataset is not a complete matched cohort; do not infer failure or success rates.']}
    (args.out/'analysis-manifest.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8')
    plot(result,args.out,args.scope)
    print(json.dumps(meta,indent=2))


if __name__=='__main__':main()
