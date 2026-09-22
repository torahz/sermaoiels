import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from datetime import date, timedelta
import json
import tempfile
import unittest
from calendario import domingos, pascoa, classificar, primeiro_advento
from acervo import ler, adicionar, render, validar_novo

ROOT=Path(__file__).resolve().parents[1]

def normalized(label):
    return label.replace('Dom.', 'Domingo').replace('Aniv. da Igreja','Aniversário da Igreja').replace('Domingo Estação','Domingo da Estação').replace('Domingo Tempo','Domingo do Tempo').replace('Domingo da Páscoa','Domingo de Páscoa')

class CalendarioTests(unittest.TestCase):
    def test_pdf_2026(self):
        expected=json.loads((ROOT/'tests/calendario-2026.json').read_text(encoding='utf-8'))
        actual=domingos(2026)
        self.assertEqual(len(actual),len(expected))
        for a,e in zip(actual,expected):
            self.assertEqual((a['date'],a['season'],normalized(a['celebration'])),(e['date'],e['season'],normalized(e['celebration'])))

    def test_full_years_through_2200(self):
        for year in range(2026,2201):
            rows=domingos(year)
            self.assertIn(len(rows),(52,53))
            dates=[date.fromisoformat(r['date']) for r in rows]
            self.assertEqual(len(set(dates)),len(dates))
            self.assertTrue(all(d.year==year and d.weekday()==6 for d in dates))
            self.assertTrue(all((b-a).days==7 for a,b in zip(dates,dates[1:])))
            self.assertLessEqual(dates[0].day,7)
            self.assertGreaterEqual(dates[-1].day,25)
            self.assertEqual(sum(r['season']=='Advento' for r in rows),4)
            self.assertEqual(sum(r['season']=='Quaresma' for r in rows),6)
            self.assertEqual(sum(r['season']=='Páscoa' for r in rows),7)
            self.assertEqual(sum(r['season']=='Pentecostes' for r in rows),1)
            self.assertEqual(sum(r['season']=='Trindade' for r in rows),1)
            self.assertEqual(sum(r['season']=='Cristo Rei' for r in rows),1)
            self.assertEqual(sum('Aniversário' in r['celebration'] for r in rows),1)
            self.assertEqual(sum('Reforma' in r['celebration'] for r in rows),1)
            for r in rows:
                if r['date'][5:7]=='09':self.assertEqual(r['season'],'Estação da Criação')

    def test_easter_known_dates_and_extremes(self):
        for year,expected in {2026:'2026-04-05',2027:'2027-03-28',2028:'2028-04-16',2029:'2029-04-01',2030:'2030-04-21',2038:'2038-04-25',1818:'1818-03-22'}.items():
            self.assertEqual(pascoa(year).isoformat(),expected)
        with self.assertRaises(ValueError):classificar(date(2026,9,21))
        self.assertEqual(classificar(date(2033,12,25)),('Natal','Domingo de Natal'))
        self.assertEqual(classificar(date(2030,1,6)),('Epifania','Domingo da Epifania'))
        self.assertEqual(domingos(2028)[-1]['liturgicalYear'],2029)

class AcervoTests(unittest.TestCase):
    def setUp(self):
        self.text,self.data,self.fingerprint=ler(ROOT/'index.html')
        self.record={**domingos(2027)[0], 'id':'teste-novo', 'title':'Título <seguro> & original', 'series':'Uma série', 'preacher':'Um preletor', 'url':'https://drive.google.com/file/d/ID-original/view?usp=sharing', 'originalText':'Série de teste', 'publishedAt':'2026-09-22T12:00:00+00:00','legacy':False}

    def test_all_original_records_preserved(self):
        original=json.loads((ROOT/'tests/acervo-original.json').read_text(encoding='utf-8'))['sermons']
        current={r['id']:r for r in self.data['sermons']}
        self.assertEqual(len(original),78)
        for r in original:self.assertEqual(current[r['id']],r)

    def test_append_backup_no_other_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'index.html';path.write_bytes((ROOT/'index.html').read_bytes())
            backup=adicionar(path,self.record,self.fingerprint)
            _,new,_=ler(path)
            self.assertEqual(new['sermons'][:-1],self.data['sermons'])
            self.assertEqual(new['sermons'][-1],self.record)
            self.assertEqual(backup.read_bytes(),(ROOT/'index.html').read_bytes())
            self.assertIn('Título &lt;seguro&gt; &amp; original',path.read_text(encoding='utf-8'))
            with self.assertRaises(ValueError):adicionar(path,self.record,self.fingerprint)

    def test_duplicate_id_and_non_sunday_rejected(self):
        bad={**self.record,'date':'2026-09-21'}
        with self.assertRaises(ValueError):validar_novo(bad)
        for url in ('javascript:alert(1)','http://drive.google.com/file/d/x/view','https://evil.example/file/d/x/view'):
            with self.assertRaises(ValueError):validar_novo({**self.record,'url':url})
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'index.html';path.write_bytes((ROOT/'index.html').read_bytes())
            with self.assertRaises(ValueError):adicionar(path,{**self.record,'id':self.data['sermons'][0]['id']},self.fingerprint)
            self.assertEqual(path.read_bytes(),(ROOT/'index.html').read_bytes())

    def test_json_injection_and_concurrent_change(self):
        data={**self.data,'sermons':self.data['sermons']+[{**self.record,'title':'</script><script>alert(1)</script>'}]}
        rendered=render(self.text,data)
        self.assertNotIn('</script><script>alert(1)</script>',rendered)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'index.html';path.write_text(self.text+'\n<!-- edição externa -->',encoding='utf-8')
            unchanged=path.read_bytes()
            with self.assertRaises(ValueError):adicionar(path,self.record,self.fingerprint)
            self.assertEqual(path.read_bytes(),unchanged)

if __name__=='__main__':unittest.main()
