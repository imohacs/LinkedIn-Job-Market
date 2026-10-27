"""LinkedIn US job market | 2023–2024 historical EDA, full CSV-backed explorer."""
from pathlib import Path
import ast
import html
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="LinkedIn Job Market | Career Intelligence", page_icon="💼", layout="wide", initial_sidebar_state="collapsed")
ROOT = Path(__file__).resolve().parent
CSV = ROOT / "linkedin_job_postings_cleaned.csv"
BLUE, MUTED, WHITE = "#1689ff", "#9daec7", "#eff6ff"

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp,button,input,textarea{font-family:'DM Sans',sans-serif!important}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#080b15!important;color:#edf4ff!important}
.block-container{max-width:none!important;width:100%!important;padding:1.5rem clamp(14px,3.5vw,56px) 4rem!important}
#MainMenu,footer,header{visibility:hidden}
h1,h2,h3,h4{font-family:'Manrope',sans-serif!important;color:#f1f6ff!important;letter-spacing:-.035em!important}
p,li,[data-testid="stCaptionContainer"],label,[data-testid="stWidgetLabel"] p{color:#e1eafa!important;opacity:1!important}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid #273149!important;background:linear-gradient(135deg,#111827,#0e1322)!important;border-radius:20px!important;box-shadow:0 10px 26px #00000017}
[data-testid="stMetric"]{padding:20px!important;background:#111827!important;border:1px solid #26334a!important;border-radius:18px!important}
[data-testid="stMetricLabel"] p{color:#a7bbd5!important;font-weight:650!important}
[data-testid="stMetricValue"]{color:#f7fbff!important;font-family:'Manrope',sans-serif!important;font-weight:800!important}
[data-baseweb="select"]>div,[data-testid="stTextInput"] input,[data-baseweb="input"]>div{background:#111a2b!important;border:1px solid #365273!important;border-radius:12px!important;color:#fff!important}
[data-baseweb="select"] * , [data-baseweb="popover"] *,[role="option"] *,[role="listbox"] *{color:#ecf5ff!important}
[data-baseweb="popover"],[role="listbox"]{background:#152139!important}
[data-testid="stTabs"] [role="tab"]{padding:15px 23px!important;color:#cad8e9!important;font-weight:750!important}
[data-testid="stTabs"] [aria-selected="true"]{color:#55afff!important;border-bottom:3px solid #1689ff!important}
[data-testid="stTabs"] [role="tab"] p{color:inherit!important}
.stButton button{border-radius:10px!important;font-weight:700!important}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}
[data-testid="stAlert"] p{color:#e7f2ff!important}
.brand{font:800 24px Manrope,sans-serif;color:white!important;letter-spacing:-1.1px}.brand span{color:#2499ff!important}
.nav{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #263149;padding:5px 0 23px;margin-bottom:25px;gap:14px;flex-wrap:wrap}
.nav small{font-size:12px;color:#92a8c5!important}
.eyebrow{font:750 12px Manrope,sans-serif;color:#66b9ff!important;letter-spacing:2px;margin-bottom:12px}
.hero{position:relative;overflow:hidden;background:radial-gradient(ellipse at 87% 10%,#0d3961 0%,transparent 45%),linear-gradient(135deg,#111e35,#0d1323 65%);border:1px solid #284363;border-radius:24px;padding:38px clamp(22px,4vw,58px);margin-bottom:26px}
.hero h1{font-size:clamp(33px,4vw,62px);line-height:1.08;margin:3px 0 15px;max-width:980px;font-weight:800}
.hero p{color:#bbcee8!important;font-size:16px;line-height:1.75;max-width:820px}
.chip{display:inline-block;border:1px solid #375875;border-radius:30px;background:#102b49;padding:8px 13px;color:#9fd5ff!important;font-weight:700;font-size:12px;margin:12px 8px 0 0}
.sectionline{margin:6px 0 24px}.sectionline p{max-width:760px;line-height:1.8}
.kicker{font-weight:800;color:#6cb5ff!important;font-size:11px;letter-spacing:2px}
.chapter{font:800 clamp(23px,2.5vw,36px) Manrope,sans-serif;color:#fff!important;line-height:1.3;margin:12px 0}
.takeaway{border-left:3px solid #2599ff;background:#12253e;padding:15px 20px;border-radius:0 12px 12px 0;color:#d5eaff!important;margin:18px 0;line-height:1.7}
.muted{color:#d4e3fa!important;line-height:1.8}.foot{font-size:12px;color:#879bb4!important;margin-top:20px}
@media(max-width:750px){.block-container{padding:1rem 12px 3rem!important}.hero{padding:26px 21px}}

/* Explicit high-contrast treatment for all interactive surfaces */
[data-testid="stTextInput"] input,[data-baseweb="select"] input{background:#101d32!important;color:#fff!important;-webkit-text-fill-color:#fff!important;caret-color:#62bcff!important;font-size:16px!important;font-weight:650!important}
[data-baseweb="select"] [data-testid="stMarkdownContainer"], [data-baseweb="select"] span {color:#f3f8ff!important;opacity:1!important}
[data-testid="stWidgetLabel"] *, [data-testid="stCaptionContainer"] *, [data-testid="stMetricLabel"] *, [data-testid="stRadio"] *{opacity:1!important}
[data-baseweb="input"] input::placeholder,[data-testid="stTextInput"] input::placeholder{color:#91a9c9!important;-webkit-text-fill-color:#91a9c9!important;opacity:1!important}
[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,[data-baseweb="select"]>div:focus-within{border:2px solid #3aa4ff!important;box-shadow:0 0 0 4px #1689ff22!important}
[data-testid="stMetricValue"] *{opacity:1!important}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary *{color:#eff6ff!important}
[data-testid="stSelectbox"] label,[data-testid="stTextInput"] label{color:#e2edfc!important;font-weight:750!important}
[data-testid="stAlert"]{background:#12253d!important}
.rank-note{font-size:13px;color:#c2d7ef!important;line-height:1.8;margin:10px 0 18px}
</style>''', unsafe_allow_html=True)

# Notebook-derived values used only if the exported CSV has not been placed yet.
COUNTS = {"New York, NY":2695,"Chicago, IL":1797,"Houston, TX":1720,"Dallas, TX":1352,"Atlanta, GA":1332,"Boston, MA":1153,"Austin, TX":1071,"Charlotte, NC":1056,"Phoenix, AZ":1027}
PAY = {"San Francisco, CA":130770,"Seattle, WA":125673.6,"New York City Metropolitan Area":111562.5,"New York, NY":110000,"Chicago, IL":100000,"Atlanta, GA":95000,"Los Angeles, CA":93600,"Houston, TX":85000,"San Diego, CA":84000,"Denver, CO":79100}
LOC = {"New York, NY":(40.7128,-74.006),"Chicago, IL":(41.8781,-87.6298),"Houston, TX":(29.7604,-95.3698),"Dallas, TX":(32.7767,-96.797),"Atlanta, GA":(33.749,-84.388),"Boston, MA":(42.3601,-71.0589),"Austin, TX":(30.2672,-97.7431),"Charlotte, NC":(35.2271,-80.8431),"Phoenix, AZ":(33.4484,-112.074),"San Francisco, CA":(37.7749,-122.4194),"Seattle, WA":(47.6062,-122.3321),"New York City Metropolitan Area":(40.88,-73.72),"Los Angeles, CA":(34.0522,-118.2437),"San Diego, CA":(32.7157,-117.1611),"Denver, CO":(39.7392,-104.9903)}
LEVELS = {"Internship":48048,"Entry level":52052,"Associate":72800,"Mid-Senior level":107500,"Director":167500,"Executive":192500}
ANALYST = {"SQL":71.21,"Python":52.27,"Communication":36.36,"Excel":36.36,"Data Analysis":34.09,"JavaScript":30.30,"Statistics":25.0,"Tableau":18.94,"Data Visualization":14.39,"Leadership":13.64}

@st.cache_data(show_spinner=False)
def get_data(path: str, modified_ns: int, size: int):
    data = pd.read_csv(path, low_memory=False)
    if 'title' not in data.columns:
        raise ValueError("CSV must contain a 'title' column")
    data['title'] = data['title'].fillna('').astype(str).str.strip()
    return data

DATA = None
if CSV.exists():
    try:
        meta=CSV.stat()
        DATA=get_data(str(CSV),meta.st_mtime_ns,meta.st_size)
    except Exception as ex:
        st.error(f"Could not read cleaned CSV: {ex}")

@st.cache_data(show_spinner=False)
def title_list(titles):
    return sorted({x for x in titles if x},key=str.casefold)

@st.cache_data(show_spinner=False)
def skill_table(data):
    rows=data[['title','extracted_skills']].copy()
    rows['skill']=rows['extracted_skills'].fillna('').astype(str).str.split(';')
    rows=rows[['title','skill']].explode('skill')
    rows['skill']=rows['skill'].astype(str).str.strip()
    rows=rows[rows.skill.ne('')].drop_duplicates()
    return rows.groupby(['title','skill'],sort=False).size().rename('count').reset_index()

def get_skills(data, role):
    sub=data.loc[data.title.eq(role)]
    n=len(sub)
    if not n or 'extracted_skills' not in sub: return pd.DataFrame(columns=['Skill','Share (%)']),n,0
    def normalize(value):
        if isinstance(value,list):return list(dict.fromkeys(str(v).strip() for v in value if str(v).strip()))
        if pd.isna(value) or not str(value).strip(): return []
        s=str(value).strip()
        if s.startswith('['):
            try:
                arr=ast.literal_eval(s)
                if isinstance(arr,list):return list(dict.fromkeys(str(v).strip() for v in arr if str(v).strip()))
            except (ValueError,SyntaxError):pass
        return list(dict.fromkeys(v.strip() for v in s.split(';') if v.strip()))
    expanded=sub.extracted_skills.map(normalize)
    counts=expanded.explode().dropna().value_counts()
    result=pd.DataFrame({'Skill':counts.index,'Share (%)':(counts.values/n*100).round(2)})
    return result,n,expanded.map(len).mean()

@st.cache_data(show_spinner=False)
def salaries(data):
    if not {'normalized_salary','currency'}.issubset(data.columns):return data.iloc[0:0].copy()
    df=data.copy()
    df['normalized_salary']=pd.to_numeric(df.normalized_salary,errors='coerce')
    df=df[df.currency.astype(str).str.upper().eq('USD') & df.normalized_salary.gt(0)].copy()
    if {'pay_period','max_salary'}.issubset(df.columns):
        mx=pd.to_numeric(df.max_salary,errors='coerce')
        bad=(df.pay_period.eq('HOURLY') & mx.gt(1000)) | (df.pay_period.eq('BIWEEKLY') & df.normalized_salary.gt(500000))
        df=df.loc[~bad]
    return df

@st.cache_data(show_spinner=False)
def salary_summary(df):
    return df.groupby('location').normalized_salary.agg(['median','count']).reset_index()

@st.cache_data(show_spinner=False)
def top_title_catalog(csv_path, modified_ns, size):
    """Pick 30 titles with the most usable observations for each explorer."""
    data = get_data(csv_path, modified_ns, size)
    if 'extracted_skills' in data.columns:
        skill_text = data['extracted_skills'].fillna('').astype(str).str.strip()
        # Count advertisements containing at least one extracted keyword, not mentions.
        usable = skill_text.ne('') & ~skill_text.isin(['[]', 'nan', 'None'])
        skill_counts = data.loc[usable & data.title.ne(''), 'title'].value_counts()
    else:
        skill_counts = pd.Series(dtype=int)
    paid = salaries(data)
    salary_counts = paid.loc[paid.title.ne(''), 'title'].value_counts() if len(paid) else pd.Series(dtype=int)
    return skill_counts.head(30), salary_counts.head(30)


def pick_role(prefix, titles, default='Data Analyst'):
    """Native compact selectbox: typing within the dropdown filters its 30 options."""
    titles = list(titles)
    if not titles:
        st.info('No eligible job titles were found in the dataset.')
        return None
    current = st.session_state.get(f'{prefix}_selected')
    if current not in titles:
        st.session_state[f'{prefix}_selected'] = default if default in titles else titles[0]
    return st.selectbox(
        'Job title · type to search or browse',
        titles,
        key=f'{prefix}_selected',
        help='Only the 30 titles with the highest number of eligible advertisements are shown. Click and start typing to filter.'
    )


def plot_bars(names,values,height=480,percent=False):
    names=list(names)[::-1];values=list(values)[::-1]
    fig=go.Figure(go.Bar(x=values,y=names,orientation='h',marker=dict(color=[f'rgba(30, {min(180,90+i*7)}, 255, 1)' for i in range(len(names))],line=dict(width=0)),text=[f'{v:.1f}%' if percent else f'{v:,.0f}' for v in values],textposition='outside',textfont=dict(color=WHITE,size=12),hovertemplate='%{y}<br>%{x:,.2f}<extra></extra>'))
    fig.update_layout(height=height,margin=dict(l=5,r=65,t=18,b=15),paper_bgcolor='#111827',plot_bgcolor='#111827',font=dict(family='DM Sans',color='#e8f2ff',size=12),xaxis=dict(showgrid=True,gridcolor='#223047',zeroline=False,visible=False,range=[0,(max(values)*1.20 if values else 1)]),yaxis=dict(showgrid=False,tickfont=dict(size=13)),showlegend=False)
    return fig

def section(label,title,desc):
    st.markdown(f'<div class="sectionline"><div class="kicker">{html.escape(label)}</div><h2>{html.escape(title)}</h2><p>{html.escape(desc)}</p></div>',unsafe_allow_html=True)

st.markdown('<div class="nav"><div class="brand">career<span>insights.</span></div><small>US JOB MARKET · 2023—2024 &nbsp; / &nbsp; LINKEDIN DATA EXPLORER</small></div>',unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">DATA-DRIVEN CAREER INTELLIGENCE</div><h1>The market has a story.<br>Find your place in it.</h1><p>Explore the jobs employers advertised, the skills they mention, the cities where opportunities concentrate and the salaries associated with different experience levels.</p><div class="chip">✦ Interactive skills intelligence</div><div class="chip">◉ City-level salary map</div><div class="chip">↗ Historical salary insights</div></div>',unsafe_allow_html=True)

if DATA is not None:
    job_count=len(DATA)
    unique_roles=DATA.title[DATA.title.ne('')].nunique()
    salary_count=len(salaries(DATA))
    nums=[(f'{job_count:,}','JOB POSTS'),(f'{unique_roles:,}','JOB TITLES'),(f'{salary_count:,}','USD SALARY ADS'),('2023—24','PERIOD')]
else:
    nums=[('120,497','POSTS IN NOTEBOOK'),('—','ALL ROLES AFTER CSV'),('—','SALARY ADS AFTER CSV'),('2023—24','PERIOD')]
for col,(value,label) in zip(st.columns(4),nums):col.metric(label,value)

story,roles,geo,paytab,comparetab,gaptab,citycareer=st.tabs(['01 · MARKET STORY','02 · JOBS & SKILLS','03 · CITY EXPLORER','04 · SALARY LAB','05 · CAREER COMPARE','06 · SKILL GAP','07 · BEST CITY'])

with story:
    section('THE NARRATIVE','Five insights. One job market.','A carefully selected story from your EDA notebook — fewer charts, more meaning.')
    chapters=[
        ('01 / WHERE','Jobs concentrate in specific cities','New York led the displayed city count with 2,695 postings. Explore cities to compare opportunities.','top_cities.png'),
        ('02 / WHO','Employers ask for experience','Mid-Senior and Entry-level appear frequently, but they represent different hiring markets.','experience_levels.png'),
        ('03 / PAY','Your level changes the pay picture','Across professions, the reported Entry-level median was $52,052 and Mid-Senior $107,500.','salary_experience.png'),
        ('04 / SKILLS','A job title changes required skills','SQL and Python are frequent keyword mentions in Data Analyst descriptions; other roles have a different mix.','most_mentioned_skills.png'),
        ('05 / LOCATION','Where you work changes the numbers','Selected salary-reporting cities show very different salary medians, but sample sizes vary.','salary_cities.png'),
    ]
    for i,(k,t,d,img) in enumerate(chapters):
        with st.container(border=True):
            a,b=st.columns([1,1.5],gap='large',vertical_alignment='center')
            with a:
                st.markdown(f'<div class="kicker">CHAPTER {k}</div><div class="chapter">{html.escape(t)}</div><p class="muted">{html.escape(d)}</p><div class="takeaway">Keep exploring this insight in the interactive tabs.</div>',unsafe_allow_html=True)
            with b:st.image(str(ROOT/'assets'/img),use_container_width=True)

with roles:
    section('ROLE INTELLIGENCE','Skills behind the most-advertised jobs','Choose from the 30 job titles with the most advertisements containing extracted skills. Select a title to see the percentages.')
    if DATA is None:
        st.info('Run your notebook export and place linkedin_job_postings_cleaned.csv next to app.py to show the top 30 roles by usable job advertisements.')
        titles=['Data Analyst']
        skill_samples = None
    else:
        _meta = CSV.stat()
        skill_samples, salary_samples = top_title_catalog(str(CSV), _meta.st_mtime_ns, _meta.st_size)
        titles = skill_samples.index.tolist()
        st.caption(f'Top {len(titles)} titles by job ads with extracted skills, not by skill score.')
    if titles:
        first=titles.index('Data Analyst') if 'Data Analyst' in titles else 0
        c1,c2=st.columns([2.2,1],gap='large')
        with c1:chosen=pick_role('role',titles)
        with c2:topn=st.select_slider('Skills displayed',options=[5,10,15,20,30],value=15,key='skills_n')
        if chosen is None:
            st.stop()
        if DATA is not None:
            role_skills,n,avg=get_skills(DATA,chosen)
            usd=salaries(DATA)
            subset=usd.loc[usd.title.eq(chosen)]
            median=subset.normalized_salary.median() if len(subset) else None
        else:
            role_skills=pd.DataFrame({'Skill':list(ANALYST),'Share (%)':list(ANALYST.values())})
            n=132;avg=None;median=None
        a,b,c=st.columns(3)
        a.metric('MATCHED JOB ADS',f'{n:,}')
        if skill_samples is not None: st.caption(f'Ads with extracted skills for this title: {int(skill_samples.get(chosen, 0)):,}')
        b.metric('AVG SKILLS PER AD',f'{avg:.1f}' if avg is not None else '—')
        c.metric('MEDIAN ANNUAL USD PAY',f'${median:,.0f}' if median is not None and pd.notna(median) else 'Not reported')
        with st.container(border=True):
            st.subheader('Most-mentioned skills')
            st.caption('Share of this job title’s ads mentioning each keyword at least once. Not a skill proficiency score.')
            if len(role_skills):
                shown=role_skills.head(topn)
                st.plotly_chart(plot_bars(shown.Skill,shown['Share (%)'],height=max(360,45*len(shown)),percent=True),use_container_width=True,config={'displaylogo':False})
                best=shown.iloc[0]
                st.markdown(f'<div class="takeaway"><b>{html.escape(str(best.Skill))}</b> appears in <b>{best["Share (%)"]:.1f}%</b> of the {n:,} matching ads.</div>',unsafe_allow_html=True)
            else:st.info('No recognized keywords were recorded for this title.')
        if len(role_skills):
            with st.expander('Explore all extracted skill percentages'):
                st.dataframe(role_skills,use_container_width=True,hide_index=True)
                st.download_button('Download skills as CSV',role_skills.to_csv(index=False),'job_skill_percentages.csv','text/csv')

with geo:
    section('LOCATION INTELLIGENCE','Explore the United States, city by city','Choose openings or salary and choose a city. The city selector persists without resetting; hovering the markers shows each location.')
    metric=st.segmented_control('Map metric',['Job openings','Median annual salary'],default='Job openings',key='city_metric')
    if DATA is not None and 'location' in DATA.columns:
        if metric=='Job openings':
            values=DATA.location.dropna().astype(str).value_counts().to_dict()
        else:
            ds=salaries(DATA)
            values=ds.groupby('location').normalized_salary.median().to_dict() if 'location' in ds.columns else {}
        values={k:float(v) for k,v in values.items() if k in LOC and pd.notna(v)}
    else:values=COUNTS if metric=='Job openings' else PAY
    if not values:st.info('No city statistics are available for this metric.')
    else:
        names=sorted(values,key=values.get,reverse=True)
        left,right=st.columns([2.7,1],gap='large')
        with right:
            city=st.selectbox('Select a city',names,key=f'city_{metric}',help='Start typing to find a city.')
            st.metric(metric, f'{values[city]:,.0f}' if metric=='Job openings' else f'${values[city]:,.0f}')
            st.metric('POSITION IN THIS VIEW',f'#{names.index(city)+1} of {len(names)}')
            st.markdown(f'<div class="takeaway">{html.escape(city)} is ranked using the selected metric. Select another city to compare instantly.</div>',unsafe_allow_html=True)
            st.caption('Mapped labels are limited to notebook cities with known map coordinates. The map does not claim to show all US cities.')
        with left:
            display=pd.DataFrame([{'city':x,'lat':LOC[x][0],'lon':LOC[x][1],'value':values[x]} for x in names])
            size=[11+24*(v/max(values.values()))**0.55 for v in display.value]
            colors=['#89cdff' if x==city else '#1689ff' for x in display.city]
            fig=go.Figure(go.Scattergeo(lat=display.lat,lon=display.lon,mode='markers+text',text=[x.split(',')[0] if x==city else '' for x in display.city],textposition='top center',textfont=dict(color='#e8f5ff',size=13),marker=dict(size=size,color=colors,opacity=.88,line=dict(color='#d3ecff',width=1)),customdata=display[['city','value']].values,hovertemplate='<b>%{customdata[0]}</b><br>Value: %{customdata[1]:,.0f}<extra></extra>'))
            fig.update_geos(scope='usa',projection_type='albers usa',showland=True,landcolor='#192a42',showlakes=True,lakecolor='#101a30',showsubunits=True,subunitcolor='#42516b',bgcolor='#101725')
            fig.update_layout(height=520,margin=dict(l=0,r=0,t=4,b=0),paper_bgcolor='#111827',font=dict(color=WHITE,family='DM Sans'),showlegend=False)
            st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False,'scrollZoom':False})
        st.subheader('City leaderboard')
        st.dataframe(pd.DataFrame({'City':names,metric:[round(values[x],2) for x in names]}),use_container_width=True,hide_index=True)

with paytab:
    section('COMPENSATION INTELLIGENCE','What does your role pay?','Explore the median and middle 50% of annualized advertised USD pay for a selected title and experience level, not a personal salary guarantee.')
    if DATA is None or not {'normalized_salary','currency','formatted_experience_level'}.issubset(DATA.columns):
        level=st.selectbox('Experience level',list(LEVELS))
        st.metric('ALL-JOB MEDIAN · NOT ROLE-SPECIFIC',f'${LEVELS[level]:,.0f}')
        st.caption('Role × level estimates will activate once the exported CSV is beside app.py. This figure comes from the notebook across occupations.')
    else:
        usd=salaries(DATA)
        _meta=CSV.stat()
        _, salary_samples=top_title_catalog(str(CSV),_meta.st_mtime_ns,_meta.st_size)
        titles=salary_samples.index.tolist()
        st.caption(f'Top {len(titles)} job titles by advertisements with usable USD salary data. Not sorted by highest salary.')
        levels=sorted(DATA.formatted_experience_level.dropna().astype(str).unique())
        c1,c2=st.columns([2,1])
        with c1:role=pick_role('salary',titles)
        with c2:level=st.selectbox('Choose experience level',levels,key='salary_experience')
        sample=usd.loc[usd.title.eq(role) & usd.formatted_experience_level.astype(str).eq(level)] if role is not None else usd.iloc[0:0]
        n=len(sample)
        st.metric('ADS WITH REPORTED USD SALARY FOR SELECTED LEVEL',f'{n:,}')
        if role is not None: st.caption(f'Total qualifying salary ads for {role}: {int(salary_samples.get(role, 0)):,}')
        if n>=5:
            q1,mid,q3=sample.normalized_salary.quantile([.25,.5,.75])
            a,b,c=st.columns(3)
            a.metric('25TH PERCENTILE',f'${q1:,.0f}')
            b.metric('MEDIAN ANNUAL PAY',f'${mid:,.0f}')
            c.metric('75TH PERCENTILE',f'${q3:,.0f}')
            with st.container(border=True):
                fig=go.Figure(go.Histogram(x=sample.normalized_salary,nbinsx=30,marker=dict(color='#1689ff',line=dict(color='#111827',width=1))))
                fig.add_vline(x=mid,line_dash='dash',line_color='#6ed6ff',annotation_text='Median',annotation_font_color='#d3eaff')
                fig.update_layout(height=340,paper_bgcolor='#111827',plot_bgcolor='#111827',font=dict(color=WHITE,family='DM Sans'),xaxis_title='Annualized advertised USD salary',yaxis_title='Job advertisements',margin=dict(l=15,r=15,t=18,b=15))
                st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
            st.markdown(f'<div class="takeaway">The middle 50% of the {n:,} observed salaries for <b>{html.escape(role)}</b> ({html.escape(level)}) lies between <b>${q1:,.0f}</b> and <b>${q3:,.0f}</b>.</div>',unsafe_allow_html=True)
            if n<20:st.warning('Small sample: treat this estimate cautiously.')
        else:st.warning(f'Only {n} salary records match this role and level. At least 5 are required to show a meaningful range.')




# ─── Additional career intelligence tools ───────────────────────────────
@st.cache_data(show_spinner=False)
def skills_for_top_roles(csv_path, modified_ns, file_size):
    """Summaries cached across reruns; denominator is ALL ads for each title."""
    frame=get_data(csv_path,modified_ns,file_size)
    sc,_=top_title_catalog(csv_path,modified_ns,file_size)
    output={}
    for role_name in sc.index.tolist():
        skills, count, avg=get_skills(frame,role_name)
        output[role_name]=(skills,count,avg)
    return output


def median_for_role(usd, role_name):
    series=usd.loc[usd.title.eq(role_name),'normalized_salary']
    return (float(series.median()),len(series)) if len(series) else (None,0)


def coverage_bar(caption, pct):
    st.progress(min(100,max(0,int(round(pct)))))
    st.caption(caption)


with comparetab:
    section('CAREER COMPARISON','Compare two career paths','Compare skills, available job advertisements and advertised annual USD salaries using your actual LinkedIn dataset.')
    if DATA is None or 'extracted_skills' not in DATA.columns:
        st.info('Place linkedin_job_postings_cleaned.csv beside app.py to enable role-to-role comparisons.')
    else:
        _meta=CSV.stat()
        all_skills=skills_for_top_roles(str(CSV),_meta.st_mtime_ns,_meta.st_size)
        names=list(all_skills)
        if len(names)<2:
            st.info('At least two job titles with extracted skills are needed.')
        else:
            lhs,rhs=st.columns(2,gap='large')
            with lhs:
                left_title=st.selectbox('First job',names,index=0,key='compare_first')
            with rhs:
                right_titles=[name for name in names if name!=left_title]
                right_title=st.selectbox('Second job',right_titles,index=0,key='compare_second')
            s1,n1,avg1=all_skills[left_title]
            s2,n2,avg2=all_skills[right_title]
            usd=salaries(DATA)
            med1,salary_n1=median_for_role(usd,left_title)
            med2,salary_n2=median_for_role(usd,right_title)
            a,b=st.columns(2)
            with a:
                with st.container(border=True):
                    st.subheader(left_title)
                    st.metric('Job advertisements',f'{n1:,}')
                    st.metric('Average skills mentioned',f'{avg1:.1f}')
                    st.metric('Median annual salary', f'${med1:,.0f}' if med1 is not None else 'Not available')
                    st.caption(f'Salary sample: {salary_n1:,} advertisements')
            with b:
                with st.container(border=True):
                    st.subheader(right_title)
                    st.metric('Job advertisements',f'{n2:,}')
                    st.metric('Average skills mentioned',f'{avg2:.1f}')
                    st.metric('Median annual salary',f'${med2:,.0f}' if med2 is not None else 'Not available')
                    st.caption(f'Salary sample: {salary_n2:,} advertisements')
            st.subheader('Skills comparison')
            joined=(s1[['Skill','Share (%)']].rename(columns={'Share (%)':left_title})
                    .merge(s2[['Skill','Share (%)']].rename(columns={'Share (%)':right_title}),on='Skill',how='outer').fillna(0))
            joined['Importance']=joined[[left_title,right_title]].max(axis=1)
            joined=joined.sort_values('Importance',ascending=False).head(15)
            fig=go.Figure()
            for col,color in [(left_title,'#1689ff'),(right_title,'#71c9ff')]:
                fig.add_trace(go.Bar(name=col,x=joined['Skill'][::-1],y=joined[col][::-1],marker_color=color,
                    hovertemplate='%{x}: %{y:.1f}%<extra></extra>'))
            fig.update_layout(barmode='group',height=460,paper_bgcolor='#111827',plot_bgcolor='#111827',
                font=dict(color='#edf4ff',family='DM Sans'),margin=dict(l=15,r=15,t=15,b=65),yaxis_title='Share of advertisements (%)',
                xaxis_tickangle=-35,legend=dict(orientation='h',y=1.12))
            st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
            common=set(s1.Skill)&set(s2.Skill)
            ca,cb=st.columns(2)
            with ca:
                st.markdown('**Skills shared by both roles**')
                st.write(', '.join(joined[joined.Skill.isin(common)].Skill.head(12)) or 'No common extracted skills among the most-mentioned keywords.')
            with cb:
                st.markdown('**Skills that distinguish each role**')
                delta=(s1[['Skill','Share (%)']].rename(columns={'Share (%)':'First'})
                       .merge(s2[['Skill','Share (%)']].rename(columns={'Share (%)':'Second'}),on='Skill',how='outer').fillna(0))
                delta['Difference (pp)']=delta['First']-delta['Second']
                st.dataframe(delta.reindex(delta['Difference (pp)'].abs().sort_values(ascending=False).index).head(10),hide_index=True,use_container_width=True)
            st.caption('Skill percentages reflect keyword mentions across advertisements, not mandatory proficiency levels. Salary values are historical and available for fewer ads.')

with gaptab:
    section('PERSONAL SKILL MATCH','How closely do your skills match?','Select a role, then select your current skills. The score reflects the fraction of skill mentions covered, not an employability or hiring probability.')
    if DATA is None or 'extracted_skills' not in DATA.columns:
        st.info('Add linkedin_job_postings_cleaned.csv beside app.py to enable personalized skill matching.')
    else:
        _meta=CSV.stat()
        job_skills=skills_for_top_roles(str(CSV),_meta.st_mtime_ns,_meta.st_size)
        titles=list(job_skills)
        chosen_role=st.selectbox('Target job',titles,key='gap_role')
        table,n,avg=job_skills[chosen_role]
        all_terms=sorted(table.Skill.tolist(),key=str.casefold)
        known=st.multiselect('Skills you already have',all_terms,default=[],key='known_skills',
            placeholder='Type a skill name or select it from the list')
        covered=table.loc[table.Skill.isin(known)]
        total=float(table['Share (%)'].sum())
        match=100*covered['Share (%)'].sum()/total if total>0 else 0
        a,b,c=st.columns(3)
        a.metric('Skill-demand coverage',f'{match:.1f}%')
        b.metric('Matched listed skills',f'{len(covered)} of {len(table)}')
        c.metric('Ads used',f'{n:,}')
        coverage_bar('Demand-weighted keyword coverage from extracted skill frequency; not a prediction of hiring success.',match)
        missing=table.loc[~table.Skill.isin(known)].head(12)
        left,right=st.columns([1.6,1],gap='large')
        with left:
            with st.container(border=True):
                st.subheader('Most useful skills to explore next')
                if missing.empty:st.success('You selected all extracted skills recorded for this role.')
                else:st.plotly_chart(plot_bars(missing.Skill,missing['Share (%)'],height=max(320,len(missing)*37),percent=True),use_container_width=True,config={'displaylogo':False})
        with right:
            with st.container(border=True):
                st.subheader('Skills you selected')
                if known:st.write(', '.join(known))
                else:st.info('Select your skills above to see your matching demand coverage.')
                st.metric('Most-requested missing skill',str(missing.iloc[0]['Skill']) if len(missing) else 'None')
                st.caption('This analysis does not judge your proficiency or calculate the chance of getting hired.')

with citycareer:
    section('YOUR NEXT CITY','Where is your target job most advertised?','Choose a job title and compare cities by actual matching job advertisements. Salary comparisons use only ads with reported USD salaries.')
    if DATA is None or 'location' not in DATA.columns:
        st.info('Add linkedin_job_postings_cleaned.csv beside app.py to explore locations for each job title.')
    else:
        _meta=CSV.stat()
        skills_counts,salary_counts=top_title_catalog(str(CSV),_meta.st_mtime_ns,_meta.st_size)
        available=list(skills_counts.index)
        if not available:
            available=DATA.title.value_counts().head(30).index.tolist()
        target=st.selectbox('Select your job',available,key='citycareer_job')
        min_ads=st.slider('Minimum ads per location',1,30,3,key='citycareer_min')
        postings=DATA.loc[DATA.title.eq(target) & DATA.location.notna()].copy()
        postings['location']=postings['location'].astype(str).str.strip()
        counts=postings.loc[postings.location.ne(''),'location'].value_counts()
        counts=counts[counts>=min_ads].head(25)
        usd=salaries(postings)
        if not usd.empty and 'location' in usd.columns:
            pay=usd.groupby('location').normalized_salary.agg(['median','count'])
        else:
            pay=pd.DataFrame(columns=['median','count'])
        summary=pd.DataFrame({'City':counts.index,'Job ads':counts.values})
        summary['Median salary (USD)']=summary.City.map(pay['median'] if len(pay) else {}).round(0)
        summary['Salary sample']=summary.City.map(pay['count'] if len(pay) else {}).fillna(0).astype(int)
        a,b,c=st.columns(3)
        a.metric('Ads for chosen job',f'{len(postings):,}')
        b.metric('Locations in ranking',f'{len(summary):,}')
        c.metric('Top location',str(summary.iloc[0].City) if len(summary) else 'Not enough data')
        if summary.empty:st.info('No locations meet that minimum. Try a lower minimum number of ads.')
        else:
            left,right=st.columns([1.5,1],gap='large')
            with left:
                st.subheader('Job opportunities by city')
                st.plotly_chart(plot_bars(summary.head(12).City,summary.head(12)['Job ads'],height=480),use_container_width=True,config={'displaylogo':False})
            with right:
                city=st.selectbox('City details',summary.City.tolist(),key='career_city_choice')
                record=summary.loc[summary.City.eq(city)].iloc[0]
                st.metric('Matching job ads',f'{record["Job ads"]:,}')
                st.metric('Median annual USD pay',f'${record["Median salary (USD)"]:,.0f}' if pd.notna(record['Median salary (USD)']) else 'Not reported')
                st.metric('Salary-reporting ads',f'{record["Salary sample"]:,}')
                if record['Salary sample']<5:
                    st.caption('Insufficient paid-ad sample for a reliable salary comparison.')
            st.subheader('Explore all ranked locations')
            st.dataframe(summary,use_container_width=True,hide_index=True)
            if len(summary[summary['Salary sample']>=5]):
                st.caption('Salary figures with fewer than five observations should be treated with particular caution.')
            st.download_button('Download location ranking',summary.to_csv(index=False),'career_city_ranking.csv','text/csv')
